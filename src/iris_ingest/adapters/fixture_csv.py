
from iris_ingest.adapter import SourceAdapter
from typing import Iterator
import csv

from iris_ingest.countries import normalize_country_code
from iris_ingest.errors import NormalizationError
from iris_ingest.geometry import normalize_geometry
from iris_ingest.models import CanonicalRecord
from datetime import date, datetime, timezone

class FixtureCsvAdapter(SourceAdapter):
    adapter_name = "fixture_csv"

    def __init__(self, path: str):
        self.path = path

    def extract(self) -> Iterator[dict]:
        with open(self.path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row
                
    def normalize(self, raw: dict) -> CanonicalRecord:
            source_id = raw.get("unique_code")
            if not source_id:
                raise NormalizationError("Missing unique_code")

            country_code = normalize_country_code(raw.get("nation"))

            try:
                source_date = date.fromisoformat(raw.get("updated_at")) if raw.get("updated_at") else None
            except (ValueError, TypeError) as e:
                raise NormalizationError(f"Invalid date: {raw.get('updated_at')}") from e

            lat_str = raw.get("y")
            lon_str = raw.get("x")
            
            if lat_str and lon_str:
                try:
                    geom = normalize_geometry(lat_str, lon_str)
                except (ValueError, TypeError) as e:
                    raise NormalizationError(str(e)) from e
            else:
                geom = None

            return CanonicalRecord(
                country_code=country_code,
                source_id=source_id,
                source_date=source_date,
                fetched_at=datetime.now(timezone.utc),
                attributes={"notes": raw.get("notes")},
                region_code=raw.get("state_code"),
                geom=geom,
            )