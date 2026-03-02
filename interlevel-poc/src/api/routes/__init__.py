from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/status", methods=["GET"])
def status():
    return {"status": "ok"}, 200


# Import and register sub-blueprints
from src.api.routes.clarification import bp as clarification_bp

bp.register_blueprint(clarification_bp)
