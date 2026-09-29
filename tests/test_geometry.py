from iris_ingest.geometry import validate_geom

def test_none_geom_is_valid():
    assert validate_geom(None) == []

def test_point_wrong_coordinate_count_is_rejected():
    geom = {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}
    result = validate_geom(geom)
    assert result != [], f"Expected a problem for wrong coordinate count, got: {result}"

def test_missing_geometry_type_is_rejected():
    geom = {"coordinates": [1.0, 2.0]}  
    result = validate_geom(geom)
    assert result != [], f"Expected a problem for missing geometry type, got: {result}"

def test_unknown_geometry_type_is_rejected():
    geom = {"type": "Blob", "coordinates": [1.0, 2.0]}
    result = validate_geom(geom)
    assert result != [], f"Expected a problem for unknown geometry type, got: {result}"

def test_missing_coordinates_is_rejected():
    geom = {"type": "Point"}  # no "coordinates" key
    result = validate_geom(geom)
    assert result != [], f"Expected a problem for missing coordinates, got: {result}"

def test_valid_point_passes():
    geom = {"type": "Point", "coordinates": [6.7762, 51.2217]}
    result = validate_geom(geom)
    assert result == [], f"Expected no problems for valid point, got: {result}"

def test_longitude_out_of_range_is_rejected():
    geom = {"type": "Point", "coordinates": [200.0, 51.2217]}  # longitude > 180
    result = validate_geom(geom)
    assert result != [], f"Expected a problem for longitude out of range, got: {result}"

def test_latitude_out_of_range_is_rejected():
    geom = {"type": "Point", "coordinates": [6.7762, 95.0]}  # latitude > 90
    result = validate_geom(geom)
    assert result != [], f"Expected a problem for latitude out of range, got: {result}"
