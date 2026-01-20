import axios from 'axios';
import type { Podcast, Episode, Tag, SearchResponse, ThemeDiscovery } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Podcasts
export const podcastApi = {
  list: () => api.get<Podcast[]>('/podcasts'),
  get: (id: number) => api.get<Podcast>(`/podcasts/${id}`),
  create: (data: Partial<Podcast>) => api.post<Podcast>('/podcasts', data),
  update: (id: number, data: Partial<Podcast>) => api.put<Podcast>(`/podcasts/${id}`, data),
  delete: (id: number) => api.delete(`/podcasts/${id}`),
  getEpisodes: (id: number) => api.get<Episode[]>(`/podcasts/${id}/episodes`),
};

// Episodes
export const episodeApi = {
  list: (params?: { podcast_id?: number; tag_id?: number; skip?: number; limit?: number }) =>
    api.get<Episode[]>('/episodes', { params }),
  get: (id: number, includeTranscript: boolean = true) =>
    api.get<Episode>(`/episodes/${id}`, { params: { include_transcript: includeTranscript } }),
  upload: (formData: FormData) =>
    api.post<{ episode_id: number; message: string }>('/episodes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  update: (id: number, data: Partial<Episode>) =>
    api.put<Episode>(`/episodes/${id}`, data),
  delete: (id: number) => api.delete(`/episodes/${id}`),
  streamAudio: (id: number) => `${API_URL}/episodes/${id}/audio`,
  uploadTranscript: (id: number, segments: any[]) =>
    api.post(`/episodes/${id}/transcript`, { segments }),
  regenerateSummary: (id: number) =>
    api.post(`/episodes/${id}/regenerate-summary`),
};

// Tags
export const tagApi = {
  list: (params?: { preset_only?: boolean; sort_by?: string }) =>
    api.get<Tag[]>('/tags', { params }),
  get: (id: number) => api.get<Tag>(`/tags/${id}`),
  create: (data: { name: string; description?: string; is_preset?: boolean }) =>
    api.post<Tag>('/tags', data),
  update: (id: number, data: Partial<Tag>) =>
    api.put<Tag>(`/tags/${id}`, data),
  delete: (id: number, force: boolean = false) =>
    api.delete(`/tags/${id}`, { params: { force } }),
  getEpisodes: (id: number) => api.get<Episode[]>(`/tags/${id}/episodes`),
  getPreset: () => api.get<Tag[]>('/tags/preset'),
  getPopular: (limit: number = 20) =>
    api.get<Tag[]>('/tags/popular', { params: { limit } }),
  initializePresets: () => api.post('/tags/initialize-presets'),
};

// Search
export const searchApi = {
  transcripts: (data: {
    query: string;
    podcast_ids?: number[];
    tag_ids?: number[];
    limit?: number;
  }) => api.post<SearchResponse>('/search/transcripts', data),
  keywords: (keywords: string, episode_id?: number, limit: number = 50) =>
    api.get<SearchResponse>('/search/keywords', {
      params: { keywords, episode_id, limit },
    }),
  episodes: (query: string, podcast_id?: number, skip: number = 0, limit: number = 50) =>
    api.get<{ results: Episode[]; total_count: number }>('/search/episodes', {
      params: { query, podcast_id, skip, limit },
    }),
  segmentContext: (segmentId: number, contextSeconds: number = 30) =>
    api.get(`/search/segment/${segmentId}/context`, {
      params: { context_seconds: contextSeconds },
    }),
  discoverThemes: (podcast_ids?: number[], limit: number = 20) =>
    api.post<ThemeDiscovery>('/search/discover-themes', null, {
      params: { podcast_ids, limit },
    }),
  relatedEpisodes: (episodeId: number, limit: number = 10) =>
    api.get(`/search/related-episodes/${episodeId}`, { params: { limit } }),
};

// Health & Stats
export const systemApi = {
  health: () => api.get('/health'),
  stats: () => api.get<{
    podcasts: number;
    episodes: number;
    tags: number;
    transcript_segments: number;
    processed_episodes: number;
  }>('/stats'),
};

export default api;
