from flask import Blueprint, jsonify, render_template
from flask_login import login_required

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
@login_required
def index():
    """Clinic dashboard shell."""

    return render_template("index.html")


@main_bp.get("/health")
def health():
    """Health check endpoint."""

    return jsonify(
        {
            "status": "ok",
            "service": "Nada Clinic System",
            "stage": "Stage 1 Auth Foundation",
        }
    ), 200
