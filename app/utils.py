import csv
from datetime import date
from pathlib import Path
from typing import Optional

from app.models import Load

CSV_PATH = Path(__file__).parent.parent / "data" / "loads.csv"

FIELDNAMES = [
    "load_id", "origin", "destination", "pickup_datetime", "delivery_datetime",
    "equipment_type", "loadboard_rate", "notes", "weight", "commodity_type",
    "num_of_pieces", "miles", "dimensions",
]


def _read_rows() -> list[dict]:
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _row_to_load(row: dict) -> Load:
    return Load(
        load_id=row["load_id"],
        origin=row["origin"],
        destination=row["destination"],
        pickup_datetime=row["pickup_datetime"],
        delivery_datetime=row["delivery_datetime"],
        equipment_type=row["equipment_type"],
        loadboard_rate=float(row["loadboard_rate"]),
        notes=row["notes"],
        weight=float(row["weight"]),
        commodity_type=row["commodity_type"],
        num_of_pieces=int(row["num_of_pieces"]),
        miles=float(row["miles"]),
        dimensions=row["dimensions"],
    )


def get_loads(
    origin: Optional[str] = None,
    min_distance: Optional[float] = None,
    max_distance: Optional[float] = None,
    pickup_date: Optional[date] = None,
    equipment_type: Optional[str] = None,
) -> list[Load]:
    filtered_loads = _read_rows()

    if origin:
        filtered_loads = [
            load for load in filtered_loads
            if load["origin"].lower() == origin.lower()
        ]

    if min_distance is not None:
        filtered_loads = [
            load for load in filtered_loads
            if float(load["miles"]) >= min_distance
        ]

    if max_distance is not None:
        filtered_loads = [
            load for load in filtered_loads
            if float(load["miles"]) <= max_distance
        ]

    if pickup_date:
        pickup_date_str = pickup_date.strftime("%Y-%m-%d")
        filtered_loads = [
            load for load in filtered_loads
            if load["pickup_datetime"].startswith(pickup_date_str)
        ]

    if equipment_type:
        filtered_loads = [
            load for load in filtered_loads
            if load["equipment_type"].lower() == equipment_type.lower()
        ]

    return [_row_to_load(row) for row in filtered_loads]

def get_load_by_id(load_id: str) -> Optional[Load]:
    for row in _read_rows():
        if row["load_id"] == load_id:
            return _row_to_load(row)
    return None


def create_load(load: Load) -> Load:
    rows = _read_rows()
    if any(r["load_id"] == load.load_id for r in rows):
        return None  # signals duplicate

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(load.model_dump())

    return load
