# StyleSense AI — Lead Generation & Email Outreach Platform

Take-home assignment submission for ThinkDataX — Full Stack + AI Engineer.

## Overview

StyleSense AI is an AI-assisted lead discovery and outreach platform built for a fictional B2B AI SaaS specializing in demand forecasting, inventory allocation, and merchandising intelligence for apparel and fashion brands.

The platform streamlines the outbound sales workflow:
- Campaign and ICP definition (target titles, industry, region, company size)
- AI agent lead discovery using search/fetch tools with grounding checks against source URLs
- Dual-component lead scoring (0–100) combining ICP fit and engagement history
- Dynamic cold outreach email generation using the Appendix A skeleton and verified research
- Outreach sending via provider API in sandbox/mock mode with tracking pixel and unsubscribe links
- Event tracking (`sent`, `delivered`, `opened`, `unsubscribed`) and automatic suppression list enforcement
- Inbound reply classification (5 intent classes) and contextual AI draft response generation
- A React console for managing campaigns, viewing ranked leads, and tracking lifecycle events

---

## Tech Stack

### Backend
- **Language & Framework:** Python 3.14, FastAPI
- **ORM & Database:** SQLAlchemy 2.x, PostgreSQL (psycopg3 driver)
- **Data Validation:** Pydantic v2 & Pydantic-Settings
- **Testing & Tooling:** Pytest, HTTPX

### Frontend
- **Framework & Tooling:** React 19, TypeScript, Vite
- **Styling:** Vanilla CSS with custom properties (sleek dark mode, zero external CSS bloat)
- **Client:** Native Fetch API client with bearer token authentication

### AI & External Services
- **LLM Provider:** Anthropic Claude (`claude-sonnet-5`) with function/tool calling; deterministic mock fallback when API key is absent
- **Web Search:** Tavily Search API; structured mock fallback when API key is absent
- **Email Delivery:** Resend API (sandbox mode); mock send fallback when API key is absent

---

## Architecture & Design Decisions

### System Architecture

```text
       +--------------------------------------------+
       |           React Frontend Console           |
       |  (Campaigns, Ranked Leads, Detail & State) |
       +--------------------------------------------+
                             |  HTTP (Bearer Token)
                             v
       +--------------------------------------------+
       |             FastAPI REST API               |
       |    Validation, Auth, Pagination, Errors    |
       +---------------------+----------------------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
+-----------------+ +-----------------+ +-----------------+
|   PostgreSQL    | | Anthropic Claude| |  Resend Email   |
| Relational DB + | |  Tool-Use Agent | |  Sandbox Send + |
|  JSONB Storage  | | & Reply Classif.| |  Tracking/Pixel |
+-----------------+ +--------+--------+ +-----------------+
                             |
                             v
                    +-----------------+
                    |  Tavily Search  |
                    |  Web Discovery  |
                    +-----------------+
```

### Data Model & Event-Derived State Separation
- **Relational Schema:** PostgreSQL tables for `companies`, `campaigns`, `leads`, `email_events`, `scores`, `score_history`, and `suppressions`.
- **Semi-Structured Payloads:** `JSONB` columns store raw scraped research signals, LLM extraction metadata, and event payloads without requiring a secondary database.
- **Event / State Separation:** Raw email events (`sent`, `delivered`, `opened`, `replied`, `unsubscribed`) are stored immutably in `email_events`. Derived state (`lead.status`, `scores`, and `score_history`) is computed directly from raw history, enabling reproducible audit trails and dynamic score recomputation.

### Key Decisions & Single-Language Backend Rationale
- **FastAPI Backend:** Python was selected as the single backend language because it natively bridges relational API design, modern asynchronous HTTP services, and the Python AI/NLP ecosystem (Anthropic API, tool-calling pipelines, text classification, and data processing).
- **Synchronous Execution:** In accordance with core scope requirements, operations run synchronously, with background job queues (Celery/Redis) reserved as a stretch enhancement.
- **Single-User Security:** Protected routes require a static bearer token (`API_TOKEN`) verified via `secrets.compare_digest`. Public tracking pixel and unsubscribe routes remain unauthenticated by design.

---

## Lead Scoring Weights

Lead scores range from **0 to 100**, combining **Fit** (max 60 points) and **Engagement** (max 40 points). Weights are defined in `backend/app/config/scoring_weights.json` rather than hardcoded constants:

