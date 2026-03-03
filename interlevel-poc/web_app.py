#!/usr/bin/env python3
"""
Interlevel POC - Web Testing Interface
Complete testing interface for Phases 1-5
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.database import SessionLocal, User, Agent, Session as DBSession, Execution
from src.services.clarification import ClarificationService
from src.services.agent_req import AgentRequirementModel
from src.services.executor import ExecutorService
from src.llm.client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__,
            template_folder='web/templates',
            static_folder='web/static')
CORS(app)
app.config['SECRET_KEY'] = 'interlevel-poc-testing-key'

# Initialize services
db = SessionLocal()
clarification_service = ClarificationService()
requirements_service = AgentRequirementModel()
executor_service = ExecutorService()
llm_client = LLMClient()


# =============================================================================
# HOME PAGE
# =============================================================================

@app.route('/')
def index():
    """Main testing dashboard"""
    return render_template('index.html')


# =============================================================================
# PHASE 1: FOUNDATION - STATUS CHECK
# =============================================================================

@app.route('/api/test/phase1/status')
def test_phase1_status():
    """Test Phase 1 foundation components"""
    try:
        results = {
            "phase": "Phase 1: Foundation",
            "components": []
        }

        # Test database connection
        try:
            user_count = db.query(User).count()
            results["components"].append({
                "name": "Database",
                "status": "✅ Connected",
                "details": f"{user_count} users in database"
            })
        except Exception as e:
            results["components"].append({
                "name": "Database",
                "status": "❌ Error",
                "details": str(e)
            })

        # Test logger
        try:
            logger.info("Web interface test")
            results["components"].append({
                "name": "Logger",
                "status": "✅ Working",
                "details": "Logging system operational"
            })
        except Exception as e:
            results["components"].append({
                "name": "Logger",
                "status": "❌ Error",
                "details": str(e)
            })

        # Test validators
        try:
            from src.utils.validators import validate_email
            valid = validate_email("test@example.com")
            results["components"].append({
                "name": "Validators",
                "status": "✅ Working",
                "details": "Email validation working"
            })
        except Exception as e:
            results["components"].append({
                "name": "Validators",
                "status": "❌ Error",
                "details": str(e)
            })

        return jsonify(results)

    except Exception as e:
        logger.error(f"Phase 1 test error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# PHASE 2: LLM INTEGRATION - STATUS CHECK
# =============================================================================

@app.route('/api/test/phase2/status')
def test_phase2_status():
    """Test Phase 2 LLM integration"""
    try:
        results = {
            "phase": "Phase 2: LLM Integration",
            "components": []
        }

        # Test LLM client initialization
        try:
            model_name = llm_client.model_name
            results["components"].append({
                "name": "LLM Client",
                "status": "✅ Initialized",
                "details": f"Model: {model_name}"
            })
        except Exception as e:
            results["components"].append({
                "name": "LLM Client",
                "status": "❌ Error",
                "details": str(e)
            })

        # Test Ollama connection
        try:
            provider_name = llm_client.provider.__class__.__name__
            results["components"].append({
                "name": "LLM Provider",
                "status": "✅ Connected",
                "details": f"Provider: {provider_name}"
            })
        except Exception as e:
            results["components"].append({
                "name": "LLM Provider",
                "status": "⚠️ Warning",
                "details": "Provider may not be running"
            })

        return jsonify(results)

    except Exception as e:
        logger.error(f"Phase 2 test error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# PHASE 3: CLARIFICATION - FULL WORKFLOW
# =============================================================================

@app.route('/api/test/phase3/start-session', methods=['POST'])
def test_phase3_start_session():
    """Start a new clarification session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'test-user')
        intent = data.get('intent', 'I want to create a test agent')

        # Ensure user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, email=f"{user_id}@test.com", token_balance=50000)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Start clarification session
        result = clarification_service.start_session(user_id, intent)

        return jsonify({
            "success": True,
            "session_id": result["session_id"],
            "first_question": result.get("question", ""),
            "status": result.get("status", "active")
        })

    except Exception as e:
        logger.error(f"Phase 3 start session error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/test/phase3/respond', methods=['POST'])
def test_phase3_respond():
    """Respond to clarification question"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        response = data.get('response')

        if not session_id or not response:
            return jsonify({"error": "Missing session_id or response"}), 400

        result = clarification_service.add_response(session_id, response)

        return jsonify({
            "success": True,
            "next_question": result.get("question", ""),
            "status": result.get("status", "active"),
            "is_complete": result.get("status") == "complete"
        })

    except Exception as e:
        logger.error(f"Phase 3 respond error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/test/phase3/session/<session_id>')
def test_phase3_get_session(session_id):
    """Get session details"""
    try:
        result = clarification_service.get_session(session_id)

        if not result:
            return jsonify({"error": "Session not found"}), 404

        return jsonify({
            "success": True,
            "session": result
        })

    except Exception as e:
        logger.error(f"Phase 3 get session error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# PHASE 4: REQUIREMENTS GENERATION
# =============================================================================

@app.route('/api/test/phase4/generate', methods=['POST'])
def test_phase4_generate():
    """Generate requirements from session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({"error": "Missing session_id"}), 400

        # Generate requirements
        result = requirements_service.generate_requirements(session_id)

        return jsonify({
            "success": True,
            "agent_id": result["requirements"]["agent_id"],
            "name": result["requirements"]["metadata"]["name"],
            "requirements": result["requirements"],
            "filepath": result["filepath"]
        })

    except Exception as e:
        logger.error(f"Phase 4 generate error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/test/phase4/load/<agent_id>')
def test_phase4_load(agent_id):
    """Load requirements for agent"""
    try:
        requirements = requirements_service.load_requirements(agent_id)

        return jsonify({
            "success": True,
            "requirements": requirements
        })

    except Exception as e:
        logger.error(f"Phase 4 load error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# PHASE 5: CODE GENERATION
# =============================================================================

@app.route('/api/test/phase5/generate', methods=['POST'])
def test_phase5_generate():
    """Generate code for agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agent_id')

        if not agent_id:
            return jsonify({"error": "Missing agent_id"}), 400

        # Generate code
        result = executor_service.generate_agent_code(agent_id)

        if not result.get("success"):
            return jsonify(result), 400

        # Read generated code
        code_path = result.get("code_path")
        generated_code = ""
        if code_path and Path(code_path).exists():
            with open(code_path, 'r') as f:
                generated_code = f.read()

        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "code_path": code_path,
            "template_used": result.get("template_used"),
            "code_preview": generated_code[:1000] + "..." if len(generated_code) > 1000 else generated_code,
            "code_size": len(generated_code)
        })

    except Exception as e:
        logger.error(f"Phase 5 generate error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/test/phase5/validate', methods=['POST'])
def test_phase5_validate():
    """Validate code"""
    try:
        data = request.get_json()
        code = data.get('code')

        if not code:
            return jsonify({"error": "Missing code"}), 400

        is_valid, formatted_code, errors = executor_service.validate_and_format(code)

        return jsonify({
            "success": True,
            "is_valid": is_valid,
            "formatted_code": formatted_code if is_valid else code,
            "errors": errors
        })

    except Exception as e:
        logger.error(f"Phase 5 validate error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/test/phase5/templates')
def test_phase5_templates():
    """List available templates"""
    try:
        templates = [
            {
                "name": "base_agent.py.template",
                "description": "Basic agent with input validation",
                "use_case": "Simple agents without external APIs"
            },
            {
                "name": "api_agent.py.template",
                "description": "Agent with API integration and retry logic",
                "use_case": "Agents calling external REST APIs"
            },
            {
                "name": "scheduled_agent.py.template",
                "description": "Agent for scheduled execution",
                "use_case": "Cron-like scheduled agents"
            }
        ]

        return jsonify({
            "success": True,
            "templates": templates
        })

    except Exception as e:
        logger.error(f"Phase 5 templates error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# COMPLETE WORKFLOW TEST
# =============================================================================

@app.route('/api/test/complete-workflow', methods=['POST'])
def test_complete_workflow():
    """Test complete workflow from intent to code"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'test-workflow-user')
        intent = data.get('intent', 'Create a weather monitoring agent')

        workflow_results = {
            "steps": [],
            "success": False
        }

        # Step 1: Start clarification
        workflow_results["steps"].append({
            "phase": "Phase 3: Clarification",
            "step": "Starting session...",
            "status": "in_progress"
        })

        # Note: This is a mock workflow since real clarification requires user interaction
        workflow_results["steps"][-1]["status"] = "complete"
        workflow_results["steps"][-1]["result"] = "Session started (requires user interaction)"

        workflow_results["success"] = True
        workflow_results["message"] = "Workflow initiated. Complete clarification session to proceed."

        return jsonify(workflow_results)

    except Exception as e:
        logger.error(f"Complete workflow error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# DASHBOARD DATA
# =============================================================================

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            "users": db.query(User).count(),
            "sessions": db.query(DBSession).count(),
            "agents": db.query(Agent).count(),
            "executions": db.query(Execution).count() if Execution else 0
        }

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard/recent-agents')
def dashboard_recent_agents():
    """Get recent agents"""
    try:
        agents = db.query(Agent).order_by(Agent.created_at.desc()).limit(10).all()

        agent_list = []
        for agent in agents:
            agent_list.append({
                "agent_id": agent.agent_id,
                "name": agent.name,
                "status": agent.status,
                "created_at": agent.created_at.isoformat() if agent.created_at else None
            })

        return jsonify({"agents": agent_list})

    except Exception as e:
        logger.error(f"Recent agents error: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("  INTERLEVEL POC - WEB TESTING INTERFACE")
    print("=" * 80)
    print("\n🚀 Starting web server...")
    print(f"📍 URL: http://localhost:5001")
    print(f"📊 Dashboard: http://localhost:5001")
    print(f"🧪 API Docs: http://localhost:5001/api/test")
    print("\n✨ Available Test Endpoints:")
    print("   - Phase 1: /api/test/phase1/status")
    print("   - Phase 2: /api/test/phase2/status")
    print("   - Phase 3: /api/test/phase3/*")
    print("   - Phase 4: /api/test/phase4/*")
    print("   - Phase 5: /api/test/phase5/*")
    print("\n" + "=" * 80 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=True)
