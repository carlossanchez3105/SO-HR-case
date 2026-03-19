from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.auth import verify_api_key
from app.database import get_session, init_db
from app.models import CallLog, Load, MessageResponse
from app.utils import create_load, get_load_by_id, get_loads

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Carrier Load Sales API",
    description="Backend for HappyRobot inbound carrier call automation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── System ────────────────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    return {"status": "ok", "title": "Carrier Load Sales API", "version": "1.0.0"}


# ── Loads ─────────────────────────────────────────────────────────────────────

@app.get("/loads", response_model=Load, dependencies=[Depends(verify_api_key)])
def list_loads(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None,
):
    results = get_loads(origin=origin, destination=destination, equipment_type=equipment_type)
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No loads found matching filters")
    return results[0]


@app.get("/loads/{load_id}", response_model=Load, dependencies=[Depends(verify_api_key)])
def read_load(load_id: str):
    load = get_load_by_id(load_id)
    if not load:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Load '{load_id}' not found")
    return load

# ── Call Logs ─────────────────────────────────────────────────────────────────

@app.post("/log_call_extraction", response_model=MessageResponse, dependencies=[Depends(verify_api_key)])
def log_call(call: CallLog, session: Session = Depends(get_session)):
    existing = session.get(CallLog, call.Run_ID)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Run_ID '{call.Run_ID}' already exists")
    session.add(call)
    session.commit()
    return MessageResponse(message=f"Call log '{call.Run_ID}' recorded")


@app.post("/bulk_log_call_extraction", response_model=MessageResponse, dependencies=[Depends(verify_api_key)])
def bulk_log_calls(calls: list[CallLog], session: Session = Depends(get_session)):
    for call in calls:
        existing = session.get(CallLog, call.Run_ID)
        if existing:
            for field, value in call.model_dump().items():
                setattr(existing, field, value)
        else:
            session.add(call)
    session.commit()
    return MessageResponse(message=f"Upserted {len(calls)} call log(s)")


@app.get("/all_call_extractions", response_model=list[CallLog], dependencies=[Depends(verify_api_key)])
def all_call_extractions(session: Session = Depends(get_session)):
    return session.exec(select(CallLog)).all()


@app.get("/call_analytics", dependencies=[Depends(verify_api_key)])
def call_analytics(session: Session = Depends(get_session)):
    logs = session.exec(select(CallLog)).all()

    if not logs:
        return {
            "summary": {
                "total_calls": 0,
                "total_closed": 0,
                "success_rate": 0.0,
                "rate_efficiency_ratio": 0.0,
                "avg_negotiation_turns": 0.0,
            },
            "origin_success": {},
            "sentiment_distribution": {},
            "tag_distribution": {},
            "evolution": {},
        }

    total_calls = len(logs)
    total_closed = sum(1 for l in logs if l.flag_closed_deal)
    success_rate = round(total_closed / total_calls, 4) if total_calls else 0.0

    closed_logs = [l for l in logs if l.flag_closed_deal and l.original_rate > 0]
    rate_efficiency_ratio = (
        round(sum(l.final_rate / l.original_rate for l in closed_logs) / len(closed_logs), 4)
        if closed_logs else 0.0
    )

    avg_negotiation_turns = round(sum(l.turns for l in logs) / total_calls, 2) if total_calls else 0.0

    # Origin success
    origin_totals: dict = defaultdict(lambda: {"total": 0, "closed": 0})
    for l in logs:
        origin_totals[l.Origin]["total"] += 1
        if l.flag_closed_deal:
            origin_totals[l.Origin]["closed"] += 1

    # Sentiment distribution
    sentiment_dist: dict = defaultdict(int)
    for l in logs:
        sentiment_dist[l.carrier_sentiment] += 1

    # Tag distribution
    tag_dist: dict = defaultdict(int)
    for l in logs:
        tag_dist[l.call_tag] += 1

    # Evolution (per date)
    evolution: dict = defaultdict(lambda: {"total": 0, "closed": 0})
    for l in logs:
        date_key = l.date_time.strftime("%Y-%m-%d")
        evolution[date_key]["total"] += 1
        if l.flag_closed_deal:
            evolution[date_key]["closed"] += 1

    return {
        "summary": {
            "total_calls": total_calls,
            "total_closed": total_closed,
            "success_rate": success_rate,
            "rate_efficiency_ratio": rate_efficiency_ratio,
            "avg_negotiation_turns": avg_negotiation_turns,
        },
        "origin_success": dict(origin_totals),
        "sentiment_distribution": dict(sentiment_dist),
        "tag_distribution": dict(tag_dist),
        "evolution": dict(sorted(evolution.items())),
    }
