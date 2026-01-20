"""Audio Service for handling audio file operations"""

import os
import shutil
from typing import Tuple, Optional
from pathlib import Path
import uuid
from pydub import AudioSegment
from pydub.utils import mediainfo
from fastapi import UploadFile
from app.config import settings


class AudioService:
    """Service for audio file operations"""

    SUPPORTED_FORMATS = ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac', 'wma']

    def __init__(self):
        self.storage_path = Path(settings.AUDIO_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_audio_file(
        self,
        file: UploadFile,
        podcast_id: int,
        episode_id: int
    ) -> Tuple[str, int, float, str]:
        """
        Save uploaded audio file and extract metadata

        Args:
            file: Uploaded file
            podcast_id: ID of the podcast
            episode_id: ID of the episode

        Returns:
            Tuple of (file_path, file_size, duration, format)
        """
        # Validate file
        file_ext = self._get_file_extension(file.filename)
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {file_ext}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Generate unique filename
        unique_filename = f"{podcast_id}_{episode_id}_{uuid.uuid4()}.{file_ext}"
        file_path = self.storage_path / unique_filename

        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            await file.close()

        # Get file size
        file_size = os.path.getsize(file_path)

        # Check file size limit
        max_size_bytes = settings.MAX_UPLOAD_SIZE * 1024 * 1024
        if file_size > max_size_bytes:
            os.remove(file_path)
            raise ValueError(
                f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds "
                f"maximum allowed size ({settings.MAX_UPLOAD_SIZE}MB)"
            )

        # Extract audio metadata
        try:
            duration = self._get_audio_duration(file_path)
        except Exception as e:
            print(f"Warning: Could not extract audio duration: {e}")
            duration = 0.0

        return str(file_path), file_size, duration, file_ext

    def get_audio_info(self, file_path: str) -> dict:
        """
        Get detailed information about an audio file

        Args:
            file_path: Path to audio file

        Returns:
            Dictionary with audio metadata
        """
        try:
            info = mediainfo(file_path)
            return {
                'duration': float(info.get('duration', 0)),
                'bit_rate': info.get('bit_rate'),
                'sample_rate': info.get('sample_rate'),
                'channels': info.get('channels'),
                'format': info.get('format_name'),
                'codec': info.get('codec_name'),
            }
        except Exception as e:
            print(f"Error getting audio info: {e}")
            return {}

    def delete_audio_file(self, file_path: str) -> bool:
        """
        Delete an audio file

        Args:
            file_path: Path to the file to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting audio file: {e}")
            return False

    def get_audio_segment(
        self,
        file_path: str,
        start_time: float,
        end_time: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Extract a segment of audio file

        Args:
            file_path: Source audio file path
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Optional output path, generates temp file if not provided

        Returns:
            Path to the extracted segment
        """
        try:
            audio = AudioSegment.from_file(file_path)
            segment = audio[start_time * 1000:end_time * 1000]  # pydub uses milliseconds

            if output_path is None:
                output_path = os.path.join(
                    self.storage_path,
                    'temp',
                    f"segment_{uuid.uuid4()}.mp3"
                )

            segment.export(output_path, format="mp3")
            return output_path

        except Exception as e:
            raise Exception(f"Failed to extract audio segment: {str(e)}")

    def convert_audio_format(
        self,
        input_path: str,
        output_format: str = 'mp3',
        output_path: Optional[str] = None
    ) -> str:
        """
        Convert audio file to different format

        Args:
            input_path: Source audio file
            output_format: Target format (mp3, wav, etc.)
            output_path: Optional output path

        Returns:
            Path to converted file
        """
        if output_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported output format: {output_format}")

        try:
            audio = AudioSegment.from_file(input_path)

            if output_path is None:
                base_name = Path(input_path).stem
                output_path = os.path.join(
                    self.storage_path,
                    f"{base_name}_converted.{output_format}"
                )

            audio.export(output_path, format=output_format)
            return output_path

        except Exception as e:
            raise Exception(f"Failed to convert audio: {str(e)}")

    def _get_audio_duration(self, file_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            # Fallback to mediainfo
            try:
                info = mediainfo(file_path)
                return float(info.get('duration', 0))
            except:
                raise Exception(f"Could not determine audio duration: {e}")

    @staticmethod
    def _get_file_extension(filename: str) -> str:
        """Extract file extension from filename"""
        if not filename:
            raise ValueError("Filename is empty")
        ext = filename.split('.')[-1].lower()
        return ext

    def get_waveform_data(
        self,
        file_path: str,
        samples: int = 1000
    ) -> list:
        """
        Generate waveform data for visualization

        Args:
            file_path: Audio file path
            samples: Number of sample points to return

        Returns:
            List of amplitude values
        """
        try:
            audio = AudioSegment.from_file(file_path)

            # Get raw audio data
            raw_data = audio.raw_data
            sample_width = audio.sample_width
            frame_rate = audio.frame_rate

            # Calculate sampling interval
            total_samples = len(raw_data) // sample_width
            interval = max(1, total_samples // samples)

            # Extract sample points
            waveform = []
            for i in range(0, len(raw_data), interval * sample_width):
                if len(waveform) >= samples:
                    break
                # Get sample value (simplified, just taking first channel)
                if i + sample_width <= len(raw_data):
                    sample = int.from_bytes(
                        raw_data[i:i + sample_width],
                        byteorder='little',
                        signed=True
                    )
                    # Normalize to 0-1 range
                    max_val = 2 ** (sample_width * 8 - 1)
                    normalized = abs(sample) / max_val
                    waveform.append(normalized)

            return waveform

        except Exception as e:
            print(f"Error generating waveform: {e}")
            return []

    def validate_audio_file(self, file_path: str) -> bool:
        """
        Validate that a file is a valid audio file

        Args:
            file_path: Path to file

        Returns:
            True if valid audio file, False otherwise
        """
        try:
            AudioSegment.from_file(file_path)
            return True
        except Exception:
            return False
