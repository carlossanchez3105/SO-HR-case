"""
Seed the SQLite database with sample call log records.
Run from the project root: python scripts/seed_db.py
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlmodel import Session

load_dotenv()

from app.database import engine, init_db
from app.models import CallLog

SAMPLE_CALLS = [
    CallLog(
        Run_ID="RUN-001",
        date_time=datetime(2026, 3, 18, 9, 14),
        Origin="Chicago IL",
        Destination="Dallas TX",
        equipment_type="Dry Van",
        load_id="LD-1001",
        mc_number="MC-483920",
        carrier_name="Swift Transport LLC",
        original_rate=2850.0,
        final_rate=2700.0,
        turns=3,
        was_transferred=False,
        flag_closed_deal=True,
        carrier_sentiment="Positive",
        call_tag="Booked",
    ),
    CallLog(
        Run_ID="RUN-002",
        date_time=datetime(2026, 3, 18, 10, 45),
        Origin="Los Angeles CA",
        Destination="Phoenix AZ",
        equipment_type="Reefer",
        load_id="LD-1002",
        mc_number="MC-772011",
        carrier_name="Cold Chain Express",
        original_rate=1650.0,
        final_rate=1600.0,
        turns=2,
        was_transferred=False,
        flag_closed_deal=True,
        carrier_sentiment="Neutral",
        call_tag="Booked",
    ),
    CallLog(
        Run_ID="RUN-003",
        date_time=datetime(2026, 3, 18, 13, 22),
        Origin="Houston TX",
        Destination="Memphis TN",
        equipment_type="Flatbed",
        load_id="LD-1004",
        mc_number="MC-901234",
        carrier_name="Iron Road Carriers",
        original_rate=3100.0,
        final_rate=0.0,
        turns=5,
        was_transferred=False,
        flag_closed_deal=False,
        carrier_sentiment="Negative",
        call_tag="No Deal",
    ),
    CallLog(
        Run_ID="RUN-004",
        date_time=datetime(2026, 3, 19, 8, 5),
        Origin="Chicago IL",
        Destination="Columbus OH",
        equipment_type="Dry Van",
        load_id="LD-1005",
        mc_number="MC-334455",
        carrier_name="Midwest Freight Inc",
        original_rate=1450.0,
        final_rate=1450.0,
        turns=1,
        was_transferred=True,
        flag_closed_deal=False,
        carrier_sentiment="Neutral",
        call_tag="Transferred",
    ),
    CallLog(
        Run_ID="RUN-005",
        date_time=datetime(2026, 3, 19, 11, 30),
        Origin="Dallas TX",
        Destination="Miami FL",
        equipment_type="Dry Van",
        load_id="LD-1007",
        mc_number="MC-558899",
        carrier_name="Sunbelt Logistics",
        original_rate=3400.0,
        final_rate=3200.0,
        turns=4,
        was_transferred=False,
        flag_closed_deal=True,
        carrier_sentiment="Positive",
        call_tag="Booked",
    ),
]


def main():
    init_db()
    with Session(engine) as session:
        for call in SAMPLE_CALLS:
            existing = session.get(CallLog, call.Run_ID)
            if not existing:
                session.add(call)
        session.commit()
    print(f"Seeded {len(SAMPLE_CALLS)} call log records.")


if __name__ == "__main__":
    main()
