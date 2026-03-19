# Carrier API

FastAPI backend for HappyRobot inbound carrier call automation.

## Quick Start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

## Docker

```bash
docker build -t carrier-api .
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data carrier-api
```

See [CLAUDE.md](CLAUDE.md) for full documentation.
