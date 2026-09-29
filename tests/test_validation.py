from datetime import date, datetime, timezone
from iris_ingest.models import CanonicalRecord
from iris_ingest.validation import validate_record
from iris_ingest.countries import normalize_country_code, validate_country_code


def test_invalid_country_code_is_rejected():
    record = CanonicalRecord(
        country_code="XX",
        source_id="source_1",
        source_date=date(2024, 6, 1),
        fetched_at=datetime(2024, 6, 2, tzinfo=timezone.utc),
        attributes={"key": "value"},
        region_code="CA",
        geom={"type": "Point", "coordinates": [-122.4194, 37.7749]},
    )

    result = validate_record(record)

    assert result != [], f"Expected problems for invalid country code, got: {result}"

def test_valid_country_code_passes():
    record = CanonicalRecord(
        country_code="DE",
        source_id="source_1",
        source_date=date(2024, 6, 1),
        fetched_at=datetime(2024, 6, 2, tzinfo=timezone.utc),
        attributes={"key": "value"},
        region_code="NW",
        geom={"type": "Point", "coordinates": [6.7762, 51.2217]},
    )

    result = validate_record(record)

    assert result == [], f"Expected no problems, got: {result}"


def test_normalize_then_validate_lowercase_code():
    assert normalize_country_code("de") == "DE"
    assert validate_country_code("de") is False
    assert validate_country_code(normalize_country_code("de")) is True