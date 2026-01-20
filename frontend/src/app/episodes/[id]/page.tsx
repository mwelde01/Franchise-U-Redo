'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { episodeApi } from '@/services/api';
import type { Episode } from '@/types';
import AudioPlayer from '@/components/AudioPlayer';
import TranscriptView from '@/components/TranscriptView';
import { formatDate, formatTime } from '@/utils/format';

export default function EpisodeDetailPage() {
  const params = useParams();
  const episodeId = parseInt(params.id as string);

  const [episode, setEpisode] = useState<Episode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [currentTime, setCurrentTime] = useState(0);
  const [audioPlayerRef, setAudioPlayerRef] = useState<any>(null);

  useEffect(() => {
    loadEpisode();
  }, [episodeId]);

  const loadEpisode = async () => {
    try {
      const response = await episodeApi.get(episodeId, true);
      setEpisode(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load episode');
    } finally {
      setLoading(false);
    }
  };

  const handleSegmentClick = (time: number) => {
    // This would need to be implemented in AudioPlayer to expose a method
    // For now, we'll just update the state
    setCurrentTime(time);
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        </div>
      </div>
    );
  }

  if (error || !episode) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900">Error Loading Episode</h3>
          <p className="mt-2 text-sm text-gray-600">{error || 'Episode not found'}</p>
          <a href="/" className="mt-4 inline-block text-primary-600 hover:text-primary-700">
            Back to Episodes
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back Button */}
      <a
        href="/"
        className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
      >
        <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Back to Episodes
      </a>

      {/* Episode Header */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{episode.title}</h1>
            {episode.podcast_name && (
              <p className="text-lg text-gray-600 mb-2">{episode.podcast_name}</p>
            )}
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              {episode.duration && <span>{formatTime(episode.duration)}</span>}
              {episode.publish_date && <span>{formatDate(episode.publish_date)}</span>}
              {episode.episode_number && <span>Episode {episode.episode_number}</span>}
              {episode.season_number && <span>Season {episode.season_number}</span>}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {episode.is_processed ? (
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                Processed
              </span>
            ) : (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">
                Processing...
              </span>
            )}
          </div>
        </div>

        {/* Tags */}
        {episode.tags && episode.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {episode.tags.map((tag) => (
              <span
                key={tag.id}
                className={`px-3 py-1 rounded-full text-sm ${
                  tag.is_preset
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}

        {/* Description */}
        {episode.description && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
            <p className="text-gray-700">{episode.description}</p>
          </div>
        )}

        {/* AI Summary */}
        {episode.summary && (
          <div className="border-t border-gray-200 pt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">AI Summary</h3>
            <p className="text-gray-700 whitespace-pre-line">{episode.summary}</p>
          </div>
        )}
      </div>

      {/* Audio Player */}
      <div className="mb-6">
        <AudioPlayer
          episode={episode}
          onTimeUpdate={setCurrentTime}
        />
      </div>

      {/* Transcript */}
      {episode.transcript_segments && episode.transcript_segments.length > 0 && (
        <TranscriptView
          segments={episode.transcript_segments}
          currentTime={currentTime}
          onSegmentClick={handleSegmentClick}
        />
      )}

      {/* No Transcript Message */}
      {(!episode.transcript_segments || episode.transcript_segments.length === 0) && (
        <div className="bg-white rounded-lg shadow-lg p-6 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No Transcript Available</h3>
          <p className="mt-1 text-sm text-gray-500">
            Upload a transcript to enable AI summarization and content search.
          </p>
        </div>
      )}
    </div>
  );
}
