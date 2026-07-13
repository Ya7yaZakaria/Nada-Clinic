from copy import deepcopy

from app.extensions import db
from app.models.print_template import PrintTemplate


class PrintTemplateService:
    """Service layer for reusable print layout templates."""

    DEFAULT_PAPER_WIDTH_MM = 148.0
    DEFAULT_PAPER_HEIGHT_MM = 210.0

    DEFAULT_LAYOUTS = {
        PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION: {
            "patient_name": {
                "label": "Patient Name",
                "x": 12,
                "y": 18,
                "width": 55,
                "height": 8,
                "fontSize": 14,
                "visible": True,
            },
            "mrn": {
                "label": "MRN",
                "x": 72,
                "y": 18,
                "width": 32,
                "height": 8,
                "fontSize": 14,
                "visible": True,
            },
            "date": {
                "label": "Date",
                "x": 112,
                "y": 18,
                "width": 30,
                "height": 8,
                "fontSize": 14,
                "visible": True,
            },
            "prescription_items": {
                "label": "Prescription Items",
                "x": 18,
                "y": 45,
                "width": 115,
                "height": 120,
                "fontSize": 15,
                "lineHeight": 9,
                "visible": True,
            },
        },
        PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST: {
            "patient_name": {
                "label": "Patient Name",
                "x": 12,
                "y": 18,
                "width": 55,
                "height": 8,
                "fontSize": 14,
                "visible": True,
            },
            "mrn": {
                "label": "MRN",
                "x": 72,
                "y": 18,
                "width": 32,
                "height": 8,
                "fontSize": 14,
                "visible": True,
            },
            "date": {
                "label": "Date",
                "x": 112,
                "y": 18,
                "width": 30,
                "height": 8,
                "fontSize": 14,
                "visible": True,
            },
            "instruction": {
                "label": "Instruction",
                "x": 22,
                "y": 42,
                "width": 100,
                "height": 10,
                "fontSize": 16,
                "visible": True,
                "defaultText": "ثاني أيام الدورة",
            },
            "investigation_items": {
                "label": "Investigation Items",
                "x": 28,
                "y": 62,
                "width": 90,
                "height": 110,
                "fontSize": 18,
                "lineHeight": 10,
                "visible": True,
            },
        },
    }

    DEFAULT_TEMPLATE_NAMES = {
        PrintTemplate.DOCUMENT_TYPE_PRESCRIPTION: "Default Prescription Layout",
        PrintTemplate.DOCUMENT_TYPE_INVESTIGATION_REQUEST: "Default Investigation Request Layout",
    }

    @staticmethod
    def _clean(value):
        return (value or "").strip()

    @classmethod
    def _require_text(cls, value, message):
        cleaned = cls._clean(value)
        if not cleaned:
            raise ValueError(message)
        return cleaned

    @classmethod
    def validate_document_type(cls, document_type):
        cleaned = cls._require_text(document_type, "Document type is required")
        if not PrintTemplate.is_supported_document_type(cleaned):
            raise ValueError(f"Unsupported print document type: {cleaned}")
        return cleaned

    @staticmethod
    def validate_paper_size(width_mm, height_mm):
        try:
            width = float(width_mm)
            height = float(height_mm)
        except (TypeError, ValueError):
            raise ValueError("Paper size must be numeric") from None

        if width <= 0 or height <= 0:
            raise ValueError("Paper size must be positive")

        if width > 1000 or height > 1000:
            raise ValueError("Paper size is too large")

        return width, height

    @staticmethod
    def validate_layout(layout_json):
        if layout_json is None:
            return {}

        if not isinstance(layout_json, dict):
            raise ValueError("Layout must be a JSON object")

        return deepcopy(layout_json)

    @staticmethod
    def _validate_template(template):
        if not template:
            raise ValueError("Print template is required")

        if not isinstance(template, PrintTemplate):
            raise ValueError("Invalid print template")

    @classmethod
    def _ensure_unique_name(cls, *, document_type, name, template_id=None):
        existing = PrintTemplate.query.filter_by(
            document_type=document_type,
            name=name,
        ).first()

        if existing and existing.id != template_id:
            raise ValueError("Print template name already exists for this document type")

    @classmethod
    def default_layout_for(cls, document_type):
        document_type = cls.validate_document_type(document_type)
        return deepcopy(cls.DEFAULT_LAYOUTS[document_type])

    @classmethod
    def create_template(
        cls,
        *,
        document_type,
        name,
        paper_width_mm=None,
        paper_height_mm=None,
        layout_json=None,
        is_default=False,
        actor_user=None,
    ):
        document_type = cls.validate_document_type(document_type)
        cleaned_name = cls._require_text(name, "Print template name is required")
        cls._ensure_unique_name(document_type=document_type, name=cleaned_name)

        width, height = cls.validate_paper_size(
            paper_width_mm if paper_width_mm is not None else cls.DEFAULT_PAPER_WIDTH_MM,
            paper_height_mm if paper_height_mm is not None else cls.DEFAULT_PAPER_HEIGHT_MM,
        )

        layout = (
            cls.validate_layout(layout_json)
            if layout_json is not None
            else cls.default_layout_for(document_type)
        )

        if is_default:
            cls.clear_default(document_type)

        template = PrintTemplate(
            document_type=document_type,
            name=cleaned_name,
            paper_width_mm=width,
            paper_height_mm=height,
            layout_json=layout,
            is_default=bool(is_default),
            created_by_user=actor_user,
            updated_by_user=actor_user,
        )

        db.session.add(template)
        db.session.commit()
        return template

    @classmethod
    def update_template(
        cls,
        template,
        *,
        name=None,
        paper_width_mm=None,
        paper_height_mm=None,
        layout_json=None,
        is_default=None,
        is_active=None,
        actor_user=None,
    ):
        cls._validate_template(template)

        if name is not None:
            cleaned_name = cls._require_text(name, "Print template name is required")
            cls._ensure_unique_name(
                document_type=template.document_type,
                name=cleaned_name,
                template_id=template.id,
            )
            template.name = cleaned_name

        if paper_width_mm is not None or paper_height_mm is not None:
            width, height = cls.validate_paper_size(
                paper_width_mm if paper_width_mm is not None else template.paper_width_mm,
                paper_height_mm if paper_height_mm is not None else template.paper_height_mm,
            )
            template.paper_width_mm = width
            template.paper_height_mm = height

        if layout_json is not None:
            template.layout_json = cls.validate_layout(layout_json)

        if is_active is not None:
            template.is_active = bool(is_active)

        if is_default is not None:
            if is_default:
                cls.clear_default(template.document_type, exclude_template_id=template.id)
            template.is_default = bool(is_default)

        if actor_user is not None:
            template.updated_by_user = actor_user

        db.session.commit()
        return template

    @staticmethod
    def get_template_by_uuid(template_uuid):
        if not template_uuid:
            return None

        return PrintTemplate.query.filter_by(uuid=template_uuid).first()

    @classmethod
    def list_active_templates(cls, document_type=None):
        query = PrintTemplate.query.filter_by(is_active=True)

        if document_type:
            query = query.filter_by(document_type=cls.validate_document_type(document_type))

        return query.order_by(
            PrintTemplate.document_type.asc(),
            PrintTemplate.is_default.desc(),
            PrintTemplate.name.asc(),
            PrintTemplate.id.asc(),
        ).all()

    @classmethod
    def list_all_templates(cls, document_type=None):
        query = PrintTemplate.query

        if document_type:
            query = query.filter_by(document_type=cls.validate_document_type(document_type))

        return query.order_by(
            PrintTemplate.document_type.asc(),
            PrintTemplate.is_active.desc(),
            PrintTemplate.is_default.desc(),
            PrintTemplate.name.asc(),
            PrintTemplate.id.asc(),
        ).all()

    @classmethod
    def clear_default(cls, document_type, exclude_template_id=None):
        document_type = cls.validate_document_type(document_type)

        query = PrintTemplate.query.filter_by(
            document_type=document_type,
            is_default=True,
        )

        if exclude_template_id:
            query = query.filter(PrintTemplate.id != exclude_template_id)

        for template in query.all():
            template.is_default = False

        db.session.flush()

    @classmethod
    def get_default_template(cls, document_type):
        document_type = cls.validate_document_type(document_type)

        return (
            PrintTemplate.query.filter_by(
                document_type=document_type,
                is_active=True,
                is_default=True,
            )
            .order_by(PrintTemplate.id.asc())
            .first()
        )

    @classmethod
    def get_or_create_default_template(cls, document_type, actor_user=None):
        document_type = cls.validate_document_type(document_type)

        existing = cls.get_default_template(document_type)
        if existing:
            return existing

        fallback = (
            PrintTemplate.query.filter_by(
                document_type=document_type,
                name=cls.DEFAULT_TEMPLATE_NAMES[document_type],
            )
            .first()
        )

        if fallback:
            return cls.update_template(
                fallback,
                is_active=True,
                is_default=True,
                actor_user=actor_user,
            )

        return cls.create_template(
            document_type=document_type,
            name=cls.DEFAULT_TEMPLATE_NAMES[document_type],
            layout_json=cls.default_layout_for(document_type),
            is_default=True,
            actor_user=actor_user,
        )

    @classmethod
    def ensure_default_templates(cls, actor_user=None):
        return {
            document_type: cls.get_or_create_default_template(
                document_type,
                actor_user=actor_user,
            )
            for document_type in PrintTemplate.SUPPORTED_DOCUMENT_TYPES
        }

    @classmethod
    def deactivate_template(cls, template, *, actor_user=None):
        return cls.update_template(
            template,
            is_active=False,
            is_default=False,
            actor_user=actor_user,
        )

    @classmethod
    def reactivate_template(cls, template, *, actor_user=None):
        return cls.update_template(
            template,
            is_active=True,
            actor_user=actor_user,
        )
