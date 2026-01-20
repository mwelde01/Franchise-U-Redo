export interface Podcast {
  id: number;
  name: string;
  description?: string;
  author?: string;
  website?: string;
  image_url?: string;
  created_at: string;
  updated_at?: string;
  episode_count?: number;
}

export interface Tag {
  id: number;
  name: string;
  description?: string;
  is_preset: boolean;
  usage_count: number;
  created_at: string;
}

export interface TranscriptSegment {
  id: number;
  episode_id: number;
  start_time: number;
  end_time: number;
  text: string;
  speaker?: string;
  sequence_number: number;
  confidence?: number;
  created_at: string;
}

export interface Episode {
  id: number;
  podcast_id: number;
  title: string;
  description?: string;
  audio_file_path: string;
  audio_file_size?: number;
  duration?: number;
  audio_format?: string;
  episode_number?: number;
  season_number?: number;
  publish_date?: string;
  summary?: string;
  summary_generated_at?: string;
  is_processed: boolean;
  processing_error?: string;
  created_at: string;
  updated_at?: string;
  tags: Tag[];
  podcast_name?: string;
  transcript_segments?: TranscriptSegment[];
}

export interface SearchResult {
  episode_id: number;
  episode_title: string;
  podcast_name: string;
  segment_id: number;
  start_time: number;
  end_time: number;
  text: string;
  speaker?: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total_count: number;
}

export interface ThemeDiscovery {
  discovered_tags: string[];
  common_themes: Array<{
    theme: string;
    frequency: string;
    description: string;
  }>;
  tag_relationships: Record<string, string[]>;
}
