from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, client=("192.0.2.10", 50000))


def test_root_returns_client_ip() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"ip": "192.0.2.10"}


def test_forwarded_for_is_ignored() -> None:
    response = client.get("/", headers={"X-Forwarded-For": "203.0.113.10"})

    assert response.status_code == 200
    assert response.json() == {"ip": "192.0.2.10"}


def test_root_supports_ipv6() -> None:
    ipv6_client = TestClient(app, client=("2001:db8::10", 50000))

    response = ipv6_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"ip": "2001:db8::10"}


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
