# Carrier API — CLAUDE.md

## Project Purpose

FastAPI backend for **HappyRobot inbound carrier call automation**. When a carrier calls in, HappyRobot's AI agent handles the conversation, queries available loads, negotiates rates, and logs the outcome. This API serves as the data layer between HappyRobot and the load/call data.

---

## Running Locally

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
cd carrier-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then set your API_KEY
uvicorn app.main:app --reload --port 8000
```

Swagger docs available at: `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_KEY` | Yes | Shared secret sent in `X-API-Key` header by all callers |

Copy `.env.example` to `.env` and fill in values before running.

---

## API Endpoints Summary

All endpoints except `GET /` require the `X-API-Key` header.

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |

### Loads (CSV-backed)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/loads` | List loads; filter by `origin`, `destination`, `equipment_type` |
| GET | `/loads/{load_id}` | Get a single load by ID |
| POST | `/loads` | Add a new load to the CSV |

### Call Logs (SQLite via SQLModel)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/log_call_extraction` | Insert a single call log record |
| POST | `/bulk_log_call_extraction` | Upsert a list of call log records |
| GET | `/all_call_extractions` | Return all call log records |
| GET | `/call_analytics` | Return aggregated analytics |

---

## Running with Docker

### Build and run

```bash
docker build -t carrier-api .
docker run -p 8000:8000 -e API_KEY=your-secret-key carrier-api
```

### With a .env file

```bash
docker run -p 8000:8000 --env-file .env carrier-api
```

### Persisting SQLite data

```bash
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data carrier-api
```

---

## Key Architectural Decisions

### CSV as load store
Loads are read from and written to `data/loads.csv` on every request. This is intentional simplicity — no caching, no ORM. The CSV is the source of truth and can be edited directly without a migration step.

### SQLite for call logs
Call logs need querying, aggregation, and upserts, which SQL handles naturally. SQLModel (SQLAlchemy + Pydantic) keeps the model definition in one place. The DB file lives at `./data/calls.db` so it co-locates with the CSV.

### API key auth via dependency
A single FastAPI dependency (`verify_api_key`) is injected on all protected routes. The key comes from the `X-API-Key` header and is validated against the `API_KEY` env var. Easy to swap for OAuth2 later by replacing the dependency.

### No caching on CSV reads
Loads data is small and call volume in this use case is low. Reading from disk on each request keeps the code simple and ensures the AI agent always sees the latest data without cache invalidation logic.
