from fastapi.testclient import TestClient

from shortz_ai import server


def test_reframe_returns_both_camera_paths(monkeypatch):
    paths = {"track": [{"t": 0, "x": 0.5, "cut": False}], "smart_track": []}
    monkeypatch.setattr(server, "analyze_clip", lambda path, aspect: paths)
    response = TestClient(server.app).post(
        "/reframe", files={"video": ("clip.mp4", b"fake", "video/mp4")}, data={"source_aspect": "1.7778"}
    )
    assert response.status_code == 200
    assert response.json() == paths
