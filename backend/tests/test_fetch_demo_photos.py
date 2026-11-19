import json

import pytest

from fetch_demo_photos import clean_text, is_allowed_license, pick, run, slugify


@pytest.mark.parametrize("name,ok", [
    ("CC BY-SA 4.0", True), ("CC BY 2.0", True), ("CC0", True), ("CC0 1.0", True),
    ("Public domain", True), ("PD-old-70", True),
    ("CC BY-NC 2.0", False), ("CC BY-ND 4.0", False), ("CC BY-NC-SA 3.0", False),
    ("GFDL", False), ("Copyrighted free use", False), ("", False),
])
def test_license_filter(name, ok):
    assert is_allowed_license(name) is ok


def test_clean_text_strips_html_and_pipes():
    assert clean_text('<a href="x">Jane &amp; Co</a> | <b>Photo</b>') == "Jane & Co / Photo"


def test_slugify():
    assert slugify("File name (1) – owl.JPG") == "File_name_1_owl.jpg"


def page(title, width=2000, mime="image/jpeg", lic="CC BY-SA 4.0", artist="<b>Ann</b>", restrictions="", index=1):
    meta = {"LicenseShortName": {"value": lic}, "Artist": {"value": artist}}
    if restrictions:
        meta["Restrictions"] = {"value": restrictions}
    return {"title": f"File:{title}", "index": index, "imageinfo": [{
        "mime": mime, "width": width, "url": f"https://x/{title}", "thumburl": f"https://x/t/{title}",
        "descriptionurl": f"https://commons/{title}", "extmetadata": meta}]}


def test_pick_applies_all_filters():
    pages = [
        page("small.jpg", width=500),
        page("png.png", mime="image/png"),
        page("nc.jpg", lic="CC BY-NC 2.0"),
        page("restricted.jpg", restrictions="personality"),
        page("noauthor.jpg", artist=""),
        page("good1.jpg"),
        page("good2.jpg", lic="CC0", artist=""),
        page("good3.jpg"),
    ]
    got = pick(pages, 2, set())
    assert [g["title"] for g in got] == ["good1.jpg", "good2.jpg"]
    assert got[0]["author"] == "Ann" and got[1]["author"] == "Unknown"


class FakeResponse:
    def __init__(self, data=None, content=b"", status=200):
        self._data, self.content, self.status_code = data, content, status

    def json(self):
        return self._data

    def raise_for_status(self):
        assert self.status_code == 200


class FakeSession:
    def __init__(self):
        self.calls = 0

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls += 1
        assert "User-Agent" in headers and "me@example.com" in headers["User-Agent"]
        if params is not None:
            term = params["gsrsearch"].split(" filetype")[0]
            pages = [page(f"{term}_{k}.jpg", index=k) for k in range(3)]
            return FakeResponse({"query": {"pages": pages}})
        return FakeResponse(content=b"fake-jpeg-bytes")


def test_run_downloads_and_writes_credits(tmp_path):
    n = run(tmp_path, "me@example.com", per_term=2, topics={"Birds": ["owl"], "Plants": ["fern"]},
            session=FakeSession(), pause=0)
    assert n == 4
    assert (tmp_path / "Birds" / "owl_0.jpg").read_bytes() == b"fake-jpeg-bytes"
    text = (tmp_path / "ATTRIBUTION.md").read_text(encoding="utf-8")
    assert "| Birds/owl_0.jpg |" in text and "CC BY-SA 4.0" in text
    assert len(json.loads((tmp_path / "credits.json").read_text())) == 4


def test_credits_only_drops_deleted_photos(tmp_path):
    run(tmp_path, "me@example.com", per_term=2, topics={"Birds": ["owl"]}, session=FakeSession(), pause=0)
    (tmp_path / "Birds" / "owl_0.jpg").unlink()
    assert run(tmp_path, "me@example.com", credits_only=True) == 1
    assert "owl_0.jpg" not in (tmp_path / "ATTRIBUTION.md").read_text(encoding="utf-8")


def test_rerun_does_not_duplicate(tmp_path):
    kwargs = dict(per_term=2, topics={"Birds": ["owl"]}, pause=0)
    run(tmp_path, "me@example.com", session=FakeSession(), **kwargs)
    second = FakeSession()
    assert run(tmp_path, "me@example.com", session=second, **kwargs) == 2
    assert second.calls == 0   # nothing was searched or downloaded again
