// ─── Pagination ───────────────────────────────────────────────────────────────
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// ─── Company ─────────────────────────────────────────────────────────────────
export interface Company {
  id: number;
  name: string;
  domain: string | null;
  industry: string | null;
  region: string | null;
  size: string | null;
  created_at: string;
  raw_data: Record<string, string> | null;
}

// ─── Campaign ─────────────────────────────────────────────────────────────────
export interface IcpCriteria {
  titles?: string[];
  industry?: string;
  region?: string;
  company_size?: string;
}

export interface Campaign {
  id: number;
  name: string;
  icp_criteria: IcpCriteria | null;
  created_at: string;
}

export interface CampaignCreate {
  name: string;
  icp_criteria?: IcpCriteria | null;
}

// ─── Score ────────────────────────────────────────────────────────────────────
export interface Score {
  value: number;
  fit_component: number;
  engagement_component: number;
  updated_at: string;
}

export interface ScoreHistory {
  id: number;
  old_score: number | null;
  new_score: number;
  reason: string;
  created_at: string;
}

// ─── Leads ────────────────────────────────────────────────────────────────────
export type LeadStatus = 'new' | 'sent' | 'opened' | 'replied' | 'unsubscribed';

export interface Lead {
  id: number;
  company_id: number;
  campaign_id: number;
  first_name: string;
  last_name: string | null;
  title: string | null;
  email: string;
  source_url: string;
  status: LeadStatus;
  created_at: string;
  score: Score | null;
  raw_data: Record<string, string> | null;
}

export interface LeadDetail extends Lead {
  company: Company;
  campaign: Campaign;
}

// ─── Events ───────────────────────────────────────────────────────────────────
export type EventType = 'sent' | 'delivered' | 'opened' | 'replied' | 'unsubscribed';

export interface EmailEvent {
  id: number;
  lead_id: number;
  event_type: EventType;
  occurred_at: string;
  event_metadata: Record<string, unknown> | null;
}

// ─── Discovery ────────────────────────────────────────────────────────────────
export interface DiscoveryResult {
  created_count: number;
  rejected_count: number;
  created_lead_ids: number[];
  rejected: { reason: string }[];
}
