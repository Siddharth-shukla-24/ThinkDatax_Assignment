import type { LeadStatus, EventType } from '../lib/types';

// ─── Spinner ──────────────────────────────────────────────────────────────────
export function Spinner({ large }: { large?: boolean }) {
  return <div className={large ? 'spinner spinner-lg' : 'spinner'} />;
}

// ─── Empty state ─────────────────────────────────────────────────────────────
export function Empty({ icon, message, hint }: { icon: string; message: string; hint?: string }) {
  return (
    <div className="state-center">
      <div className="state-icon">{icon}</div>
      <p>{message}</p>
      {hint && <small>{hint}</small>}
    </div>
  );
}

// ─── Error alert ─────────────────────────────────────────────────────────────
export function ErrorAlert({ message }: { message: string }) {
  return (
    <div className="alert alert-error">
      <span>⚠</span>
      <span>{message}</span>
    </div>
  );
}

// ─── Success alert ────────────────────────────────────────────────────────────
export function SuccessAlert({ message }: { message: string }) {
  return (
    <div className="alert alert-success">
      <span>✓</span>
      <span>{message}</span>
    </div>
  );
}

// ─── Info alert ───────────────────────────────────────────────────────────────
export function InfoAlert({ message }: { message: string }) {
  return (
    <div className="alert alert-info">
      <span>ℹ</span>
      <span>{message}</span>
    </div>
  );
}

// ─── Status badge ─────────────────────────────────────────────────────────────
const STATUS_LABELS: Record<LeadStatus, string> = {
  new: 'New',
  sent: 'Sent',
  opened: 'Opened',
  replied: 'Replied',
  unsubscribed: 'Unsubscribed',
};

export function StatusBadge({ status }: { status: LeadStatus }) {
  return (
    <span className={`badge badge-${status}`}>
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}

// ─── Event type badge ─────────────────────────────────────────────────────────
const EVENT_LABELS: Record<EventType, string> = {
  sent: 'Sent',
  delivered: 'Delivered',
  opened: 'Opened',
  replied: 'Replied',
  unsubscribed: 'Unsubscribed',
};

export function EventBadge({ type }: { type: EventType }) {
  return (
    <span className={`badge badge-event-${type}`}>
      {EVENT_LABELS[type] ?? type}
    </span>
  );
}

// ─── Score bar inline (for table) ────────────────────────────────────────────
function scoreColor(value: number): string {
  if (value >= 70) return '#29d87a';
  if (value >= 40) return '#f5c842';
  return '#a06af8';
}

export function ScoreBar({ value }: { value: number | null | undefined }) {
  if (value == null) return <span className="text-dim">—</span>;
  const color = scoreColor(value);
  return (
    <div className="score-cell">
      <span className="score-num" style={{ color }}>{value}</span>
      <div className="score-track">
        <div className="score-fill" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );
}

// ─── Score widget (for detail page) ──────────────────────────────────────────
export function ScoreWidget({
  value,
  fit,
  engagement,
}: {
  value: number;
  fit: number;
  engagement: number;
}) {
  const color = scoreColor(value);
  return (
    <div className="score-widget">
      <div className="score-main">
        <div className="score-circle" style={{ background: `${color}22`, color }}>
          {value}
        </div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color }}>
            {value >= 70 ? 'Hot lead' : value >= 40 ? 'Warm lead' : 'Cold lead'}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
            Total score /100
          </div>
        </div>
      </div>
      <div className="score-breakdown">
        <h4>Breakdown</h4>
        <div className="score-row">
          <span className="score-row-label">ICP Fit</span>
          <div className="score-track" style={{ flex: 1 }}>
            <div
              className="score-fill"
              style={{ width: `${(fit / 60) * 100}%`, background: '#4f7dff' }}
            />
          </div>
          <span className="score-row-val" style={{ color: '#4f7dff' }}>{fit}</span>
          <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>/60</span>
        </div>
        <div className="score-row">
          <span className="score-row-label">Engagement</span>
          <div className="score-track" style={{ flex: 1 }}>
            <div
              className="score-fill"
              style={{ width: `${(engagement / 40) * 100}%`, background: '#f5c842' }}
            />
          </div>
          <span className="score-row-val" style={{ color: '#f5c842' }}>{engagement}</span>
          <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>/40</span>
        </div>
      </div>
    </div>
  );
}

// ─── Relative time ────────────────────────────────────────────────────────────
export function RelativeTime({ iso }: { iso: string }) {
  const d = new Date(iso);
  const diff = (Date.now() - d.getTime()) / 1000;
  let label: string;
  if (diff < 60) label = 'just now';
  else if (diff < 3600) label = `${Math.floor(diff / 60)}m ago`;
  else if (diff < 86400) label = `${Math.floor(diff / 3600)}h ago`;
  else label = d.toLocaleDateString();
  return <time dateTime={iso} title={d.toLocaleString()}>{label}</time>;
}

// ─── Absolute timestamp ───────────────────────────────────────────────────────
export function AbsTime({ iso }: { iso: string }) {
  const d = new Date(iso);
  return (
    <time dateTime={iso} title={d.toLocaleString()}>
      {d.toLocaleDateString()} {d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
    </time>
  );
}
