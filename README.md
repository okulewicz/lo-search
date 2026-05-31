# LO Search – Architecture

High-school explorer for Warsaw and Mazovian region with AI-powered school profiles and public transit routing.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        React Frontend (Vite)                         │
│  SchoolList  │  SchoolDetail  │  RoutePlanner  │  SchoolMap (Leaflet) │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ REST / JSON  (proxied by Vite dev server)
┌──────────────────────────▼───────────────────────────────────────────┐
│                      FastAPI Backend (Python)                        │
│  /api/schools   /api/routes   /api/tasks                             │
└──────┬───────────────┬──────────────────┬────────────────────────────┘
       │               │                  │
       ▼               ▼                  ▼
  PostgreSQL        Celery Worker       Transit Router
  (SQLAlchemy)      (Redis broker)      ┌─────────────────┐
                         │              │ Google Maps API │
                    Pipeline Tasks      │       OR        │
                    ┌──────────┐        │ OTP2 (GraphQL)  │
                    │  RSPO    │        └─────────────────┘
                    │  Client  │
                    ├──────────┤
                    │ SmartScraper
                    │  ├── StaticScraper (httpx + BS4)
                    │  └── PlaywrightScraper (Chromium)
                    ├──────────┤
                    │ ProfileExtractor
                    │  └── OllamaClient  →  local LLM
                    └──────────┘
```

---

## Modules

### 1. Transit Module (`backend/app/modules/transit/`)

Provides a unified `TransitProviderBase` interface. The active provider is selected via the `TRANSIT_PROVIDER` env variable.

| Provider | Implementation | Notes |
|---|---|---|
| `otp` (default) | `OTPTransitProvider` | Uses OTP2 GraphQL endpoint |
| `google_maps` | `GoogleMapsTransitProvider` | Requires `GOOGLE_MAPS_API_KEY` |

**Switching providers** requires only changing `TRANSIT_PROVIDER=google_maps` in `.env` — no code changes.

---

### 2. School Discovery Module (`backend/app/modules/school_discovery/`)

- **`RSPOClient`** — wraps the public [RSPO REST API](https://api.rspo.gov.pl) (Polish official school registry). Iterates over all Mazovian high-school types (LO, Technikum, Branżowe) page-by-page.
- **`SchoolDiscoveryService`** — upserts fetched records into the `schools` table using RSPO ID as the natural key.

Trigger via: `POST /api/tasks/sync-schools`

---

### 3. Web Scraper Module (`backend/app/modules/scraper/`)

Two-stage smart scraping strategy:

```
URL → StaticScraper (httpx + BeautifulSoup)
          │
          ▼
   < 80 words extracted?
          │ yes
          ▼
   PlaywrightScraper (headless Chromium, networkidle)
```

`SmartScraper` automatically falls back to the JS-rendering path when the static result looks like a skeleton SPA. Results are stored in the `scraped_pages` table.

Trigger via: `POST /api/tasks/scrape/{school_id}`

---

### 4. Information Extractor Module (`backend/app/modules/extractor/`)

- **`OllamaClient`** — thin async HTTP client for the local Ollama REST API (`/api/generate`, `/api/chat`).
- **`ProfileExtractor`** — sends scraped plain text to Ollama with a Polish-language structured extraction prompt. Parses the JSON response into typed fields stored in `school_profiles`.

Extracted fields per school:
- `class_profiles` – profiles of study streams (JSONB)
- `languages_offered` – foreign languages (JSONB array)
- `extracurricular_activities` – clubs, sport, arts (JSONB array)
- `notable_achievements` – rankings, olympiad results (JSONB array)
- `description_summary` – 2-3 sentence summary

Trigger via: `POST /api/tasks/extract/{school_id}`

---

## Database Schema

```
schools
  id (UUID PK)
  rspo_id (unique)
  name, school_type
  address_*, latitude, longitude
  website_url, phone, email
  is_public

scraped_pages
  id (UUID PK)
  school_id (FK → schools)
  url, raw_html, plain_text
  js_rendered, http_status, error_message, scraped_at

school_profiles
  id (UUID PK)
  school_id (FK → schools, unique)
  class_profiles (JSONB)
  languages_offered (JSONB)
  extracurricular_activities (JSONB)
  notable_achievements (JSONB)
  description_summary (TEXT)
  raw_extraction (JSONB)
  model_used, extracted_at
```

---

## Data Pipeline

Full pipeline can be triggered in one call: `POST /api/tasks/run-pipeline`

```
sync_schools  →  scrape_school (×N parallel)  →  extract_profile (×N parallel)
```

Orchestrated by Celery chains/groups. Task status: `GET /api/tasks/status/{task_id}`

---

## Getting Started

### Prerequisites
- Docker + Docker Compose
- Ollama running locally with a model pulled (e.g. `ollama pull llama3.2`)
- (Optional) Google Maps API key or a running OTP2 instance for transit

### Quick Start

```bash
# 1. Copy env file and fill in secrets
cp .env.example .env

# 2. Start all services
docker compose up -d

# 3. Trigger initial data sync
curl -X POST http://localhost:8000/api/tasks/run-pipeline

# 4. Open frontend
open http://localhost:3000
```

### Local Development (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload

# Celery worker (separate terminal)
celery -A app.celery_app worker --loglevel=info

# Frontend
cd frontend
npm install
npm run dev
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TypeScript, TanStack Query, React Leaflet, Tailwind CSS |
| Backend API | FastAPI, SQLAlchemy (async), Pydantic v2 |
| Async tasks | Celery + Redis |
| Database | PostgreSQL 16 |
| Scraping | Playwright (Chromium), BeautifulSoup4, httpx |
| AI extraction | Ollama (local LLM – llama3.2 by default) |
| Transit | Open Trip Planner 2 (default) / Google Maps Directions API |
| School data | RSPO public REST API |
| Infrastructure | Docker Compose |

User clicks "Sync all schools"

  * → FastAPI responds instantly: {"task_id": "abc-123"}
  * → Worker does all the heavy work in the background
  * → User polls GET /api/tasks/status/abc-123 to check progress


```
  ┌─────────────┐   1. POST /api/tasks/run-pipeline
  │   FastAPI   │──────────────────────────────────►
  │  (backend)  │   publishes task message to Redis
  └─────────────┘
                          ┌─────────┐
                          │  Redis  │  ← acts as the post-box
                          │  Queue  │     (broker + result store)
                          └────┬────┘
                               │ 2. Worker picks up the message
                               ▼
                      ┌────────────────┐
                      │ Celery Worker  │
                      │  (worker svc)  │
                      │                │
                      │  sync_schools  │ ← calls RSPO API
                      │  scrape_school │ ← calls Playwright
                      │  extract_profile│ ← calls Ollama
                      └────────────────┘
                               │ 3. Stores result back in Redis
                               ▼
                          ┌─────────┐
                          │  Redis  │
                          │ Results │
                          └─────────┘
                               │ 4. FastAPI reads result on demand
                               ▼
                      GET /api/tasks/status/abc-123
```