from fastapi.testclient import TestClient

from main import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200, health.text
    assert health.json()["status"] == "ok"

    models = client.get("/models")
    assert models.status_code == 200, models.text
    assert "available" in models.json()
    assert "configured" in models.json()

    stats = client.get("/stats")
    assert stats.status_code == 200, stats.text
    assert stats.json()["total_calls"] == 0

    print("Smoke test passed: app imports and safe endpoints work.")


if __name__ == "__main__":
    main()
