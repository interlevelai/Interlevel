"""
Unit tests for agent requirements model
"""
import pytest
import json
from pathlib import Path
from src.services.agent_req import AgentRequirementModel
from src.services.clarification import ClarificationService
from src.models.database import init_db, SessionLocal, User, Session, Agent, Base, engine


@pytest.fixture(scope="module")
def setup_db():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(setup_db):
    """Create test user"""
    import uuid
    db = SessionLocal()
    unique_email = f"test-{uuid.uuid4()}@example.com"
    user = User(email=unique_email, token_balance=10000)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


@pytest.fixture
def completed_session(test_user):
    """Create a completed clarification session"""
    clarify = ClarificationService()

    # Start session
    result = clarify.start_session(
        test_user.user_id,
        "Check weather API every hour"
    )

    session_id = result["session_id"]

    # Manually mark as complete for testing
    db = SessionLocal()
    session = db.query(Session).filter(Session.session_id == session_id).first()
    session.status = "complete"
    db.commit()
    db.close()

    return session_id


def test_generate_requirements(setup_db, completed_session):
    """Test requirements generation"""
    service = AgentRequirementModel()

    try:
        result = service.generate_requirements(completed_session)

        assert "requirements" in result
        assert "filepath" in result
        assert "agent_id" in result["requirements"]
        assert "metadata" in result["requirements"]
        assert "purpose" in result["requirements"]
    except TimeoutError:
        pytest.skip("LLM provider timeout")


def test_save_and_load_requirements(setup_db):
    """Test saving and loading requirements"""
    service = AgentRequirementModel()

    # Create test requirements
    requirements = {
        "agent_id": "test-agent-123",
        "metadata": {"name": "Test Agent"},
        "purpose": "Test purpose"
    }

    # Save
    filepath = service.save_requirements(requirements)
    assert Path(filepath).exists()

    # Load
    loaded = service.load_requirements("test-agent-123")
    assert loaded["agent_id"] == "test-agent-123"
    assert loaded["metadata"]["name"] == "Test Agent"


def test_create_agent_record(setup_db, test_user):
    """Test creating agent database record"""
    service = AgentRequirementModel()

    requirements = {
        "agent_id": "test-agent-456",
        "metadata": {
            "name": "Test Agent 2",
            "description": "A test agent"
        },
        "purpose": "Testing"
    }

    agent = service.create_agent_record(requirements, test_user.user_id)

    assert agent.agent_id == "test-agent-456"
    assert agent.name == "Test Agent 2"
    assert agent.user_id == test_user.user_id
    assert agent.status == "requirements_complete"


def test_requirements_json_structure(setup_db):
    """Test requirements JSON structure validation"""
    service = AgentRequirementModel()

    requirements = {
        "agent_id": "test-agent-789",
        "metadata": {
            "name": "Validation Test Agent",
            "description": "Testing JSON structure"
        },
        "purpose": "Structure validation",
        "capabilities": ["api_call", "scheduling"],
        "constraints": {
            "max_retries": 3,
            "timeout": 30
        }
    }

    # Save requirements
    filepath = service.save_requirements(requirements)

    # Load and verify structure
    with open(filepath, 'r', encoding='utf-8') as f:
        loaded_json = json.load(f)

    assert "agent_id" in loaded_json
    assert "metadata" in loaded_json
    assert "purpose" in loaded_json
    assert loaded_json["agent_id"] == "test-agent-789"


def test_requirements_file_persistence(setup_db):
    """Test requirements persistence to filesystem"""
    service = AgentRequirementModel()

    requirements = {
        "agent_id": "test-agent-persist",
        "metadata": {"name": "Persistence Test"},
        "purpose": "Testing file persistence"
    }

    # Save multiple times
    filepath1 = service.save_requirements(requirements)
    filepath2 = service.save_requirements(requirements)

    # Both should point to same file
    assert filepath1 == filepath2
    assert Path(filepath1).exists()


def test_agent_record_status(setup_db, test_user):
    """Test agent record status tracking"""
    service = AgentRequirementModel()

    requirements = {
        "agent_id": "test-agent-status",
        "metadata": {"name": "Status Test Agent"},
        "purpose": "Testing status"
    }

    agent = service.create_agent_record(requirements, test_user.user_id)

    # Verify initial status
    assert agent.status == "requirements_complete"

    # Verify agent is in database
    db = SessionLocal()
    retrieved_agent = db.query(Agent).filter(
        Agent.agent_id == "test-agent-status"
    ).first()
    assert retrieved_agent is not None
    assert retrieved_agent.status == "requirements_complete"
    db.close()
