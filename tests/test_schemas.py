from app.schemas.poi import AttractionList

def test_attractionlist_schema():
    data = {
        "id": 1,
        "name": "Test Place",
        "description": "Just a test",
        "tags": "tourism : museum",
        "structure_type": "POINT",
        "lat": 55.0,
        "lon": -3.0,
        "distance_m": 120.5,
    }
    obj = AttractionList(**data)
    assert obj.id == 1
    assert obj.name == "Test Place"
    assert obj.tags == "tourism : museum"
    assert obj.structure_type == "POINT"
    assert obj.lat == 55.0
    assert obj.distance_m == 120.5

def test_attractionlist_missing_optionals():
    obj = AttractionList(id=2, structure_type="POLYGON")
    assert obj.lat is None
    assert obj.lon is None
