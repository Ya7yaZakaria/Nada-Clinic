from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_product_refresh_stylesheet_is_loaded_after_base_styles():
    base = read("app/templates/base.html")

    assert "css/product-refresh.css" in base
    assert base.index("css/app.css") < base.index("css/product-refresh.css")


def test_emergency_modal_has_viewport_safe_scroll_contract():
    template = read(
        "app/templates/clinic/actions/_emergency_form.html"
    )
    styles = read("app/static/css/product-refresh.css")

    assert 'class="clinic-modal-form"' in template
    assert ".clinic-modal-form" in styles
    assert ".emergency-modal-body" in styles
    assert "overflow-y: auto" in styles
    assert "100dvh" in styles


def test_today_clinic_marks_operational_and_secondary_sections():
    template = read("app/templates/clinic/_today_dynamic.html")

    assert "clinic-operational-columns" in template
    assert "clinic-live-finance" in template
    assert "clinic-type-breakdown" in template
