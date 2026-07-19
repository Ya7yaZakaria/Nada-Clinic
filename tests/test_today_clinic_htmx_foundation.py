from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path):
    return (
        ROOT / relative_path
    ).read_text(encoding="utf-8")


def test_base_contains_shared_htmx_targets():
    content = read("app/templates/base.html")

    assert (
        '"clinic/_action_modal_shell.html"'
        in content
    )
    assert (
        '"clinic/_drilldown_drawer.html"'
        in content
    )
    assert (
        '"clinic/_toast_region.html"'
        in content
    )


def test_htmx_shells_have_unique_targets():
    modal = read(
        "app/templates/clinic/"
        "_action_modal_shell.html"
    )
    drawer = read(
        "app/templates/clinic/"
        "_drilldown_drawer.html"
    )
    toast = read(
        "app/templates/clinic/"
        "_toast_region.html"
    )

    assert modal.count(
        'id="clinic-action-modal"'
    ) == 1
    assert modal.count(
        'id="clinic-action-modal-content"'
    ) == 1
    assert drawer.count(
        'id="clinic-drilldown-drawer"'
    ) == 1
    assert drawer.count(
        'id="clinic-drilldown-content"'
    ) == 1
    assert toast.count(
        'id="clinic-toast-region"'
    ) == 1
    assert toast.count(
        'id="clinic-htmx-loading"'
    ) == 1


def test_dynamic_partial_updates_timestamp_oob():
    content = read(
        "app/templates/clinic/"
        "_today_dynamic.html"
    )

    assert (
        "is_htmx_partial"
        in content
    )
    assert (
        'hx-swap-oob="outerHTML"'
        in content
    )
    assert (
        'id="clinic-last-updated"'
        in content
    )


def test_dynamic_route_marks_htmx_partial():
    content = read(
        "app/routes/today_clinic.py"
    )

    assert (
        'context["is_htmx_partial"] = True'
        in content
    )


def test_htmx_javascript_foundation_exists():
    content = read("app/static/js/app.js")

    for marker in [
        "window.clinicShowToast",
        "window.clinicOpenActionModal",
        "window.clinicOpenDrilldown",
        '"htmx:beforeRequest"',
        '"htmx:afterRequest"',
        '"htmx:afterSwap"',
        '"htmx:responseError"',
        '"htmx:sendError"',
        '"clinic:action-success"',
    ]:
        assert marker in content


def test_finance_heading_is_clean():
    content = read(
        "app/templates/clinic/"
        "_today_dynamic.html"
    )

    assert "Today?s" not in content
    assert "Today's financial position" in content


def test_action_success_refreshes_dynamic_clinic():
    javascript = read("app/static/js/app.js")
    dynamic = read(
        "app/templates/clinic/_today_dynamic.html"
    )

    assert '"clinic:action-success"' in javascript
    assert '"clinicSync"' in javascript
    assert "htmx.trigger(" in javascript
    assert (
        'hx-trigger="clinicSync from:body"'
        in dynamic
    )
