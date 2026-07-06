from pathlib import Path

from app import create_app


def test_pwa_placeholder_files_exist():
    static_dir = Path("app/static")

    assert (static_dir / "manifest.json").exists()
    assert (static_dir / "service-worker.js").exists()


def test_base_template_references_pwa_placeholders():
    app = create_app("testing")

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b"manifest.json" in response.data
    assert b"service-worker.js" in response.data
