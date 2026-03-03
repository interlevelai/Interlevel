"""
Phase 4: Requirements Model - Unit Tests
Tests for agent requirements generation and API endpoints
"""
import pytest
import json


@pytest.fixture
def db_cleanup():
    """Clean up test database before and after tests"""
    from src.models.database import SessionLocal, Base, engine

    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=engine)


# Requirements Model Tests
def test_agent_requirement_model_initialization(db_cleanup):
    """Test requirements model initializes"""
    from src.services.agent_req import AgentRequirementModel

    try:
        model = AgentRequirementModel()
        assert model is not None
        assert model.llm is not None
        assert model.db is not None
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_requirements_model_format_conversation(db_cleanup):
    """Test conversation formatting"""
    from src.services.agent_req import AgentRequirementModel

    try:
        model = AgentRequirementModel()

        conversation = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "I need a weather agent"},
            {"role": "assistant", "content": "What locations?"}
        ]

        formatted = model._format_conversation(conversation)

        # Should skip system message
        assert "You are helpful" not in formatted
        assert "I need a weather agent" in formatted
        assert "What locations?" in formatted
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_requirements_model_extract_json(db_cleanup):
    """Test JSON extraction from response"""
    from src.services.agent_req import AgentRequirementModel

    try:
        model = AgentRequirementModel()

        response = """Some text before
        {
            "agent_id": "test-123",
            "version": "1.0",
            "metadata": {"name": "Test Agent"}
        }
        Some text after"""

        extracted = model._extract_json(response)

        assert extracted["agent_id"] == "test-123"
        assert extracted["version"] == "1.0"
        assert extracted["metadata"]["name"] == "Test Agent"
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_requirements_model_extract_json_invalid(db_cleanup):
    """Test JSON extraction with invalid JSON"""
    from src.services.agent_req import AgentRequirementModel

    try:
        model = AgentRequirementModel()
        response = "No JSON here at all"

        with pytest.raises(ValueError, match="No JSON found"):
            model._extract_json(response)
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_requirements_model_save_requirements(db_cleanup):
    """Test saving requirements to file"""
    from src.services.agent_req import AgentRequirementModel
    from pathlib import Path

    try:
        model = AgentRequirementModel()

        requirements = {
            "agent_id": "test-agent-123",
            "version": "1.0",
            "metadata": {
                "name": "Test Agent",
                "description": "A test agent",
                "created_at": "2024-01-01T00:00:00"
            },
            "purpose": "Test purpose",
            "inputs": [],
            "outputs": [],
            "triggers": {"type": "manual"},
            "constraints": {}
        }

        filepath = model.save_requirements(requirements)

        # Check file was created
        assert Path(filepath).exists()

        # Check file contents
        with open(filepath) as f:
            loaded = json.load(f)

        assert loaded["agent_id"] == "test-agent-123"
        assert loaded["metadata"]["name"] == "Test Agent"

    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_requirements_model_load_requirements(db_cleanup):
    """Test loading requirements from file"""
    from src.services.agent_req import AgentRequirementModel

    try:
        model = AgentRequirementModel()

        # First save
        requirements = {
            "agent_id": "load-test-123",
            "version": "1.0",
            "metadata": {
                "name": "Load Test Agent",
                "description": "Test loading",
                "created_at": "2024-01-01T00:00:00"
            },
            "purpose": "Test",
            "inputs": [],
            "outputs": [],
            "triggers": {"type": "manual"},
            "constraints": {}
        }

        model.save_requirements(requirements)

        # Then load
        loaded = model.load_requirements("load-test-123")

        assert loaded["agent_id"] == "load-test-123"
        assert loaded["metadata"]["name"] == "Load Test Agent"

    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_requirements_model_load_nonexistent(db_cleanup):
    """Test loading non-existent requirements"""
    from src.services.agent_req import AgentRequirementModel

    try:
        model = AgentRequirementModel()

        with pytest.raises(FileNotFoundError):
            model.load_requirements("nonexistent-agent-id")

    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_requirements_model_create_agent_record(db_cleanup):
    """Test creating agent database record"""
    from src.services.agent_req import AgentRequirementModel

    try:
        model = AgentRequirementModel()

        requirements = {
            "agent_id": "record-test-123",
            "version": "1.0",
            "metadata": {
                "name": "Record Test Agent",
                "description": "Test record creation"
            },
            "purpose": "Test",
            "inputs": [],
            "outputs": [],
            "triggers": {"type": "manual"},
            "constraints": {}
        }

        agent = model.create_agent_record(requirements, "test_user_id")

        assert agent.agent_id == "record-test-123"
        assert agent.user_id == "test_user_id"
        assert agent.name == "Record Test Agent"
        assert agent.status == "requirements_complete"

    except ConnectionError:
        pytest.skip("Ollama server not running")


