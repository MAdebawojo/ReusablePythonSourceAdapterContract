
from curses import raw
from datetime import date, datetime, timezone
import json
from typing import Iterator

from iris_ingest.adapter import SourceAdapter
from iris_ingest.countries import normalize_country_code
from iris_ingest.errors import NormalizationError
from iris_ingest.geometry import normalize_geometry
from iris_ingest.models import CanonicalRecord


class FixtureAdapter(SourceAdapter):
    adapter_name = "fixture"

    def __init__(self, path: str):
        self.path = path

    def extract(self) -> Iterator[dict]:
        with open(self.path) as f:
            records = json.load(f)
        yield from records

    def normalize(self, raw: dict) -> CanonicalRecord:
        EXTRACTED_KEYS = {"source_id", "country", "region", "lat", "lon", "source_date"}

        source_id = raw.get("source_id")
        country_code = normalize_country_code(raw.get("country"))
        fetched_at = datetime.now(timezone.utc)
        region_code = raw.get("region")
        lat = raw.get("lat", None)
        lon = raw.get("lon", None)
        attributes = {k: v for k, v in raw.items() if k not in EXTRACTED_KEYS}

        try:
            source_date = date.fromisoformat(raw.get("source_date")) if raw.get("source_date") else None
        except ValueError as e:
            raise NormalizationError(f"Invalid source_date: {raw.get('source_date')!r}") from e

        if lat is not None and lon is not None:
            try:
                geom = normalize_geometry(lat, lon)
            except ValueError as e:
                # invalid coordinates, raise NormalizationError with the original exception message
                raise NormalizationError(f"{e}") from e
        elif lat is None and lon is None:
            geom = None
        else:
            raise NormalizationError("Both lat and lon must be provided together")

        if source_id is None or source_date is None:
            raise NormalizationError("Both source_id and source_date must be provided")

        return CanonicalRecord(
            country_code=country_code,
            source_id=source_id,
            source_date=source_date,
            fetched_at=fetched_at,
            attributes=attributes,
            region_code=region_code,
            geom=geom,
        )