import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';
import type { Lead, LeadStatus, Campaign } from '../lib/types';
import {
  Spinner,
  Empty,
  ErrorAlert,
  StatusBadge,
  ScoreBar,
  RelativeTime,
} from '../components/shared';

interface Props {
  onSelectLead: (id: number) => void;
}

export default function AllLeadsPage({ onSelectLead }: Props) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [campaignFilter, setCampaignFilter] = useState('');
  const [sortBy, setSortBy] = useState<'score' | 'created_at'>('score');
  const [scoreMin, setScoreMin] = useState('');
  const [page, setPage] = useState(1);
  const LIMIT = 25;

  // Load campaigns for filter dropdown
  useEffect(() => {
    api.campaigns.list(1, 50)
      .then(p => setCampaigns(p.items))
      .catch(() => {/* silently ignore */});
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setErr('');
    try {
      const result = await api.leads.list({
        page,
        limit: LIMIT,
        status: statusFilter || undefined,
        campaign_id: campaignFilter ? parseInt(campaignFilter, 10) : undefined,
        sort: sortBy,
      });
      let items = result.items;
      if (scoreMin !== '') {
        const min = parseInt(scoreMin, 10);
        if (!isNaN(min)) items = items.filter(l => (l.score?.value ?? 0) >= min);
      }
      setLeads(items);
      setTotal(result.total);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Failed to load leads.');
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, campaignFilter, sortBy, scoreMin]);

  useEffect(() => { void load(); }, [load]);

  const resetFilters = () => {
    setStatusFilter('');
    setCampaignFilter('');
    setSortBy('score');
    setScoreMin('');
    setPage(1);
  };

  const totalPages = Math.ceil(total / LIMIT);

  const STATUS_OPTIONS: { value: LeadStatus | ''; label: string }[] = [
    { value: '', label: 'All Statuses' },
    { value: 'new', label: 'New' },
    { value: 'sent', label: 'Sent' },
    { value: 'opened', label: 'Opened' },
    { value: 'replied', label: 'Replied' },
    { value: 'unsubscribed', label: 'Unsubscribed' },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header-left">
          <h2>All Leads</h2>
          <p>Browse and filter all leads across campaigns, sorted by score.</p>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={() => void load()} disabled={loading}>
          {loading ? <Spinner /> : '↻ Refresh'}
        </button>
      </div>

      <div className="filters">
        <select
          className="filter-select"
          value={statusFilter}
          onChange={e => { setStatusFilter(e.target.value); setPage(1); }}
        >
          {STATUS_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>

        <select
          className="filter-select"
          value={campaignFilter}
          onChange={e => { setCampaignFilter(e.target.value); setPage(1); }}
        >
          <option value="">All Campaigns</option>
          {campaigns.map(c => (
            <option key={c.id} value={String(c.id)}>{c.name}</option>
          ))}
        </select>

        <select
          className="filter-select"
          value={sortBy}
          onChange={e => { setSortBy(e.target.value as 'score' | 'created_at'); setPage(1); }}
        >
          <option value="score">Sort: Score ↓</option>
          <option value="created_at">Sort: Newest</option>
        </select>

        <select
          className="filter-select"
          style={{ minWidth: 110 }}
          value={scoreMin}
          onChange={e => { setScoreMin(e.target.value); setPage(1); }}
        >
          <option value="">Min Score: Any</option>
          <option value="70">≥ 70 (Hot)</option>
          <option value="40">≥ 40 (Warm)</option>
          <option value="20">≥ 20</option>
        </select>

        {(statusFilter || campaignFilter || scoreMin || sortBy !== 'score') && (
          <button className="btn btn-ghost btn-sm" onClick={resetFilters}>Reset</button>
        )}
      </div>

      {err && <ErrorAlert message={err} />}

      <div style={{ marginBottom: 10, fontSize: 12, color: 'var(--text-dim)' }}>
        {total} lead{total !== 1 ? 's' : ''} total
      </div>

      {loading && leads.length === 0 ? (
        <div className="state-center"><Spinner large /></div>
      ) : leads.length === 0 ? (
        <Empty icon="👤" message="No leads match your filters" hint="Run discovery in a campaign or adjust filters." />
      ) : (
        <>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Title</th>
                  <th>Email</th>
                  <th>Campaign</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Added</th>
                </tr>
              </thead>
              <tbody>
                {leads.map(lead => (
                  <tr key={lead.id} onClick={() => onSelectLead(lead.id)}>
                    <td style={{ fontWeight: 600 }}>
                      {lead.first_name} {lead.last_name ?? ''}
                    </td>
                    <td className="text-muted">{lead.title ?? '—'}</td>
                    <td className="mono">{lead.email}</td>
                    <td className="text-muted">
                      {campaigns.find(c => c.id === lead.campaign_id)?.name ?? `#${lead.campaign_id}`}
                    </td>
                    <td><StatusBadge status={lead.status as LeadStatus} /></td>
                    <td style={{ minWidth: 120 }}>
                      <ScoreBar value={lead.score?.value} />
                    </td>
                    <td className="text-dim"><RelativeTime iso={lead.created_at} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 12, alignItems: 'center' }}>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-ghost btn-sm"
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
              >← Prev</button>
              <button
                className="btn btn-ghost btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
              >Next →</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
