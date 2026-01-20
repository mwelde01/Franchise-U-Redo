'use client';

import { useState } from 'react';
import type { TranscriptSegment } from '@/types';
import { formatTime } from '@/utils/format';

interface TranscriptViewProps {
  segments: TranscriptSegment[];
  currentTime: number;
  onSegmentClick: (time: number) => void;
  searchQuery?: string;
}

export default function TranscriptView({
  segments,
  currentTime,
  onSegmentClick,
  searchQuery = '',
}: TranscriptViewProps) {
  const [filterSpeaker, setFilterSpeaker] = useState<string>('');

  // Get unique speakers
  const speakers = Array.from(
    new Set(segments.map((s) => s.speaker).filter(Boolean))
  );

  // Filter segments
  const filteredSegments = segments.filter((segment) => {
    if (filterSpeaker && segment.speaker !== filterSpeaker) {
      return false;
    }
    if (searchQuery && !segment.text.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  const highlightText = (text: string, query: string) => {
    if (!query) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
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
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-900">Transcript</h3>

        {/* Speaker Filter */}
        {speakers.length > 0 && (
          <select
            value={filterSpeaker}
            onChange={(e) => setFilterSpeaker(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">All Speakers</option>
            {speakers.map((speaker) => (
              <option key={speaker} value={speaker}>
                {speaker}
              </option>
            ))}
          </select>
        )}
      </div>

      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {filteredSegments.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No transcript segments found
            {searchQuery && ' matching your search'}
            {filterSpeaker && ` for speaker "${filterSpeaker}"`}
          </p>
        ) : (
          filteredSegments.map((segment) => {
            const isActive =
              currentTime >= segment.start_time && currentTime <= segment.end_time;

            return (
              <div
                key={segment.id}
                onClick={() => onSegmentClick(segment.start_time)}
                className={`p-3 rounded-lg cursor-pointer transition ${
                  isActive
                    ? 'bg-primary-100 border-2 border-primary-500'
                    : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSegmentClick(segment.start_time);
                    }}
                    className="flex-shrink-0 text-primary-600 hover:text-primary-700 font-mono text-sm font-semibold"
                  >
                    {formatTime(segment.start_time)}
                  </button>

                  <div className="flex-1">
                    {segment.speaker && (
                      <span className="font-semibold text-gray-700">
                        {segment.speaker}:{' '}
                      </span>
                    )}
                    <span className="text-gray-800">
                      {highlightText(segment.text, searchQuery)}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {filteredSegments.length > 0 && (
        <div className="mt-4 text-sm text-gray-500 text-center">
          Showing {filteredSegments.length} of {segments.length} segments
        </div>
      )}
    </div>
  );
}
