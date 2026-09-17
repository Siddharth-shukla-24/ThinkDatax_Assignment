import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';
import type { Campaign, CampaignCreate, IcpCriteria } from '../lib/types';
import { Spinner, Empty, ErrorAlert } from '../components/shared';

interface Props {
  onSelect: (campaign: Campaign) => void;
}

// ─── Create Campaign Modal ────────────────────────────────────────────────────
function CreateModal({ onClose, onCreate }: { onClose: () => void; onCreate: (c: Campaign) => void }) {
  const [name, setName] = useState('');
  const [titles, setTitles] = useState('');
  const [industry, setIndustry] = useState('');
  const [region, setRegion] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState('');

  const submit = async () => {
    if (!name.trim()) { setErr('Campaign name is required.'); return; }
    setSaving(true);
    setErr('');
    try {
      const icp: IcpCriteria = {};
      if (titles.trim()) icp.titles = titles.split(',').map(t => t.trim()).filter(Boolean);
      if (industry.trim()) icp.industry = industry.trim();
      if (region.trim()) icp.region = region.trim();
      if (companySize.trim()) icp.company_size = companySize.trim();

      const payload: CampaignCreate = {
        name: name.trim(),
        icp_criteria: Object.keys(icp).length ? icp : null,
      };
      const c = await api.campaigns.create(payload);
      onCreate(c);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Failed to create campaign.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h3>New Campaign</h3>
        {err && <ErrorAlert message={err} />}

        <div className="form-group">
          <label className="form-label">Campaign Name *</label>
          <input
            className="form-input"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="e.g. Q4 Apparel Outreach"
            autoFocus
          />
        </div>

        <div style={{ marginBottom: 10, fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '.05em' }}>
          ICP Criteria (optional)
        </div>

        <div className="form-group">
          <label className="form-label">Target Titles</label>
          <input
            className="form-input"
            value={titles}
            onChange={e => setTitles(e.target.value)}
            placeholder="Head of Merchandising, VP of Retail (comma-separated)"
          />
          <span className="form-hint">Comma-separated list of titles to match</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <div className="form-group">
            <label className="form-label">Industry</label>
            <input
              className="form-input"
              value={industry}
              onChange={e => setIndustry(e.target.value)}
              placeholder="Fashion"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Region</label>
            <input
              className="form-input"
              value={region}
              onChange={e => setRegion(e.target.value)}
              placeholder="US"
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Company Size</label>
          <input
            className="form-input"
            value={companySize}
            onChange={e => setCompanySize(e.target.value)}
            placeholder="200-500"
          />
        </div>

        <div className="modal-actions">
          <button className="btn btn-ghost" onClick={onClose} disabled={saving}>Cancel</button>
          <button className="btn btn-primary" onClick={submit} disabled={saving}>
            {saving ? <Spinner /> : 'Create Campaign'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Campaigns Page ───────────────────────────────────────────────────────────
export default function CampaignsPage({ onSelect }: Props) {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setErr('');
    try {
      const page = await api.campaigns.list(1, 50);
      setCampaigns(page.items);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Failed to load campaigns.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  const handleCreated = (c: Campaign) => {
    setCampaigns(prev => [c, ...prev]);
    setShowCreate(false);
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-header-left">
          <h2>Campaigns</h2>
          <p>Manage outreach campaigns and trigger AI lead discovery.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          + New Campaign
        </button>
      </div>

      {err && <ErrorAlert message={err} />}

      {loading ? (
        <div className="state-center"><Spinner large /></div>
      ) : campaigns.length === 0 ? (
        <Empty icon="📋" message="No campaigns yet" hint="Create your first campaign to start discovering leads." />
      ) : (
        <div className="campaign-grid">
          {campaigns.map(c => (
            <div key={c.id} className="campaign-card" onClick={() => onSelect(c)}>
              <h3>{c.name}</h3>
              <div className="campaign-meta">
                <span>ID #{c.id}</span>
                <span>{new Date(c.created_at).toLocaleDateString()}</span>
              </div>
              {c.icp_criteria && (
                <div className="campaign-icp">
                  {c.icp_criteria.industry && (
                    <span className="icp-tag">🏭 {c.icp_criteria.industry}</span>
                  )}
                  {c.icp_criteria.region && (
                    <span className="icp-tag">🌍 {c.icp_criteria.region}</span>
                  )}
                  {c.icp_criteria.company_size && (
                    <span className="icp-tag">👥 {c.icp_criteria.company_size}</span>
                  )}
                  {(c.icp_criteria.titles ?? []).map(t => (
                    <span key={t} className="icp-tag">🎯 {t}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <CreateModal
          onClose={() => setShowCreate(false)}
          onCreate={handleCreated}
        />
      )}
    </div>
  );
}
