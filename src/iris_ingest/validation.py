from .models import CanonicalRecord
from .countries import validate_country_code

def validate_record(record: CanonicalRecord) -> list[str]:
    """Return a list of problems. An empty list means the record is valid."""
    problems: list[str] = []
    if not record.country_code:
        problems.append("Missing country code")
    elif not validate_country_code(record.country_code):
        problems.append(f"Invalid country code: {record.country_code}")

    # if not validate_geometry(record.geom):
    #     problems.append(f"Invalid geometry: {record.geom}") 
    return problems














# def validate_geometry(geom: dict | None) -> list[str]:
#     """Return a list of problems with the geometry. An empty list means the geometry is valid."""
#     problems: list[str] = []
#     if geom is None:
#         return problems

#     if not isinstance(geom, dict):
#         problems.append("Geometry must be a dictionary")
#         return problems

#     if "type" not in geom:
#         problems.append("Missing geometry type")
#     elif geom["type"] not in ["Point", "LineString", "Polygon"]:
#         problems.append(f"Invalid geometry type: {geom['type']}")

#     if "coordinates" not in geom:
#         problems.append("Missing geometry coordinates")
#     else:
#         coords = geom["coordinates"]
#         if not isinstance(coords, (list, tuple)):
#             problems.append("Geometry coordinates must be a list or tuple")
#         elif len(coords) == 0:
#             problems.append("Geometry coordinates cannot be empty")

#     return problems











