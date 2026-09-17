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