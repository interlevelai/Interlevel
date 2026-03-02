"""
Clarification API endpoints
Handles agent requirement gathering through conversation
"""
from flask import Blueprint, request, jsonify
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.services.clarification import ClarificationService
from src.utils.logger import get_logger

logger = get_logger(__name__)

bp = Blueprint("clarification", __name__, url_prefix="/clarification")
clarification_service = ClarificationService()


@bp.route("/session", methods=["POST"])
def start_session():
    """
    Start a new clarification session

    Expected JSON body:
    {
        "user_id": "user_123",
        "intent": "I want an agent that fetches weather data"
    }

    Returns:
        {
            "session_id": "...",
            "question": "...",
            "conversation": [...]
        }
    """
    try:
        data = request.get_json()

        if not data or "user_id" not in data or "intent" not in data:
            return jsonify({
                "error": "Missing required fields: user_id, intent"
            }), 400

        user_id = data["user_id"]
        intent = data["intent"]

        logger.info(f"Starting clarification session for user {user_id}")

        result = clarification_service.start_session(user_id, intent)

        return jsonify(result), 201

    except Exception as e:
        logger.error(f"Error starting session: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/session/<session_id>/response", methods=["POST"])
def add_response(session_id):
    """
    Add a user response to an ongoing clarification session

    Expected JSON body:
    {
        "response": "The agent should fetch weather for a given city"
    }

    Returns:
        {
            "session_id": "...",
            "status": "active" | "complete",
            "question": "...",  // if active
            "summary": "...",   // if complete
            "conversation": [...]
        }
    """
    try:
        data = request.get_json()

        if not data or "response" not in data:
            return jsonify({
                "error": "Missing required field: response"
            }), 400

        response = data["response"]

        logger.info(f"Processing response for session {session_id}")

        result = clarification_service.add_response(session_id, response)

        return jsonify(result), 200

    except ValueError as e:
        logger.warning(f"Invalid session: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error processing response: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    """
    Retrieve a clarification session by ID

    Returns:
        {
            "session_id": "...",
            "user_id": "...",
            "status": "active" | "complete" | "abandoned",
            "conversation": [...],
            "created_at": "...",
            "expires_at": "..."
        }
    """
    try:
        logger.info(f"Retrieving session {session_id}")

        result = clarification_service.get_session(session_id)

        if not result:
            return jsonify({"error": "Session not found"}), 404

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        return jsonify({"error": str(e)}), 500
