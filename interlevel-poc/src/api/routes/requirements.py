"""
Requirements API endpoints
Handles agent requirement generation from clarification sessions
"""
from flask import Blueprint, request, jsonify
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.services.agent_req import AgentRequirementModel
from src.utils.logger import get_logger

logger = get_logger(__name__)

bp = Blueprint("requirements", __name__, url_prefix="/requirements")
req_model = AgentRequirementModel()


@bp.route("/generate", methods=["POST"])
def generate_requirements():
    """
    Generate requirements from a completed clarification session

    Expected JSON body:
    {
        "session_id": "session_uuid",
        "user_id": "user_uuid"  # optional, used for agent record creation
    }

    Returns:
        {
            "success": true,
            "requirements": {...},
            "agent_id": "...",
            "filepath": "...",
            "warnings": [...]
        }
    """
    try:
        data = request.get_json()

        if not data or "session_id" not in data:
            return jsonify({
                "error": "Missing required field: session_id"
            }), 400

        session_id = data["session_id"]
        user_id = data.get("user_id")

        logger.info(f"Generating requirements for session {session_id}")

        # Generate requirements
        result = req_model.generate_requirements(session_id)

        response_data = {
            "success": True,
            "session_id": session_id,
            "agent_id": result["requirements"].get("agent_id"),
            "name": result["requirements"].get("metadata", {}).get("name"),
            "filepath": result["filepath"],
            "warnings": result["warnings"]
        }

        # Optionally create agent record
        if user_id:
            try:
                agent = req_model.create_agent_record(result["requirements"], user_id)
                response_data["agent_record_created"] = True
                response_data["user_id"] = user_id
                logger.info(f"Agent record created: {agent.agent_id}")
            except Exception as e:
                logger.warning(f"Failed to create agent record: {e}")
                response_data["agent_record_created"] = False
                response_data["agent_record_error"] = str(e)

        return jsonify(response_data), 201

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating requirements: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/load/<agent_id>", methods=["GET"])
def load_requirements(agent_id):
    """
    Load a previously generated requirements file

    Returns:
        {
            "success": true,
            "requirements": {...}
        }
    """
    try:
        logger.info(f"Loading requirements for agent {agent_id}")

        requirements = req_model.load_requirements(agent_id)

        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "requirements": requirements
        }), 200

    except FileNotFoundError as e:
        logger.warning(f"Requirements not found: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error loading requirements: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/validate", methods=["POST"])
def validate_requirements():
    """
    Validate a requirements JSON structure

    Expected JSON body:
    {
        "requirements": {...}
    }

    Returns:
        {
            "is_valid": true/false,
            "errors": [...],
            "warnings": [...]
        }
    """
    try:
        data = request.get_json()

        if not data or "requirements" not in data:
            return jsonify({
                "error": "Missing required field: requirements"
            }), 400

        requirements = data["requirements"]

        logger.info("Validating requirements")

        # Validate
        from src.utils.validators import validate_requirements_json
        result = validate_requirements_json(requirements)

        return jsonify({
            "is_valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings
        }), 200

    except Exception as e:
        logger.error(f"Error validating requirements: {e}")
        return jsonify({"error": str(e)}), 500
