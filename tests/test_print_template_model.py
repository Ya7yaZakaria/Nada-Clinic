from app import create_app
from app.extensions import db
from app.models.print_template import PrintTemplate


def make_app():
    app = create_app("testing")
    app.config.update(SERVER_NAME="localhost")
    return app


def test_print_template_model_supports_prescription_document_type():
    app = make_app()

    with app.app_context():
        db.create_all()

        template = PrintTemplate(
            name="Small Rx",
            document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            paper_width_mm=105,
            paper_height_mm=148,
            layout_json={"patient_name": {"x": 10, "y": 20}},
            is_default=True,
        )
        db.session.add(template)
        db.session.commit()

        assert template.id is not None
        assert template.uuid
        assert template.document_type == "prescription"
        assert template.layout_json["patient_name"]["x"] == 10
        assert template.paper_width_mm == 105

        db.drop_all()


def test_print_template_model_supports_investigation_request_document_type():
    app = make_app()

    with app.app_context():
        db.create_all()

        template = PrintTemplate(
            name="Investigation Rx Paper",
            document_type=PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
            paper_width_mm=148,
            paper_height_mm=210,
            layout_json={"investigation_items": {"x": 25, "y": 65}},
        )
        db.session.add(template)
        db.session.commit()

        assert template.id is not None
        assert template.document_type == "investigation_request"
        assert template.layout_json["investigation_items"]["y"] == 65

        db.drop_all()


def test_print_template_model_allows_same_name_for_different_document_types():
    app = make_app()

    with app.app_context():
        db.create_all()

        prescription_template = PrintTemplate(
            name="Nada Small Paper",
            document_type=PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION,
            layout_json={},
        )
        investigation_template = PrintTemplate(
            name="Nada Small Paper",
            document_type=PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST,
            layout_json={},
        )

        db.session.add(prescription_template)
        db.session.add(investigation_template)
        db.session.commit()

        assert prescription_template.id != investigation_template.id

        db.drop_all()
