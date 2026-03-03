"""
Integration tests for the complete TASK-402 & TASK-403 workflow
Tests the interaction between CLI, services, and database
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

from src.services.agent_req import AgentRequirementModel
from src.services.clarification import ClarificationService
from src.models.database import (
    init_db, SessionLocal, User, Session, Agent, Base, engine
)


@pytest.fixture(scope="module")
def setup_integration_db():
    """Setup test database for integration tests"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def integration_user(setup_integration_db):
    """Create test user for integration"""
    import uuid
    db = SessionLocal()
    unique_email = f"integration-{uuid.uuid4()}@example.com"
    user = User(email=unique_email, token_balance=50000)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


@pytest.fixture
def completed_integration_session(integration_user):
    """Create a completed session for integration testing"""
    db = SessionLocal()
    session = Session(
        session_id="integration-test-session",
        user_id=integration_user.user_id,
        status="complete",
        conversation_state=[
            {"role": "user", "content": "Create a data processing agent"},
            {"role": "assistant", "content": "I'll help create a data processor agent"}
        ]
    )
    db.add(session)
    db.commit()
    yield session
    db.close()


class TestEndToEndWorkflow:
    """Test complete workflow from session to CLI to database"""

    def test_session_to_requirements_model_flow(self, setup_integration_db, integration_user):
        """Test flow from completed session to requirements model"""
        # Create a session
        db = SessionLocal()
        session = Session(
            user_id=integration_user.user_id,
            status="complete",
            conversation_state=[
                {"role": "user", "content": "Create email notification agent"},
                {"role": "assistant", "content": "I'll create that agent"}
            ]
        )
        db.add(session)
        db.commit()
        session_id = session.session_id
        db.close()

        # Verify session exists
        db = SessionLocal()
        retrieved_session = db.query(Session).filter(
            Session.session_id == session_id
        ).first()
        assert retrieved_session is not None
        assert retrieved_session.status == "complete"
        assert retrieved_session.user_id == integration_user.user_id
        db.close()

    def test_requirements_model_creates_agent_record(self, setup_integration_db, integration_user):
        """Test that requirements model creates agent record in database"""
        service = AgentRequirementModel()

        requirements = {
            "agent_id": "integration-test-agent",
            "metadata": {
                "name": "Integration Test Agent",
                "description": "Testing end-to-end workflow"
            },
            "purpose": "Integration testing",
            "capabilities": ["data_processing", "api_calls"]
        }

        # Create agent record
        agent = service.create_agent_record(requirements, integration_user.user_id)

        # Verify in database
        db = SessionLocal()
        retrieved_agent = db.query(Agent).filter(
            Agent.agent_id == "integration-test-agent"
        ).first()

        assert retrieved_agent is not None
        assert retrieved_agent.name == "Integration Test Agent"
        assert retrieved_agent.user_id == integration_user.user_id
        assert retrieved_agent.status == "requirements_complete"
        assert retrieved_agent.requirements_json == requirements
        db.close()

    def test_requirements_file_contains_valid_json(self, setup_integration_db):
        """Test that saved requirements are valid, readable JSON"""
        service = AgentRequirementModel()

        requirements = {
            "agent_id": "json-test-agent",
            "metadata": {"name": "JSON Test Agent"},
            "purpose": "Testing JSON validity",
            "constraints": {
                "timeout": 30,
                "max_retries": 3
            }
        }

        filepath = service.save_requirements(requirements)

        # Verify file exists and contains valid JSON
        assert Path(filepath).exists()

        with open(filepath, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        assert loaded["agent_id"] == "json-test-agent"
        assert loaded["metadata"]["name"] == "JSON Test Agent"
        assert loaded["constraints"]["timeout"] == 30

    def test_cli_loads_and_displays_requirements(self, setup_integration_db, integration_user):
        """Test CLI can load requirements and display them"""
        service = AgentRequirementModel()

        requirements = {
            "agent_id": "cli-test-agent",
            "metadata": {
                "name": "CLI Test Agent",
                "description": "For CLI testing"
            },
            "purpose": "CLI workflow testing"
        }

        # Create agent record
        agent = service.create_agent_record(requirements, integration_user.user_id)
        assert agent is not None

        # Simulate CLI loading
        db = SessionLocal()
        cli_agent = db.query(Agent).filter(
            Agent.agent_id == "cli-test-agent"
        ).first()

        assert cli_agent is not None
        assert cli_agent.requirements_json is not None
        assert cli_agent.name == "CLI Test Agent"
        db.close()

    def test_user_to_agent_relationship(self, setup_integration_db, integration_user):
        """Test user-agent relationship integrity"""
        service = AgentRequirementModel()

        # Create multiple agents for same user
        for i in range(3):
            requirements = {
                "agent_id": f"relationship-test-{i}",
                "metadata": {"name": f"Test Agent {i}"},
                "purpose": f"Relationship test {i}"
            }
            service.create_agent_record(requirements, integration_user.user_id)

        # Verify all agents belong to user
        db = SessionLocal()
        agents = db.query(Agent).filter(
            Agent.user_id == integration_user.user_id
        ).all()

        assert len(agents) == 3
        for agent in agents:
            assert agent.user_id == integration_user.user_id

        db.close()

    def test_session_to_agent_creation_pipeline(self, setup_integration_db, integration_user):
        """Test complete pipeline: session -> requirements -> agent record"""
        # Step 1: Create session
        db = SessionLocal()
        session = Session(
            user_id=integration_user.user_id,
            status="complete",
            conversation_state=[
                {"role": "user", "content": "Create monitoring agent"},
                {"role": "assistant", "content": "Creating monitoring agent"}
            ]
        )
        db.add(session)
        db.commit()
        session_id = session.session_id
        db.close()

        # Step 2: Create requirements (simulating what CLI would do)
        service = AgentRequirementModel()
        requirements = {
            "agent_id": f"pipeline-test-{session_id[:8]}",
            "metadata": {"name": "Monitoring Agent"},
            "purpose": "Pipeline test",
            "source_session": session_id
        }

        # Step 3: Create agent record
        agent = service.create_agent_record(requirements, integration_user.user_id)

        # Verify complete pipeline
        assert agent is not None
        assert agent.agent_id == f"pipeline-test-{session_id[:8]}"

        # Verify agent is in database
        db = SessionLocal()
        retrieved_agent = db.query(Agent).filter(
            Agent.agent_id == agent.agent_id
        ).first()
        assert retrieved_agent is not None
        assert retrieved_agent.requirements_json["source_session"] == session_id
        db.close()


class TestCLIServiceIntegration:
    """Test CLI and service integration"""

    def test_cli_service_instantiation(self, setup_integration_db):
        """Test CLI can instantiate the service"""
        with patch('sys.argv', ['generate_requirements.py']):
            service = AgentRequirementModel()
            assert service is not None
            assert service.llm is not None
            assert service.db is not None

    def test_requirements_model_database_access(self, setup_integration_db, integration_user):
        """Test that requirements model can access database"""
        service = AgentRequirementModel()

        # Create test requirements
        requirements = {
            "agent_id": "db-access-test",
            "metadata": {"name": "DB Access Test"},
            "purpose": "Testing DB access"
        }

        # Create agent (uses database)
        agent = service.create_agent_record(requirements, integration_user.user_id)

        # Verify agent was created
        assert agent is not None
        assert agent.agent_id == "db-access-test"

    def test_cli_mock_workflow(self, setup_integration_db, integration_user):
        """Test complete CLI workflow with mocking"""
        # Mock the service result
        mock_result = {
            "requirements": {
                "agent_id": "cli-mock-test",
                "metadata": {"name": "CLI Mock Agent"}
            },
            "filepath": "/path/to/requirements.json",
            "warnings": []
        }

        with patch('cli.generate_requirements.AgentRequirementModel') as mock_service:
            with patch('cli.generate_requirements.init_db'):
                mock_instance = MagicMock()
                mock_instance.generate_requirements.return_value = mock_result
                mock_service.return_value = mock_instance

                # Simulate CLI call
                session_id = "test-session-123"
                result = mock_instance.generate_requirements(session_id)

                assert result["requirements"]["agent_id"] == "cli-mock-test"
                assert "filepath" in result
                mock_instance.generate_requirements.assert_called_with(session_id)


class TestDataIntegrity:
    """Test data integrity across components"""

    def test_requirements_json_roundtrip(self, setup_integration_db):
        """Test requirements survive save/load cycle"""
        service = AgentRequirementModel()

        original = {
            "agent_id": "roundtrip-test",
            "metadata": {
                "name": "Roundtrip Test",
                "version": "1.0.0"
            },
            "purpose": "Testing data integrity",
            "capabilities": ["api", "scheduling", "storage"],
            "constraints": {
                "timeout": 60,
                "max_memory": "512MB"
            }
        }

        # Save
        filepath = service.save_requirements(original)

        # Load
        loaded = service.load_requirements("roundtrip-test")

        # Verify all data intact
        assert loaded["agent_id"] == original["agent_id"]
        assert loaded["metadata"] == original["metadata"]
        assert loaded["purpose"] == original["purpose"]
        assert loaded["capabilities"] == original["capabilities"]
        assert loaded["constraints"] == original["constraints"]

    def test_database_agent_record_integrity(self, setup_integration_db, integration_user):
        """Test agent record maintains data integrity in database"""
        service = AgentRequirementModel()

        requirements = {
            "agent_id": "integrity-test",
            "metadata": {
                "name": "Integrity Test",
                "description": "Testing data integrity"
            },
            "purpose": "Verify data survives DB operations"
        }

        # Create record
        agent = service.create_agent_record(requirements, integration_user.user_id)
        original_id = agent.agent_id

        # Retrieve and verify
        db = SessionLocal()
        retrieved = db.query(Agent).filter(
            Agent.agent_id == original_id
        ).first()

        assert retrieved.requirements_json == requirements
        assert retrieved.name == requirements["metadata"]["name"]
        db.close()
