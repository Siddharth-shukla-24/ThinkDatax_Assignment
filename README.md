# StyleSense AI - Lead Generation & Email Outreach Platform

Take-home assignment submission for ThinkDataX - Full Stack + AI Engineer.

## Overview

StyleSense AI is a lightweight AI-assisted lead generation and outreach platform.

The application supports:

- Campaign and ICP management
- AI-assisted lead discovery with source-backed research
- Lead scoring from 0 to 100
- Personalized outbound email generation
- Email send tracking and unsubscribe suppression
- Inbound reply classification
- AI-generated draft responses
- A React dashboard for managing campaigns and leads

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Pydantic

### Frontend
- React 19
- TypeScript
- Vite
- CSS custom properties

### AI / Data
- Anthropic Claude
- Tavily search
- Resend email API

## Architecture

```text
React Dashboard
      |
      v
FastAPI REST API
      |
      +---- PostgreSQL
      |
      +---- Anthropic Claude
      |
      +---- Tavily Search
      |
      +---- Resend Email



## Sample Emails

Three sample outreach emails based on the Appendix A skeleton and public company research are included in `docs/sample_emails.md`.

These examples are for demonstration only and were not sent to the referenced individuals.

## What I'd Build Next

With more time, I would add click tracking with behavior-based follow-up rules, real inbound email ingestion through provider webhooks/IMAP, a background job queue for email and discovery workloads, a more autonomous discovery planning loop, and optional storage for raw/semi-structured data.

## AI Provider Note

The application supports Anthropic and Tavily integrations. Local verification used the deterministic mock/fallback path because provider API keys were not configured. The fallback remains behind the same discovery/classification service boundaries so live providers can be enabled through environment variables.




## What I'd Build Next

With more time, I would add click tracking with behavior-based follow-up rules, real inbound email ingestion via provider webhooks/IMAP, a background job queue for email and discovery workloads, a more autonomous lead-discovery planning loop, and an optional separate store for raw/semi-structured data.