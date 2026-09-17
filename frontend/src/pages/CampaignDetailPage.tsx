import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';
import type { Campaign, DiscoveryResult, Lead, LeadStatus } from '../lib/types';
import {
  Spinner,
  Empty,
  ErrorAlert,
  SuccessAlert,
  StatusBadge,
  ScoreBar,
  RelativeTime,
} from '../components/shared';

interface Props {
  campaign: Campaign;
  onBack: () => void;
  onSelectLead: (id: number) => void;
}

// ─── Discovery panel ──────────────────────────────────────────────────────────
function DiscoveryPanel({
  campaign,
  onComplete,
}: {
  campaign: Campaign;
  onComplete: () => void;
}) {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<DiscoveryResult | null>(null);
  const [err, setErr] = useState('');

  const run = async () => {
    setRunning(true);
    setErr('');
    setResult(null);
    try {
      const r = await api.discovery.run(campaign.id);
      setResult(r);
      onComplete();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Discovery failed.');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="card" style={{ marginBottom: 24 }}>
      <div className="section-header">
        <span className="section-title">AI Lead Discovery</span>
        <button className="btn btn-primary btn-sm" onClick={run} disabled={running}>
          {running ? <><Spinner /> Running…</> : '⚡ Run Discovery'}
        </button>
      </div>

      {running && (
        <div className="alert alert-info" style={{ marginTop: 12 }}>
          <Spinner />
          <span>Claude is searching the web and extracting leads. This may take 20–60 seconds…</span>
        </div>
      )}

      {err && <ErrorAlert message={err} />}

      {result && (
        <div className="discovery-result" style={{ marginTop: 12 }}>
          <div className="discovery-stats">
            <div className="discovery-stat">
              <span className="discovery-stat-num" style={{ color: 'var(--green)' }}>
                {result.created_count}
              </span>
              <span className="discovery-stat-label">Leads Created</span>
            </div>
            <div className="discovery-stat">
              <span className="discovery-stat-num" style={{ color: 'var(--text-muted)' }}>
                {result.rejected_count}
              </span>
              <span className="discovery-stat-label">Rejected</span>
            </div>
          </div>

          {result.created_count > 0 && (
            <SuccessAlert
              message={`${result.created_count} new lead${result.created_count !== 1 ? 's' : ''} added to this campaign.`}
            />
          )}

          {result.rejected.length > 0 && (
            <details style={{ marginTop: 8 }}>
              <summary style={{ cursor: 'pointer', fontSize: 12, color: 'var(--text-muted)' }}>
                {result.rejected.length} rejection{result.rejected.length !== 1 ? 's' : ''} (click to expand)
              </summary>
              <ul className="rejection-list">
                {result.rejected.map((r, i) => (
                  <li key={i}>{r.reason}</li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Campaign Detail / Leads Table Page ──────────────────────────────────────
export default function CampaignDetailPage({ campaign, onBack, onSelectLead }: Props) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState<'score' | 'created_at'>('score');
  const [scoreMin, setScoreMin] = useState('');
  const [page, setPage] = useState(1);
  const LIMIT = 20;

  const load = useCallback(async () => {
    setLoading(true);
    setErr('');
    try {
      const result = await api.leads.list({
        page,
        limit: LIMIT,
        campaign_id: campaign.id,
        status: statusFilter || undefined,
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
  }, [campaign.id, statusFilter, sortBy, scoreMin, page]);

  useEffect(() => { void load(); }, [load]);

  const resetFilters = () => {
    setStatusFilter('');
    setSortBy('score');
    setScoreMin('');
    setPage(1);
  };

  const STATUS_OPTIONS: { value: LeadStatus | ''; label: string }[] = [
    { value: '', label: 'All Statuses' },
    { value: 'new', label: 'New' },
    { value: 'sent', label: 'Sent' },
    { value: 'opened', label: 'Opened' },
    { value: 'replied', label: 'Replied' },
    { value: 'unsubscribed', label: 'Unsubscribed' },
  ];

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <div className="page">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <button className="breadcrumb-link" onClick={onBack}>Campaigns</button>
        <span className="breadcrumb-sep">›</span>
        <span className="breadcrumb-current">{campaign.name}</span>
      </div>

      {/* Header */}
      <div className="page-header">
        <div className="page-header-left">
          <h2>{campaign.name}</h2>
          <p>Campaign ID #{campaign.id} · {new Date(campaign.created_at).toLocaleDateString()}</p>
        </div>
      </div>

      {/* ICP summary */}
      {campaign.icp_criteria && (
        <div className="card-sm" style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 8 }}>ICP Criteria</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {campaign.icp_criteria.industry && <span className="icp-tag">🏭 {campaign.icp_criteria.industry}</span>}
            {campaign.icp_criteria.region && <span className="icp-tag">🌍 {campaign.icp_criteria.region}</span>}
            {campaign.icp_criteria.company_size && <span className="icp-tag">👥 {campaign.icp_criteria.company_size}</span>}
            {(campaign.icp_criteria.titles ?? []).map(t => (
              <span key={t} className="icp-tag">🎯 {t}</span>
            ))}
          </div>
        </div>
      )}

      {/* Discovery panel */}
      <DiscoveryPanel campaign={campaign} onComplete={() => { setPage(1); void load(); }} />

      {/* Leads section */}
      <div className="section-header">
        <span className="section-title">Leads</span>
        <span className="section-count">{total}</span>
      </div>

      {/* Filters */}
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

        {(statusFilter || scoreMin || sortBy !== 'score') && (
          <button className="btn btn-ghost btn-sm" onClick={resetFilters}>
            Reset
          </button>
        )}

        <button
          className="btn btn-ghost btn-sm"
          onClick={() => void load()}
          disabled={loading}
          style={{ marginLeft: 'auto' }}
        >
          {loading ? <Spinner /> : '↻ Refresh'}
        </button>
      </div>

      {err && <ErrorAlert message={err} />}

      {loading && leads.length === 0 ? (
        <div className="state-center"><Spinner large /></div>
      ) : leads.length === 0 ? (
        <Empty
          icon="👤"
          message="No leads match your filters"
          hint="Run AI discovery or adjust filters."
        />
      ) : (
        <>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Title</th>
                  <th>Company</th>
                  <th>Email</th>
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
                    <td className="text-muted" style={{ fontSize: 12 }}>
                      #{lead.company_id}
                    </td>
                    <td className="mono">{lead.email}</td>
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

          {/* Pagination */}
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
