"""
Phase 1: Foundation - Unit Tests
Tests for configuration, database, logging, and validators
"""
import pytest
import json
from pathlib import Path

# Settings Tests (TASK-101)
def test_settings_loaded():
    """Test that settings load correctly"""
    from config.settings import settings

    assert settings.LLM_PROVIDER in ["ollama", "openai", "anthropic"]
    assert settings.MAX_EXECUTION_TIME > 0
    assert settings.DATABASE_URL.startswith("sqlite")
    assert settings.API_PORT == 5000
    assert settings.OLLAMA_HOST == "http://localhost:11434"
    assert settings.OLLAMA_MODEL == "codellama"


def test_settings_path_resolution():
    """Test path resolution"""
    from config.settings import settings

    path = settings.get_absolute_path("data/test.txt")
    assert path.is_absolute()
    assert "data" in str(path)


def test_settings_directories_exist():
    """Test that required directories are created"""
    from config.settings import settings
    import os

    # Check that directories were created
    assert os.path.exists(settings.get_absolute_path("agents/generated"))
    assert os.path.exists(settings.get_absolute_path("data"))


# Database Tests (TASK-102)
def test_database_models_import():
    """Test that all database models can be imported"""
    from src.models.database import User, Agent, Execution, Session

    assert User is not None
    assert Agent is not None
    assert Execution is not None
    assert Session is not None


def test_database_user_model():
    """Test User model creation"""
    from src.models.database import User

    user = User(email="test@example.com", token_balance=50000)
    assert user.email == "test@example.com"
    assert user.token_balance == 50000
    assert user.user_id is not None


def test_database_agent_model():
    """Test Agent model creation"""
    from src.models.database import Agent

    agent = Agent(
        user_id="test_user_id",
        name="Test Agent",
        description="A test agent",
        status="draft"
    )
    assert agent.name == "Test Agent"
    assert agent.status == "draft"
    assert agent.agent_id is not None


def test_database_execution_model():
    """Test Execution model"""
    from src.models.database import Execution

    execution = Execution(
        agent_id="test_agent",
        user_id="test_user",
        status="pending"
    )
    assert execution.status == "pending"
    assert execution.tokens_used == 0


def test_database_session_model():
    """Test Session model"""
    from src.models.database import Session

    session = Session(
        user_id="test_user",
        conversation_state=json.dumps([{"role": "user", "content": "test"}])
    )
    assert session.status == "active"
    assert session.user_id == "test_user"
    assert not session.is_expired


def test_database_schemas_import():
    """Test that Pydantic schemas can be imported"""
    from src.models.schemas import (
        UserResponse, AgentResponse, ExecutionResponse, SessionResponse
    )

    assert UserResponse is not None
    assert AgentResponse is not None
    assert ExecutionResponse is not None
    assert SessionResponse is not None


# Logging Tests (TASK-103)
def test_logger_initialization():
    """Test logger can be created"""
    from src.utils.logger import get_logger

    logger = get_logger("test_logger")
    assert logger is not None
    assert logger.logger.name == "test_logger"


def test_logger_correlation_id():
    """Test correlation ID functionality"""
    from src.utils.logger import get_logger, generate_correlation_id

    logger = get_logger("test")
    correlation_id = generate_correlation_id()

    assert correlation_id is not None
    assert len(correlation_id) > 0

    logger.set_correlation_id(correlation_id)
    assert logger.correlation_id == correlation_id


# Validators Tests (TASK-104)
def test_validator_email_valid():
    """Test email validation with valid email"""
    from src.utils.validators import validate_email

    result = validate_email("test@example.com")
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validator_email_invalid():
    """Test email validation with invalid email"""
    from src.utils.validators import validate_email

    result = validate_email("invalid-email")
    assert result.is_valid is False
    assert len(result.errors) > 0


def test_validator_json_string_valid():
    """Test JSON validation with valid JSON"""
    from src.utils.validators import validate_json_string

    valid_json = json.dumps({"key": "value"})
    result = validate_json_string(valid_json)
    assert result.is_valid is True


def test_validator_json_string_invalid():
    """Test JSON validation with invalid JSON"""
    from src.utils.validators import validate_json_string

    result = validate_json_string("not valid json")
    assert result.is_valid is False
    assert len(result.errors) > 0


def test_validator_code_clean():
    """Test code validation with clean code"""
    from src.utils.validators import validate_agent_code

    clean_code = """
def hello():
    print("Hello, World!")
    return True
"""
    result = validate_agent_code(clean_code)
    assert result.is_valid is True


def test_validator_code_syntax_error():
    """Test code validation with syntax errors"""
    from src.utils.validators import validate_agent_code

    bad_code = "def broken( x"
    result = validate_agent_code(bad_code)
    assert result.is_valid is False


def test_validator_code_dangerous_patterns():
    """Test code validation detects dangerous patterns"""
    from src.utils.validators import validate_agent_code

    dangerous_code = "os.system('rm -rf /')"
    result = validate_agent_code(dangerous_code)
    assert result.is_valid is False


def test_validator_requirements_valid():
    """Test requirements validation with valid spec"""
    from src.utils.validators import validate_requirements_json

    requirements = {
        "agent_id": "test",
        "metadata": {"name": "test"},
        "purpose": "test",
        "inputs": [],
        "outputs": [],
        "triggers": {"type": "manual"},
        "constraints": {}
    }
    result = validate_requirements_json(requirements)
    assert result.is_valid is True


def test_validator_requirements_missing_fields():
    """Test requirements validation detects missing fields"""
    from src.utils.validators import validate_requirements_json

    incomplete = {"agent_id": "test"}
    result = validate_requirements_json(incomplete)
    assert result.is_valid is False
    assert len(result.errors) > 0
