'use client';

import { useState, useEffect } from 'react';
import { podcastApi, episodeApi, tagApi } from '@/services/api';
import type { Podcast, Tag } from '@/types';

interface UploadFormProps {
  onSuccess?: (episodeId: number) => void;
  onCancel?: () => void;
}

export default function UploadForm({ onSuccess, onCancel }: UploadFormProps) {
  const [podcasts, setPodcasts] = useState<Podcast[]>([]);
  const [presetTags, setPresetTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const [formData, setFormData] = useState({
    podcast_id: '',
    title: '',
    description: '',
    episode_number: '',
    season_number: '',
    publish_date: '',
  });

  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [transcriptFile, setTranscriptFile] = useState<File | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [customTag, setCustomTag] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [podcastsRes, tagsRes] = await Promise.all([
        podcastApi.list(),
        tagApi.getPreset(),
      ]);
      setPodcasts(podcastsRes.data);
      setPresetTags(tagsRes.data);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!audioFile) {
      setError('Please select an audio file');
      return;
    }

    if (!formData.podcast_id) {
      setError('Please select a podcast');
      return;
    }

    setLoading(true);

    try {
      const data = new FormData();
      data.append('podcast_id', formData.podcast_id);
      data.append('title', formData.title);
      if (formData.description) data.append('description', formData.description);
      if (formData.episode_number) data.append('episode_number', formData.episode_number);
      if (formData.season_number) data.append('season_number', formData.season_number);
      if (formData.publish_date) data.append('publish_date', formData.publish_date);

      data.append('audio_file', audioFile);
      if (transcriptFile) {
        data.append('transcript_file', transcriptFile);
      }

      if (selectedTags.length > 0) {
        data.append('tag_names', JSON.stringify(selectedTags));
      }

      const response = await episodeApi.upload(data);

      onSuccess?.(response.data.episode_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload episode');
    } finally {
      setLoading(false);
    }
  };

  const addCustomTag = () => {
    if (customTag && !selectedTags.includes(customTag.toLowerCase())) {
      setSelectedTags([...selectedTags, customTag.toLowerCase()]);
      setCustomTag('');
    }
  };

  const toggleTag = (tagName: string) => {
    if (selectedTags.includes(tagName)) {
      setSelectedTags(selectedTags.filter((t) => t !== tagName));
    } else {
      setSelectedTags([...selectedTags, tagName]);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-6 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload New Episode</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Podcast Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Podcast <span className="text-red-500">*</span>
        </label>
        <select
          value={formData.podcast_id}
          onChange={(e) => setFormData({ ...formData, podcast_id: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          required
        >
          <option value="">Select a podcast</option>
          {podcasts.map((podcast) => (
            <option key={podcast.id} value={podcast.id}>
              {podcast.name}
            </option>
          ))}
        </select>
      </div>

      {/* Title */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Episode Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          required
        />
      </div>

      {/* Description */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Episode & Season Numbers */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Episode Number
          </label>
          <input
            type="number"
            value={formData.episode_number}
            onChange={(e) => setFormData({ ...formData, episode_number: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            min="1"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Season Number
          </label>
          <input
            type="number"
            value={formData.season_number}
            onChange={(e) => setFormData({ ...formData, season_number: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            min="1"
          />
        </div>
      </div>

      {/* Publish Date */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Publish Date
        </label>
        <input
          type="date"
          value={formData.publish_date}
          onChange={(e) => setFormData({ ...formData, publish_date: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Audio File */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Audio File <span className="text-red-500">*</span>
        </label>
        <input
          type="file"
          accept="audio/*"
          onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          required
        />
        {audioFile && (
          <p className="mt-1 text-sm text-gray-600">
            Selected: {audioFile.name} ({(audioFile.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      {/* Transcript File */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Transcript File (Optional)
        </label>
        <input
          type="file"
          accept=".txt,.srt,.vtt"
          onChange={(e) => setTranscriptFile(e.target.files?.[0] || null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        {transcriptFile && (
          <p className="mt-1 text-sm text-gray-600">Selected: {transcriptFile.name}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          Upload a transcript to enable AI summarization and content search
        </p>
      </div>

      {/* Tags */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>

        {/* Preset Tags */}
        <div className="flex flex-wrap gap-2 mb-3">
          {presetTags.map((tag) => (
            <button
              key={tag.id}
              type="button"
              onClick={() => toggleTag(tag.name)}
              className={`px-3 py-1 rounded-full text-sm transition ${
                selectedTags.includes(tag.name)
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {tag.name}
            </button>
          ))}
        </div>

        {/* Custom Tags */}
        <div className="flex space-x-2">
          <input
            type="text"
            value={customTag}
            onChange={(e) => setCustomTag(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomTag())}
            placeholder="Add custom tag"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <button
            type="button"
            onClick={addCustomTag}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
          >
            Add
          </button>
        </div>

        {/* Selected Custom Tags */}
        {selectedTags.filter((t) => !presetTags.find((pt) => pt.name === t)).length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {selectedTags
              .filter((t) => !presetTags.find((pt) => pt.name === t))
              .map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => toggleTag(tag)}
                    className="ml-2 text-blue-500 hover:text-blue-700"
                  >
                    ×
                  </button>
                </span>
              ))}
          </div>
        )}
      </div>

      {/* Buttons */}
      <div className="flex justify-end space-x-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Uploading...' : 'Upload Episode'}
        </button>
      </div>
    </form>
  );
}
