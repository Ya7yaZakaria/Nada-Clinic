from app import create_app


def test_health_endpoint_returns_ok():
    app = create_app("testing")

    with app.test_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_index_page_renders():
    app = create_app("testing")

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b"Nada Clinic System" in response.data