### 1. Fit Component (Max 60 points)
- **Title Match:** +25 points (e.g., Head of Merchandising, Demand Planning)
- **Industry Match:** +15 points (e.g., Fashion, Apparel)
- **Region Match:** +10 points (e.g., US, North America)
- **Company Size Match:** +10 points (e.g., 500–1000 employees)

### 2. Engagement Component (Max 40 points)
Calculated from the highest-value recorded event:
- **Replied:** 40 points
- **Opened:** 20 points
- **Delivered / Sent:** 5 points
- **Unsubscribed:** Score capped at **5 points** maximum, regardless of fit.

Scores are recomputed on lead creation and on every subsequent event, logging the delta and rationale into `score_history`.

---

## Reply Classification & Evaluation Accuracy

Inbound email replies are classified into 5 intents:
1. `Interested` — prospect expresses interest or requests a meeting
2. `Not Interested` — prospect declines outreach or mentions competitors
3. `Needs Follow-up` — timing is bad, requests circling back later
4. `Unsubscribe Request` — explicit opt-out demand
5. `Other` — ambiguous, unrelated, or unrecognized queries

A contextual response is drafted for human approval based on the classified intent and lead context.

### Evaluation Accuracy
- **Result: 8/8 correct (100% accuracy)** on the hand-labeled evaluation dataset.
- Evaluated via `python -m scripts.eval_classifier` covering all 5 intent classes.

---

## Compliance & Privacy (GDPR / CAN-SPAM)

Every outreach email includes a working one-click unsubscribe link (which immediately records an `unsubscribed` event, suppresses the address in the `suppressions` table, and is strictly honored on all future sends) and identifies the sender (StyleSense AI) — satisfying the core legal requirements of GDPR and CAN-SPAM; no marketing outreach is ever transmitted to a suppressed address.

### Demonstration Safety & Real-Person Data Note
In compliance with Section 8 constraints ("Never email real people who have not consented"), outreach emails in this repository are demonstration samples only. Research references public executive announcements from corporate investor/leadership pages, and outbound sending defaults to mock or sandbox mode (`onboarding@resend.dev`) with zero private contact information stored.

---

## Sample Outreach Emails

Three sample outreach emails generated directly from the actual `render_email()` template function using public company research (Target, Under Armour, and lululemon) are documented in [`docs/sample_emails.md`](file:///c:/ThinkDatax_Assignment/docs/sample_emails.md). All samples follow the Appendix A locked skeleton with token-grounded claims and are marked `[DEMO / NOT SENT]`.

---

## Setup & Run Instructions

### Prerequisites
- Python 3.11+ (Python 3.14 supported)
- Node.js 18+ and npm
- PostgreSQL 14+ running locally

### 1. Database Setup
Create the PostgreSQL database:
```sql
CREATE DATABASE thinkdatax;
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Database tables are initialized automatically on application startup via SQLAlchemy.

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

### 4. Running the Development Servers

**Start Backend (port 8000):**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Start Frontend (port 5173):**
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Verification & Testing Commands

### 1. Run Backend Unit & Integration Tests
```bash
cd backend
pytest -v
```
Runs 13 test suites covering reply classification fallback, API auth, lead scoring fit/engagement rules, and unsubscribed caps.

### 2. Run Reply Classifier Evaluation
```bash
cd backend
python -m scripts.eval_classifier
```
Executes the evaluation suite across the 8 labeled reply examples and outputs accuracy.

### 3. Build Frontend
```bash
cd frontend
npm run build
```
Executes TypeScript compilation (`tsc -b`) and Vite production bundle generation.

---

## What I'd Build Next (Stretch Goals)

With additional time, the following enhancements would be prioritized:
1. **Real Inbound Email Webhook / IMAP Ingestion:** Replace manual paste reply simulation with live Resend/SendGrid inbound parse webhooks or IMAP polling.
2. **Background Job Queue:** Introduce Celery or ARQ backed by Redis to handle discovery crawling and bulk email dispatch asynchronously with retry backoff.
3. **Behavior-Driven Follow-Up Sequences:** Implement automated multi-step sequences (e.g., if no open within 3 business days, dispatch gentle follow-up template).
4. **Autonomous Multi-Step Agentic Discovery:** Allow the discovery agent to dynamically formulate secondary search queries, score snippet relevance, and self-correct when search results lack merchandising titles.
5. **Secondary Document Store:** Introduce MongoDB alongside PostgreSQL for storing complete scraped HTML trees and unstructured agent reasoning traces.