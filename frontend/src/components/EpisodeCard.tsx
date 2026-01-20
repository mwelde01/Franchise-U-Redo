'use client';

import Link from 'next/link';
import type { Episode } from '@/types';
import { formatTime, formatRelativeTime, truncate } from '@/utils/format';

interface EpisodeCardProps {
  episode: Episode;
}

export default function EpisodeCard({ episode }: EpisodeCardProps) {
  return (
    <Link href={`/episodes/${episode.id}`}>
      <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 h-full cursor-pointer">
        {/* Header */}
        <div className="mb-3">
          <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-2">
            {episode.title}
          </h3>
          {episode.podcast_name && (
            <p className="text-sm text-gray-600">{episode.podcast_name}</p>
          )}
        </div>

        {/* Episode Info */}
        <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
          {episode.duration && (
            <span className="flex items-center">
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {formatTime(episode.duration)}
            </span>
          )}
          {episode.created_at && (
            <span>{formatRelativeTime(episode.created_at)}</span>
          )}
          {episode.episode_number && (
            <span>Episode {episode.episode_number}</span>
          )}
        </div>

        {/* Description/Summary */}
        {(episode.summary || episode.description) && (
          <p className="text-sm text-gray-700 mb-4 line-clamp-3">
            {truncate(episode.summary || episode.description || '', 150)}
          </p>
        )}

        {/* Tags */}
        {episode.tags && episode.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {episode.tags.slice(0, 5).map((tag) => (
              <span
                key={tag.id}
                className={`px-2 py-1 rounded-full text-xs ${
                  tag.is_preset
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {tag.name}
              </span>
            ))}
            {episode.tags.length > 5 && (
              <span className="px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-700">
                +{episode.tags.length - 5}
              </span>
            )}
          </div>
        )}

        {/* Status */}
        <div className="flex items-center justify-between mt-auto pt-3 border-t border-gray-200">
          <div className="flex items-center space-x-2">
            {episode.is_processed ? (
              <span className="flex items-center text-xs text-green-600">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                Processed
              </span>
            ) : (
              <span className="flex items-center text-xs text-yellow-600">
                <svg className="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Processing
              </span>
            )}
          </div>

          {episode.audio_format && (
            <span className="text-xs text-gray-500 uppercase">
              {episode.audio_format}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
