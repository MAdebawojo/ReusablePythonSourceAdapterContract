from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

@dataclass(frozen=True)
class CanonicalRecord:
    """The single record shape every source adapter must produce.

    Attributes:
        country_code (str): ISO 3166-1 alpha-2, required. Never defaulted.
        source_date (date): The date the source data refers to.
        fetched_at (datetime): When the data was retrieved. Must be timezone-aware (UTC).
        attributes (dict): Source-specific extra fields, kept as given.
        region_code (str, optional): The region code. None means the source gave 
            no region.
        geom (dict, optional): GeoJSON geometry in WGS84 (EPSG:4326), with coordinates 
            ordered longitude then latitude. None when the source has no geometry.
    """
    country_code: str
    source_id: str
    source_date: date
    fetched_at: datetime
    attributes: dict[str, Any]
    region_code: str | None = None
    geom: dict | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict representation."""
        return {
            "country_code": self.country_code,
            "source_id": self.source_id,
            "source_date": self.source_date.isoformat(),
            "fetched_at": self.fetched_at.isoformat(),
            "attributes": self.attributes,
            "region_code": self.region_code,
            "geom": self.geom,
        }


