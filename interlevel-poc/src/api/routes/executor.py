"""
Executor API endpoints
Handles agent code generation and validation
"""
from flask import Blueprint, request, jsonify
from src.services.executor import ExecutorService
from src.utils.logger import get_logger

logger = get_logger(__name__)
bp = Blueprint("executor", __name__, url_prefix="/api/executor")

# Initialize service
executor_service = ExecutorService()


@bp.route("/generate/<agent_id>", methods=["POST"])
def generate_code(agent_id):
    """
    Generate agent code from requirements

    POST /api/executor/generate/<agent_id>

    Returns:
        {
            "success": true/false,
            "agent_id": "...",
            "code_path": "...",
            "template_used": "...",
            "errors": [] (if not successful)
        }
    """
    try:
        logger.info(f"Generating code for agent {agent_id}")

        result = executor_service.generate_agent_code(agent_id)

        if result.get("success"):
            logger.info(f"Code generation successful for {agent_id}")
            return jsonify(result), 201
        else:
            logger.error(f"Code generation failed for {agent_id}: {result.get('error')}")
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Code generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "success": False}), 500


@bp.route("/validate", methods=["POST"])
def validate_code():
    """
    Validate and format Python code

    POST /api/executor/validate
    Body: {"code": "..."}

    Returns:
        {
            "is_valid": true/false,
            "formatted_code": "...",
            "errors": []
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        code = data.get("code")

        if not code:
            return jsonify({"error": "Missing code field"}), 400

        logger.info("Validating code")

        is_valid, formatted_code, errors = executor_service.validate_and_format(code)

        result = {
            "is_valid": is_valid,
            "formatted_code": formatted_code if is_valid else code,
            "errors": errors
        }

        logger.info(f"Validation complete: is_valid={is_valid}")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e), "is_valid": False}), 500


@bp.route("/templates", methods=["GET"])
def list_templates():
    """
    List available agent templates

    GET /api/executor/templates

    Returns:
        {
            "templates": [
                {
                    "name": "base_agent.py.template",
                    "description": "...",
                    "use_case": "..."
                }
            ]
        }
    """
    templates = [
        {
            "name": "base_agent.py.template",
            "description": "Basic agent with input validation and error handling",
            "use_case": "Simple agents without external API calls"
        },
        {
            "name": "api_agent.py.template",
            "description": "Agent for API integration with retry logic and authentication",
            "use_case": "Agents that call external APIs with retries"
        },
        {
            "name": "scheduled_agent.py.template",
            "description": "Agent for scheduled execution with state management",
            "use_case": "Agents that run on a schedule with execution tracking"
        }
    ]

    logger.info("Returning available templates")
    return jsonify({"templates": templates}), 200


@bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint

    GET /api/executor/health

    Returns:
        {
            "status": "healthy",
            "service": "ExecutorService",
            "templates_available": true,
            "llm_available": true
        }
    """
    try:
        # Check if templates directory exists
        templates_available = executor_service.templates_dir.exists()

        # Check if LLM is available
        llm_available = executor_service.llm is not None

        status = {
            "status": "healthy" if templates_available and llm_available else "degraded",
            "service": "ExecutorService",
            "templates_available": templates_available,
            "llm_available": llm_available
        }

        logger.info(f"Health check: {status['status']}")
        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# Error handlers
@bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    logger.warning(f"Bad request: {error}")
    return jsonify({"error": "Bad request"}), 400


@bp.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    logger.warning(f"Not found: {error}")
    return jsonify({"error": "Endpoint not found"}), 404


@bp.errorhandler(500)
def server_error(error):
    """Handle server errors"""
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500
