from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# ── Pydantic model for CSV-backed loads ──────────────────────────────────────

class Load(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: float
    notes: str
    weight: float
    commodity_type: str
    num_of_pieces: int
    miles: float
    dimensions: str


# ── SQLModel table for call logs ──────────────────────────────────────────────

class CallLog(SQLModel, table=True):
    __tablename__ = "call_logs"

    Run_ID: str = Field(primary_key=True)
    date_time: datetime
    Origin: str
    Destination: str
    equipment_type: str
    load_id: str
    mc_number: str
    carrier_name: str
    original_rate: float
    final_rate: float
    turns: int
    was_transferred: bool
    flag_closed_deal: bool
    carrier_sentiment: str  # Positive / Neutral / Negative
    call_tag: str           # Booked / No Deal / Transferred / Voicemail


# ── Generic response ──────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