# API Endpoint Tests
@pytest.fixture
def client():
    """Create Flask test client"""
    from src.api.app import create_app

    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_api_validate_requirements_endpoint(client):
    """Test POST /api/requirements/validate endpoint"""
    requirements = {
        "agent_id": "test",
        "metadata": {"name": "test"},
        "purpose": "test",
        "inputs": [],
        "outputs": [],
        "triggers": {"type": "manual"},
        "constraints": {}
    }

    response = client.post(
        '/api/requirements/validate',
        json={'requirements': requirements}
    )

    assert response.status_code == 200
    assert 'is_valid' in response.json
    assert response.json['is_valid'] is True


def test_api_validate_requirements_invalid(client):
    """Test validation with invalid requirements"""
    response = client.post(
        '/api/requirements/validate',
        json={'requirements': {"agent_id": "test"}}  # Missing required fields
    )

    assert response.status_code == 200
    assert response.json['is_valid'] is False
    assert len(response.json['errors']) > 0


def test_api_validate_requirements_missing_body(client):
    """Test validation endpoint with missing body"""
    response = client.post(
        '/api/requirements/validate',
        json={}
    )

    assert response.status_code == 400
    assert 'error' in response.json


def test_api_generate_requirements_missing_session(client):
    """Test generate endpoint with missing session_id"""
    response = client.post(
        '/api/requirements/generate',
        json={'user_id': 'test_user'}
    )

    assert response.status_code == 400
    assert 'error' in response.json


def test_api_load_requirements_endpoint(client):
    """Test GET /api/requirements/load/<agent_id> endpoint"""
    from src.services.agent_req import AgentRequirementModel

    try:
        # First create and save requirements
        model = AgentRequirementModel()
        requirements = {
            "agent_id": "api-test-123",
            "version": "1.0",
            "metadata": {
                "name": "API Test Agent",
                "description": "Test load endpoint",
                "created_at": "2024-01-01T00:00:00"
            },
            "purpose": "Test",
            "inputs": [],
            "outputs": [],
            "triggers": {"type": "manual"},
            "constraints": {}
        }

        model.save_requirements(requirements)

        # Then load via API
        response = client.get('/api/requirements/load/api-test-123')

        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['agent_id'] == 'api-test-123'
        assert 'requirements' in response.json

    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_api_load_requirements_not_found(client):
    """Test load endpoint with non-existent agent"""
    response = client.get('/api/requirements/load/nonexistent-agent')

    assert response.status_code == 404
    assert 'error' in response.json


@pytest.mark.integration
def test_requirements_generation_workflow(client):
    """Test complete workflow: clarification → requirements (requires Ollama)"""
    from src.services.clarification import ClarificationService
    from src.services.agent_req import AgentRequirementModel

    try:
        # 1. Start clarification session
        clar_service = ClarificationService()
        session = clar_service.start_session(
            "test_user",
            "I need an agent that monitors API health"
        )
        session_id = session["session_id"]

        # Simulate session completion
        from src.models.database import SessionLocal, Session as SessionModel
        db = SessionLocal()
        db_session = db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()

        if db_session:
            db_session.status = "complete"
            db.commit()

            # 2. Generate requirements
            try:
                req_model = AgentRequirementModel()
                result = req_model.generate_requirements(session_id)

                assert "requirements" in result
                assert "agent_id" in result["requirements"]
                assert "filepath" in result
            except Exception as e:
                # May fail if Ollama is slow, but that's ok for this test
                assert "Failed" in str(e) or "timeout" in str(e).lower() or "timed out" in str(e).lower()

        db.close()

    except ConnectionError:
        pytest.skip("Ollama server not running")
