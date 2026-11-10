from fastapi.testclient import TestClient

from future_radio_os.app import create_app


def test_health_returns_structured_service_status():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "future-radio-os",
        "version": "0.1.0",
    }


def test_readiness_returns_structured_dependency_status():
    client = TestClient(create_app())

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "future-radio-os",
        "checks": {"configuration": "ok", "storage": "not_configured"},
    }
