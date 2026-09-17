import type {
  Campaign,
  CampaignCreate,
  DiscoveryResult,
  EmailEvent,
  Lead,
  LeadDetail,
  Page,
  ScoreHistory,
} from './types';

// ─── Config ───────────────────────────────────────────────────────────────────
const BASE_URL = 'http://localhost:8000';

// The token is read from env (set VITE_API_TOKEN in .env.local) with a
// fallback to the backend default so the app works out-of-the-box in dev.
const TOKEN = (import.meta.env.VITE_API_TOKEN as string | undefined) ?? 'dev-local-token';

// ─── Core fetch helper ────────────────────────────────────────────────────────
async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${TOKEN}`,
      ...(init.headers ?? {}),
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(`${res.status}: ${detail}`);
  }

  // 204 / empty body
  const text = await res.text();
  return text ? (JSON.parse(text) as T) : ({} as T);
}

// ─── Campaigns ────────────────────────────────────────────────────────────────
export const api = {
  campaigns: {
    list: (page = 1, limit = 50): Promise<Page<Campaign>> =>
      apiFetch(`/campaigns?page=${page}&limit=${limit}`),
    get: (id: number): Promise<Campaign> =>
      apiFetch(`/campaigns/${id}`),
    create: (payload: CampaignCreate): Promise<Campaign> =>
      apiFetch('/campaigns', { method: 'POST', body: JSON.stringify(payload) }),
  },

  // ─── Discovery ─────────────────────────────────────────────────────────────
  discovery: {
    run: (campaignId: number): Promise<DiscoveryResult> =>
      apiFetch(`/campaigns/${campaignId}/discover`, { method: 'POST' }),
  },

  // ─── Leads ─────────────────────────────────────────────────────────────────
  leads: {
    list: (params: {
      page?: number;
      limit?: number;
      status?: string;
      campaign_id?: number;
      sort?: 'score' | 'created_at';
    }): Promise<Page<Lead>> => {
      const qs = new URLSearchParams();
      if (params.page != null) qs.set('page', String(params.page));
      if (params.limit != null) qs.set('limit', String(params.limit));
      if (params.status) qs.set('status', params.status);
      if (params.campaign_id != null) qs.set('campaign_id', String(params.campaign_id));
      if (params.sort) qs.set('sort', params.sort);
      return apiFetch(`/leads?${qs.toString()}`);
    },
    get: (id: number): Promise<LeadDetail> =>
      apiFetch(`/leads/${id}`),
    scoreHistory: (id: number): Promise<ScoreHistory[]> =>
      apiFetch(`/leads/${id}/score-history`),
  },

  // ─── Events ────────────────────────────────────────────────────────────────
  events: {
    list: (leadId: number): Promise<EmailEvent[]> =>
      apiFetch(`/leads/${leadId}/events`),
    create: (leadId: number, eventType: string): Promise<EmailEvent> =>
      apiFetch(`/leads/${leadId}/events`, {
        method: 'POST',
        body: JSON.stringify({ event_type: eventType }),
      }),
  },

  // ─── Email ─────────────────────────────────────────────────────────────────
  email: {
    send: (leadId: number): Promise<EmailEvent> =>
      apiFetch(`/leads/${leadId}/send`, { method: 'POST' }),
  },
};
