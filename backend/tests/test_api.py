from fastapi.testclient import TestClient

from photosearch.api import create_app


def client(store, encode):
    return TestClient(create_app(store, encode))


def test_search_ranks_best_match_first(store, encode):
    data = client(store, encode).get("/api/search", params={"q": "owl", "hide_duplicates": False}).json()
    assert data["total"] == 5
    assert [r["id"] for r in data["results"]][:3] == [0, 1, 4]


def test_hiding_duplicates_removes_copies_and_reports_them(store, encode):
    data = client(store, encode).get("/api/search", params={"q": "owl"}).json()
    ids = [r["id"] for r in data["results"]]
    assert data["total"] == 4 and 1 not in ids
    first = data["results"][0]
    assert first["copies"] == 1
    assert first["also_found"] == ["Demo/Birds/owl1_copy.jpg"]
    assert first["path"] == "Demo/Birds/owl1.jpg"
    assert first["thumb_url"] == "/thumbs/t0.jpg"


def test_pagination(store, encode):
    c = client(store, encode)
    page1 = c.get("/api/search", params={"q": "owl", "limit": 2}).json()
    page2 = c.get("/api/search", params={"q": "owl", "limit": 2, "offset": 2}).json()
    assert len(page1["results"]) == 2 and len(page2["results"]) == 2
    assert not {r["id"] for r in page1["results"]} & {r["id"] for r in page2["results"]}


def test_empty_query_is_rejected(store, encode):
    assert client(store, encode).get("/api/search", params={"q": "   "}).status_code == 422


def test_info(store, encode):
    assert client(store, encode).get("/api/info").json() == {"count": 5, "root_name": "Demo"}
