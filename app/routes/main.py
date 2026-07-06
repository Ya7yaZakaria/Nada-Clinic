from flask import Blueprint, jsonify, render_template

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    """Clinic foundation home page."""

    return render_template("index.html")


@main_bp.get("/health")
def health():
    """Health check endpoint."""

    return jsonify(
        {
            "status": "ok",
            "service": "Nada Clinic System",
            "stage": "Sprint 0.1 Foundation",
        }
    ), 200
