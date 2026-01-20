'use client';

import { useState, useEffect } from 'react';
import { episodeApi, tagApi } from '@/services/api';
import type { Episode, Tag } from '@/types';
import EpisodeCard from '@/components/EpisodeCard';

export default function HomePage() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTag, setSelectedTag] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, [selectedTag]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [episodesRes, tagsRes] = await Promise.all([
        episodeApi.list({ tag_id: selectedTag || undefined, limit: 50 }),
        tagApi.getPopular(30),
      ]);
      setEpisodes(episodesRes.data);
      setTags(tagsRes.data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Podcast Episodes</h1>
        <p className="text-gray-600">
          Browse and listen to podcast episodes with AI-powered summaries and transcripts
        </p>
      </div>

      {/* Tag Filter */}
      {tags.length > 0 && (
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Filter by Tag:</h2>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedTag(null)}
              className={`px-4 py-2 rounded-full text-sm transition ${
                selectedTag === null
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All Episodes
            </button>
            {tags.map((tag) => (
              <button
                key={tag.id}
                onClick={() => setSelectedTag(tag.id)}
                className={`px-4 py-2 rounded-full text-sm transition ${
                  selectedTag === tag.id
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {tag.name} ({tag.usage_count})
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Episodes Grid */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        </div>
      ) : episodes.length === 0 ? (
        <div className="text-center py-12">
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
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No episodes found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {selectedTag
              ? 'Try selecting a different tag or upload a new episode.'
              : 'Get started by uploading your first episode.'}
          </p>
          <div className="mt-6">
            <a
              href="/upload"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              Upload Episode
            </a>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {episodes.map((episode) => (
            <EpisodeCard key={episode.id} episode={episode} />
          ))}
        </div>
      )}
    </div>
  );
}
