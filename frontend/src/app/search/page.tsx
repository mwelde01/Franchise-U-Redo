'use client';

import { useState } from 'react';
import { searchApi } from '@/services/api';
import type { SearchResult } from '@/types';
import { formatTime } from '@/utils/format';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await searchApi.transcripts({
        query: query.trim(),
        limit: 50,
      });

      setResults(response.data.results);
      setTotalCount(response.data.total_count);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const highlightText = (text: string, query: string) => {
    if (!query) return text;

    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Search Transcripts</h1>
          <p className="text-gray-600">
            Find specific moments in podcast episodes by searching transcript content
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex space-x-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for topics, keywords, or phrases..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <svg
                    className="animate-spin h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
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
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                  <span>Search</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </form>

        {/* Results */}
        {totalCount > 0 && (
          <div className="mb-4 text-sm text-gray-600">
            Found {totalCount} result{totalCount !== 1 ? 's' : ''} for "{query}"
          </div>
        )}

        <div className="space-y-4">
          {results.map((result) => (
            <a
              key={result.segment_id}
              href={`/episodes/${result.episode_id}?t=${result.start_time}`}
              className="block bg-white rounded-lg shadow hover:shadow-lg transition p-6"
            >
              {/* Episode Info */}
              <div className="mb-3">
                <h3 className="text-lg font-bold text-gray-900 mb-1">
                  {result.episode_title}
                </h3>
                <p className="text-sm text-gray-600">{result.podcast_name}</p>
              </div>

              {/* Timestamp */}
              <div className="flex items-center space-x-2 mb-2">
                <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-sm font-mono font-semibold">
                  {formatTime(result.start_time)}
                </span>
                {result.speaker && (
                  <span className="text-sm text-gray-600">
                    Speaker: {result.speaker}
                  </span>
                )}
              </div>

              {/* Transcript Text */}
              <p className="text-gray-800">{highlightText(result.text, query)}</p>

              {/* View Episode Link */}
              <div className="mt-3 text-primary-600 text-sm flex items-center">
                Jump to this moment
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </a>
          ))}
        </div>

        {/* No Results */}
        {!loading && results.length === 0 && query && (
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
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try searching with different keywords or phrases
            </p>
          </div>
        )}

        {/* Empty State */}
        {!loading && !query && results.length === 0 && (
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
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              Search podcast transcripts
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Enter keywords to find specific moments in podcast episodes
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
