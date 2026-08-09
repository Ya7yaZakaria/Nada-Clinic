from tests.factories import read_project_file as read


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


def test_finance_heading_is_clean():
    content = read(
        "app/templates/clinic/"
        "_today_dynamic.html"
    )

    assert "Today?s" not in content
    assert "Today's financial position" in content


