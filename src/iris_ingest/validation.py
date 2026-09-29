from .models import CanonicalRecord
from .countries import validate_country_code
from .geometry import validate_geom

def validate_record(record: CanonicalRecord) -> list[str]:
    """Return a list of problems. An empty list means the record is valid."""
    problems: list[str] = []
    if not record.country_code:
        problems.append("Missing country code")
    elif not validate_country_code(record.country_code):
        problems.append(f"Invalid country code: {record.country_code}")

    problems.extend(validate_geom(record.geom))

    return problems











