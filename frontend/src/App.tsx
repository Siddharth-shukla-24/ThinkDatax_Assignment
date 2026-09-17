import { useState } from 'react';
import type { Campaign } from './lib/types';
import CampaignsPage from './pages/CampaignsPage';
import CampaignDetailPage from './pages/CampaignDetailPage';
import AllLeadsPage from './pages/AllLeadsPage';
import LeadDetailPage from './pages/LeadDetailPage';
import './index.css';

// ─── Navigation icons (inline SVG to avoid deps) ────────────────────────────
function IconCampaigns() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
    </svg>
  );
}

function IconLeads() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

// ─── Route types ──────────────────────────────────────────────────────────────
type Route =
  | { page: 'campaigns' }
  | { page: 'campaign-detail'; campaign: Campaign }
  | { page: 'all-leads' }
  | { page: 'lead-detail'; leadId: number; campaignName?: string; fromCampaign?: Campaign };

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [route, setRoute] = useState<Route>({ page: 'campaigns' });

  function nav(r: Route) { setRoute(r); }

  const currentTopPage =
    route.page === 'campaigns' || route.page === 'campaign-detail' ? 'campaigns' : 'all-leads';

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>StyleSense AI</h1>
          <p>Lead Generation Platform</p>
        </div>
        <nav className="sidebar-nav">
          <div className="nav-label">Navigation</div>
          <button
            className={`nav-item ${currentTopPage === 'campaigns' ? 'active' : ''}`}
            onClick={() => nav({ page: 'campaigns' })}
          >
            <IconCampaigns />
            Campaigns
          </button>
          <button
            className={`nav-item ${currentTopPage === 'all-leads' ? 'active' : ''}`}
            onClick={() => nav({ page: 'all-leads' })}
          >
            <IconLeads />
            All Leads
          </button>
        </nav>

        {/* Footer */}
        <div style={{
          padding: '14px 16px',
          borderTop: '1px solid var(--border)',
          fontSize: 11,
          color: 'var(--text-dim)',
        }}>
          ThinkDataX Assignment<br />
          <span style={{ color: 'var(--text-dim)', fontFamily: 'monospace' }}>
            localhost:8000
          </span>
        </div>
      </aside>

      {/* Main content */}
      <main className="main">
        {route.page === 'campaigns' && (
          <CampaignsPage
            onSelect={campaign => nav({ page: 'campaign-detail', campaign })}
          />
        )}

        {route.page === 'campaign-detail' && (
          <CampaignDetailPage
            campaign={route.campaign}
            onBack={() => nav({ page: 'campaigns' })}
            onSelectLead={leadId =>
              nav({
                page: 'lead-detail',
                leadId,
                campaignName: route.campaign.name,
                fromCampaign: route.campaign,
              })
            }
          />
        )}

        {route.page === 'all-leads' && (
          <AllLeadsPage
            onSelectLead={leadId =>
              nav({ page: 'lead-detail', leadId })
            }
          />
        )}

        {route.page === 'lead-detail' && (
          <LeadDetailPage
            leadId={route.leadId}
            campaignName={route.campaignName}
            onBack={() => {
              if (route.fromCampaign) {
                nav({ page: 'campaign-detail', campaign: route.fromCampaign });
              } else if (currentTopPage === 'all-leads') {
                nav({ page: 'all-leads' });
              } else {
                nav({ page: 'campaigns' });
              }
            }}
            onBackToCampaign={() => {
              if (route.fromCampaign) {
                nav({ page: 'campaign-detail', campaign: route.fromCampaign });
              } else {
                nav({ page: 'campaigns' });
              }
            }}
          />
        )}
      </main>
    </div>
  );
}
