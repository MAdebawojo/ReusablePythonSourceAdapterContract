def validate_geom(geom: dict | None) -> list[str]:
    """Return a list of problems with the geometry. Empty list means valid.

    None is valid (source has no geometry). If present, geom must be a
    dict with 'type' and 'coordinates'. Point geometries are validated
    strictly: exactly two numeric coordinates, longitude in [-180, 180],
    latitude in [-90, 90]. LineString and Polygon are only checked
    structurally (valid type, coordinates present), since no current
    adapter produces them; a production version would add per-type
    coordinate validation as new geometry-bearing sources are added.
    """
    problems: list[str] = []

    if geom is None:
        return problems

    if not isinstance(geom, dict):
        problems.append("Geometry must be a dictionary")
        return problems

    geom_type = geom.get("type")
    if geom_type is None:
        problems.append("Missing geometry type")
    elif geom_type not in ("Point", "LineString", "Polygon"):
        problems.append(f"Invalid geometry type: {geom_type}")

    coords = geom.get("coordinates")
    if coords is None:
        problems.append("Missing geometry coordinates")
        return problems

    if not isinstance(coords, (list, tuple)):
        problems.append("Geometry coordinates must be a list or tuple")
        return problems

    if geom_type == "Point":
        if len(coords) != 2:
            problems.append(f"Point coordinates must have exactly 2 values, got {len(coords)}")
        else:
            lon, lat = coords[0], coords[1]
            if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
                problems.append(f"Point coordinates must be numeric, got {coords!r}")
            else:
                if not (-180 <= lon <= 180):
                    problems.append(f"Longitude out of range: {lon}")
                if not (-90 <= lat <= 90):
                    problems.append(f"Latitude out of range: {lat}")
    elif geom_type in ("LineString", "Polygon"):
        if len(coords) == 0:
            problems.append(f"{geom_type} coordinates cannot be empty")

    return problems

def normalize_geometry(lat, lon) -> dict:
    """Return a GeoJSON Point geometry dictionary.

    Raises ValueError if lat/lon cannot be converted to floats.
    """
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid coordinates: lat={lat!r}, lon={lon!r}") from e
    return {"type": "Point", "coordinates": [lon_f, lat_f]}


# my normalize geometry only ever produces Point however the validate recognizes the other types as well. I think this is fine since we may want to support other types in the future.