import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';
import type { LeadDetail, EmailEvent, ScoreHistory, LeadStatus, EventType, ReplyClassification } from '../lib/types';
import {
  Spinner,
  Empty,
  ErrorAlert,
  SuccessAlert,
  StatusBadge,
  EventBadge,
  ScoreWidget,
  AbsTime,
} from '../components/shared';

interface Props {
  leadId: number;
  onBack: () => void;
  campaignName?: string;
  onBackToCampaign: () => void;
}

// ─── Manual event form ────────────────────────────────────────────────────────
const EVENT_TYPES = ['delivered', 'opened', 'replied', 'unsubscribed'] as const;

function SimulateEventPanel({
  leadId,
  onDone,
}: {
  leadId: number;
  onDone: () => void;
}) {
  const [type, setType] = useState<string>('opened');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');
  const [ok, setOk] = useState('');

  const submit = async () => {
    setLoading(true);
    setErr('');
    setOk('');
    try {
      await api.events.create(leadId, type);
      setOk(`Event "${type}" recorded.`);
      onDone();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Failed to record event.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end', flexWrap: 'wrap' }}>
      <div className="form-group" style={{ marginBottom: 0 }}>
        <label className="form-label">Simulate Event</label>
        <select
          className="form-select"
          value={type}
          onChange={e => setType(e.target.value)}
          style={{ width: 160 }}
        >
          {EVENT_TYPES.map(t => (
            <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
          ))}
        </select>
      </div>
      <button className="btn btn-ghost btn-sm" onClick={submit} disabled={loading}>
        {loading ? <Spinner /> : 'Record'}
      </button>
      {err && <span style={{ fontSize: 12, color: 'var(--red)' }}>{err}</span>}
      {ok && <span style={{ fontSize: 12, color: 'var(--green)' }}>{ok}</span>}
    </div>
  );
}

// ─── Classify reply panel ─────────────────────────────────────────────────────
function labelColor(label: string): string {
  const map: Record<string, string> = {
    'Interested': '#29d87a',
    'Not Interested': '#f0524f',
    'Needs Follow-up': '#f5c842',
    'Unsubscribe Request': '#a06af8',
    'Other': '#555d70',
  };
  return map[label] ?? '#555d70';
}

function ClassifyReplyPanel({ leadId, onDone }: { leadId: number; onDone: () => void }) {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');
  const [result, setResult] = useState<ReplyClassification | null>(null);

  const submit = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setErr('');
    setResult(null);
    try {
      const r = await api.replies.classify(leadId, text);
      setResult(r);
      onDone();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Failed to classify reply.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <div className="section-header">
        <span className="section-title">Classify Reply</span>
      </div>
      <div className="form-group" style={{ marginBottom: 8 }}>
        <textarea
          className="form-textarea"
          placeholder="Paste the inbound reply text here…"
          value={text}
          onChange={e => setText(e.target.value)}
          style={{ width: '100%' }}
        />
      </div>
      <button className="btn btn-primary btn-sm" onClick={() => void submit()} disabled={loading || !text.trim()}>
        {loading ? <><Spinner /> Classifying…</> : 'Classify Reply'}
      </button>

      {err && <div style={{ marginTop: 10 }}><ErrorAlert message={err} /></div>}

      {result && (
        <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span
              className="badge"
              style={{ background: `${labelColor(result.label)}22`, color: labelColor(result.label) }}
            >
              {result.label}
            </span>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Confidence: {(result.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{result.reasoning}</div>
          <div className="detail-field" style={{ marginTop: 4 }}>
            <div className="detail-field-label">Draft Response</div>
            <div className="detail-field-value" style={{ whiteSpace: 'pre-wrap' }}>
              {result.draft_response}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Lead Detail Page ─────────────────────────────────────────────────────────
export default function LeadDetailPage({ leadId, onBack, campaignName, onBackToCampaign }: Props) {
  const [lead, setLead] = useState<LeadDetail | null>(null);
  const [events, setEvents] = useState<EmailEvent[]>([]);
  const [history, setHistory] = useState<ScoreHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');

  const [sending, setSending] = useState(false);
  const [sendResult, setSendResult] = useState<{ ok: boolean; msg: string } | null>(null);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setErr('');
    try {
      const [l, evts, hist] = await Promise.all([
        api.leads.get(leadId),
        api.events.list(leadId),
        api.leads.scoreHistory(leadId),
      ]);
      setLead(l);
      setEvents(evts);
      setHistory(hist);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Failed to load lead.');
    } finally {
      setLoading(false);
    }
  }, [leadId]);

    useEffect(() => {
      const timer = window.setTimeout(() => { void loadAll(); }, 0);
      return () => window.clearTimeout(timer);
    }, [loadAll]);

    const refreshSilently = useCallback(async () => {
    try {
      const [l, evts, hist] = await Promise.all([
        api.leads.get(leadId),
        api.events.list(leadId),
        api.leads.scoreHistory(leadId),
      ]);
      setLead(l);
      setEvents(evts);
      setHistory(hist);
    } catch {
      // ignore - the classify result is already showing; don't disrupt it
    }
  }, [leadId]);


  const handleSend = async () => {
    setSending(true);
    setSendResult(null);
    try {
      await api.email.send(leadId);
      setSendResult({ ok: true, msg: 'Email sent successfully.' });
      void loadAll();
    } catch (e: unknown) {
      setSendResult({
        ok: false,
        msg: e instanceof Error ? e.message : 'Failed to send email.',
      });
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="state-center" style={{ paddingTop: 80 }}><Spinner large /></div>
      </div>
    );
  }

  if (err || !lead) {
    return (
      <div className="page">
        <ErrorAlert message={err || 'Lead not found.'} />
        <button className="btn btn-ghost btn-sm" onClick={onBack}>← Back</button>
      </div>
    );
  }

  const score = lead.score;
  const rawData = lead.raw_data ?? {};
  const companyRaw = lead.company?.raw_data ?? {};

  return (
    <div className="page">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <button className="breadcrumb-link" onClick={onBack}>Campaigns</button>
        <span className="breadcrumb-sep">›</span>
        {campaignName && (
          <>
            <button className="breadcrumb-link" onClick={onBackToCampaign}>{campaignName}</button>
            <span className="breadcrumb-sep">›</span>
          </>
        )}
        <span className="breadcrumb-current">
          {lead.first_name} {lead.last_name ?? ''}
        </span>
      </div>

      {/* Header */}
      <div className="page-header">
        <div className="page-header-left">
          <h2>{lead.first_name} {lead.last_name ?? ''}</h2>
          <p style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {lead.title ?? '—'} · <span className="mono">{lead.email}</span>
            &nbsp;·&nbsp;<StatusBadge status={lead.status as LeadStatus} />
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
          <button
            className="btn btn-success"
            onClick={handleSend}
            disabled={sending || lead.status === 'unsubscribed'}
            title={lead.status === 'unsubscribed' ? 'Lead has unsubscribed' : 'Send outreach email'}
          >
            {sending ? <><Spinner /> Sending…</> : '✉ Send Email'}
          </button>
        </div>
      </div>

      {/* Send result */}
      {sendResult && (
        sendResult.ok
          ? <SuccessAlert message={sendResult.msg} />
          : <ErrorAlert message={sendResult.msg} />
      )}

      {/* Score */}
      {score ? (
        <ScoreWidget
          value={score.value}
          fit={score.fit_component}
          engagement={score.engagement_component}
        />
      ) : (
        <div className="alert alert-info" style={{ marginBottom: 20 }}>No score computed yet.</div>
      )}

      {/* Lead details */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="section-header">
          <span className="section-title">Lead Details</span>
        </div>
        <div className="detail-grid">
          <div className="detail-field">
            <div className="detail-field-label">Email</div>
            <div className="detail-field-value mono">{lead.email}</div>
          </div>
          <div className="detail-field">
            <div className="detail-field-label">Status</div>
            <div className="detail-field-value"><StatusBadge status={lead.status as LeadStatus} /></div>
          </div>
          <div className="detail-field">
            <div className="detail-field-label">Title</div>
            <div className="detail-field-value">{lead.title ?? '—'}</div>
          </div>
          <div className="detail-field">
            <div className="detail-field-label">Campaign</div>
            <div className="detail-field-value">{lead.campaign?.name ?? `#${lead.campaign_id}`}</div>
          </div>
          <div className="detail-field">
            <div className="detail-field-label">Source</div>
            <div className="detail-field-value">
              <a href={lead.source_url} target="_blank" rel="noreferrer" style={{ fontSize: 12 }}>
                {lead.source_url.replace(/^https?:\/\//, '').slice(0, 50)}
              </a>
            </div>
          </div>
          <div className="detail-field">
            <div className="detail-field-label">Added</div>
            <div className="detail-field-value"><AbsTime iso={lead.created_at} /></div>
          </div>
        </div>

        {/* Company */}
        <div style={{ marginTop: 6 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 8 }}>Company</div>
          <div className="detail-grid">
            <div className="detail-field">
              <div className="detail-field-label">Name</div>
              <div className="detail-field-value">{lead.company?.name ?? '—'}</div>
            </div>
            {lead.company?.domain && (
              <div className="detail-field">
                <div className="detail-field-label">Domain</div>
                <div className="detail-field-value mono">{lead.company.domain}</div>
              </div>
            )}
            {lead.company?.industry && (
              <div className="detail-field">
                <div className="detail-field-label">Industry</div>
                <div className="detail-field-value">{lead.company.industry}</div>
              </div>
            )}
            {lead.company?.region && (
              <div className="detail-field">
                <div className="detail-field-label">Region</div>
                <div className="detail-field-value">{lead.company.region}</div>
              </div>
            )}
            {lead.company?.size && (
              <div className="detail-field">
                <div className="detail-field-label">Size</div>
                <div className="detail-field-value">{lead.company.size}</div>
              </div>
            )}
          </div>
        </div>

        {/* Research signals */}
        {(rawData.observed_signal_sentence || companyRaw.pain_point_category) && (
          <div style={{ marginTop: 10 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 8 }}>Research Signals</div>
            <div className="detail-grid">
              {rawData.observed_signal_sentence && (
                <div className="detail-field" style={{ gridColumn: '1 / -1' }}>
                  <div className="detail-field-label">Observed Signal</div>
                  <div className="detail-field-value">{rawData.observed_signal_sentence}</div>
                </div>
              )}
              {companyRaw.pain_point_category && (
                <div className="detail-field">
                  <div className="detail-field-label">Pain Point</div>
                  <div className="detail-field-value">{companyRaw.pain_point_category}</div>
                </div>
              )}
              {companyRaw.value_prop_for_pain_point && (
                <div className="detail-field">
                  <div className="detail-field-label">Value Prop</div>
                  <div className="detail-field-value">{companyRaw.value_prop_for_pain_point}</div>
                </div>
              )}
              {rawData.one_line_relevance_hypothesis && (
                <div className="detail-field" style={{ gridColumn: '1 / -1' }}>
                  <div className="detail-field-label">Relevance Hypothesis</div>
                  <div className="detail-field-value">{rawData.one_line_relevance_hypothesis}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Events */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="section-header">
          <span className="section-title">Email Events</span>
          <span className="section-count">{events.length}</span>
        </div>

        {events.length === 0 ? (
          <Empty icon="📭" message="No events yet" hint="Send an email to start tracking engagement." />
        ) : (
          <div className="timeline">
            {[...events].reverse().map(evt => (
              <div key={evt.id} className="timeline-item">
                <div
                  className="timeline-dot"
                  style={{ background: eventColor(evt.event_type as EventType) }}
                />
                <div className="timeline-body">
                  <div className="timeline-top">
                    <EventBadge type={evt.event_type as EventType} />
                    <span className="timeline-time"><AbsTime iso={evt.occurred_at} /></span>
                  </div>
                  {evt.event_metadata && Object.keys(evt.event_metadata).length > 0 && (
                    <div className="timeline-meta">
                      {Boolean(evt.event_metadata.subject) && (
                        <span>Subject: <em>{String(evt.event_metadata.subject)}</em></span>
                      )}
                      {Boolean(evt.event_metadata.mocked) && (
                        <span style={{ marginLeft: 8, color: 'var(--text-dim)' }}>[mock send]</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="divider" />
        <SimulateEventPanel leadId={leadId} onDone={() => void loadAll()} />
      </div>

       {/* Classify reply */}
      <ClassifyReplyPanel leadId={leadId} onDone={() => void refreshSilently()} />
       
      {/* Score history */}
      <div className="card">
        <div className="section-header">
          <span className="section-title">Score History</span>
          <span className="section-count">{history.length}</span>
        </div>

        {history.length === 0 ? (
          <Empty icon="📊" message="No score history yet" />
        ) : (
          <div className="history-list">
            {[...history].reverse().map(h => (
              <div key={h.id} className="history-item">
                <div className="history-arrow">
                  {h.old_score != null ? (
                    <>
                      <span style={{ color: scoreCol(h.old_score) }}>{h.old_score}</span>
                      <span style={{ color: 'var(--text-dim)' }}>→</span>
                    </>
                  ) : null}
                  <span style={{ color: scoreCol(h.new_score) }}>{h.new_score}</span>
                </div>
                <span className="history-reason">{h.reason}</span>
                <span className="history-time"><AbsTime iso={h.created_at} /></span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function eventColor(type: EventType): string {
  const map: Record<EventType, string> = {
    sent: '#4f7dff',
    delivered: '#a06af8',
    opened: '#f5c842',
    replied: '#29d87a',
    unsubscribed: '#f0524f',
  };
  return map[type] ?? '#555d70';
}

function scoreCol(v: number): string {
  if (v >= 70) return '#29d87a';
  if (v >= 40) return '#f5c842';
  return '#a06af8';
}
