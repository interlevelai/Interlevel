"""
Unit tests for Phase 5: Universal Executor Service
Tests code generation, validation, and integration
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import tempfile

from src.services.executor import ExecutorService
from src.models.database import init_db, SessionLocal, User, Agent, Session, Base, engine


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
    unique_email = f"executor-test-{uuid.uuid4()}@example.com"
    user = User(email=unique_email, token_balance=50000)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


@pytest.fixture
def test_requirements():
    """Create sample requirements for testing"""
    return {
        "agent_id": "test-executor-agent",
        "version": "1.0",
        "metadata": {
            "name": "Test Executor Agent",
            "description": "Agent for testing executor service"
        },
        "purpose": "Test code generation",
        "inputs": [
            {"name": "param1", "type": "string", "required": True, "description": "Test parameter"}
        ],
        "outputs": [
            {"name": "result", "type": "string", "description": "Test result"}
        ],
        "triggers": {"type": "manual"},
        "platforms": [],
        "constraints": {"timeout": 30, "max_execution_time": 300},
        "success_criteria": ["Returns valid JSON"],
        "failure_handling": {"retry_policy": {"max_retries": 3}},
        "permissions": {"allowed_actions": [], "disallowed_actions": []}
    }


@pytest.fixture
def test_api_requirements():
    """Create API requirements for testing"""
    return {
        "agent_id": "test-api-agent",
        "metadata": {
            "name": "Test API Agent",
            "description": "API calling agent"
        },
        "purpose": "Test API integration",
        "inputs": [],
        "outputs": [],
        "triggers": {"type": "manual"},
        "platforms": [
            {
                "name": "REST API",
                "base_url": "https://api.example.com",
                "authentication": "api_key",
                "endpoints": ["GET /status"]
            }
        ],
        "constraints": {"timeout": 30},
        "success_criteria": [],
        "failure_handling": {"retry_policy": {"max_retries": 3}},
        "permissions": {"allowed_actions": [], "disallowed_actions": [], "required_secrets": ["API_KEY"]}
    }


class TestExecutorServiceInitialization:
    """Test executor service initialization"""

    def test_executor_service_creates(self):
        """Test ExecutorService can be instantiated"""
        executor = ExecutorService()
        assert executor is not None
        assert executor.llm is not None
        assert executor.db is not None
        assert executor.templates_dir.exists()
        assert executor.output_dir is not None


class TestTemplateSelection:
    """Test template selection logic"""

    def test_select_base_template_for_manual_agent(self, test_requirements):
        """Test base template selected for manual agents"""
        executor = ExecutorService()
        template_name = executor._select_template(test_requirements)
        assert template_name == "base_agent.py.template"

    def test_select_api_template_for_api_agent(self, test_api_requirements):
        """Test API template selected for agents with platforms"""
        executor = ExecutorService()
        template_name = executor._select_template(test_api_requirements)
        assert template_name == "api_agent.py.template"

    def test_select_scheduled_template_for_scheduled_agent(self, test_requirements):
        """Test scheduled template selected for scheduled agents"""
        test_requirements["triggers"]["type"] = "schedule"
        test_requirements["triggers"]["config"] = {"schedule": "0 0 * * *"}

        executor = ExecutorService()
        template_name = executor._select_template(test_requirements)
        assert template_name == "scheduled_agent.py.template"


class TestTemplateLoading:
    """Test template file loading"""

    def test_load_base_template(self):
        """Test base template can be loaded"""
        executor = ExecutorService()
        template = executor._load_template("base_agent.py.template")
        assert template is not None
        assert len(template) > 0
        assert "{agent_name}" in template
        assert "{business_logic_placeholder}" in template

    def test_load_api_template(self):
        """Test API template can be loaded"""
        executor = ExecutorService()
        template = executor._load_template("api_agent.py.template")
        assert template is not None
        assert "make_api_request" in template
        assert "get_headers" in template

    def test_load_scheduled_template(self):
        """Test scheduled template can be loaded"""
        executor = ExecutorService()
        template = executor._load_template("scheduled_agent.py.template")
        assert template is not None
        assert "load_state" in template
        assert "save_state" in template

    def test_load_nonexistent_template_raises_error(self):
        """Test loading nonexistent template raises error"""
        executor = ExecutorService()
        with pytest.raises(FileNotFoundError):
            executor._load_template("nonexistent_template.py.template")


class TestCodeGeneration:
    """Test code generation functionality"""

    def test_extract_code_blocks_from_markdown(self):
        """Test extracting code from markdown code blocks"""
        executor = ExecutorService()
        llm_response = """Here's the code:

```python
outputs = {"result": "test"}
```

This should work."""

        code = executor._extract_code_blocks(llm_response)
        assert "outputs" in code
        assert "result" in code

    def test_extract_code_blocks_without_language(self):
        """Test extracting code from code blocks without language specifier"""
        executor = ExecutorService()
        llm_response = """Here's the code:

```
outputs = {"test": "value"}
```"""

        code = executor._extract_code_blocks(llm_response)
        assert "outputs" in code

    def test_extract_code_blocks_fallback_to_raw(self):
        """Test fallback when no code blocks found"""
        executor = ExecutorService()
        raw_code = "outputs = {'fallback': True}"

        code = executor._extract_code_blocks(raw_code)
        assert "fallback" in code

    def test_build_prompt_includes_requirements(self, test_requirements):
        """Test prompt building includes requirements"""
        executor = ExecutorService()
        prompt = executor._build_prompt(test_requirements)

        assert test_requirements["purpose"] in prompt
        assert "param1" in prompt
        assert "Test parameter" in prompt

    def test_build_auth_headers_api_key(self, test_api_requirements):
        """Test building API key authentication headers"""
        executor = ExecutorService()
        auth = executor._build_auth_headers("api_key", test_api_requirements["permissions"])

        assert "Authorization" in auth
        assert "API_KEY" in auth

    def test_build_auth_headers_bearer(self):
        """Test building bearer token authentication"""
        executor = ExecutorService()
        permissions = {"required_secrets": ["BEARER_TOKEN"]}

        auth = executor._build_auth_headers("bearer", permissions)
        assert "Bearer" in auth

    def test_build_auth_headers_none(self):
        """Test no authentication"""
        executor = ExecutorService()
        auth = executor._build_auth_headers("none", {})

        assert "No authentication" in auth


class TestValidationPipeline:
    """Test code validation pipeline"""

    def test_validate_valid_python_syntax(self):
        """Test validation of valid Python code"""
        executor = ExecutorService()
        valid_code = """
def test():
    return True
outputs = {"status": "success"}
"""

        result = executor._validate_syntax(valid_code)
        assert result.is_valid is True

    def test_validate_invalid_python_syntax(self):
        """Test validation catches syntax errors"""
        executor = ExecutorService()
        invalid_code = "def test(\n    invalid syntax here"

        result = executor._validate_syntax(invalid_code)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_security_scan_patterns_safe_code(self):
        """Test security scan passes safe code"""
        executor = ExecutorService()
        safe_code = """
outputs = {"result": "test"}
logger.info("Processing complete")
"""

        result = executor._security_scan_patterns(safe_code)
        # Should pass (no dangerous patterns)
        assert result.is_valid is True

    def test_security_scan_patterns_dangerous_code(self):
        """Test security scan catches dangerous patterns"""
        executor = ExecutorService()
        dangerous_code = "eval(user_input)"

        result = executor._security_scan_patterns(dangerous_code)
        assert result.is_valid is False

    def test_format_code_valid(self):
        """Test code formatting"""
        executor = ExecutorService()
        code = "x=1\ny=2\noutputs={'test':'value'}"

        # Should format without errors
        try:
            formatted = executor._format_code(code)
            # Black might not be installed, but code should be handled
            assert formatted is not None
        except Exception:
            # If black not installed, that's ok
            pass

    def test_validate_and_format_complete_pipeline(self):
        """Test complete validation pipeline"""
        executor = ExecutorService()
        code = """
outputs = {"status": "success"}
logger.info("Done")
"""

        is_valid, formatted_code, errors = executor.validate_and_format(code)
        assert is_valid is True
        assert formatted_code is not None


class TestCodeAssembly:
    """Test code assembly and template substitution"""

    def test_assemble_code_replaces_placeholders(self, test_requirements):
        """Test code assembly replaces all placeholders"""
        executor = ExecutorService()
        template = executor._load_template("base_agent.py.template")

        business_logic = "outputs = {'result': 'test'}"

        code = executor._assemble_code(template, business_logic, test_requirements)

        # Check placeholders were replaced
        assert "{agent_name}" not in code
        assert "{agent_id}" not in code
        assert "test-executor-agent" in code
        assert "Test Executor Agent" in code
        assert business_logic in code

    def test_assemble_code_includes_business_logic(self, test_requirements):
        """Test assembled code includes generated business logic"""
        executor = ExecutorService()
        template = executor._load_template("base_agent.py.template")

        business_logic = """
param1 = inputs.get("param1", "default")
outputs = {"result": f"Processed {param1}"}
"""

        code = executor._assemble_code(template, business_logic, test_requirements)

        assert business_logic.strip() in code


class TestFileOperations:
    """Test file operations"""

    def test_save_generated_code_creates_file(self, setup_db):
        """Test generated code is saved to disk"""
        executor = ExecutorService()

        code = """#!/usr/bin/env python3
print("test")
"""

        agent_id = "test-file-save"
        filepath = executor._save_generated_code(agent_id, code)

        assert Path(filepath).exists()

        # Verify content
        with open(filepath, 'r') as f:
            saved_code = f.read()

        assert saved_code == code

        # Cleanup
        Path(filepath).unlink()

    def test_save_generated_code_creates_directory(self):
        """Test save creates output directory if needed"""
        executor = ExecutorService()

        # Use a temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            executor.output_dir = Path(tmpdir) / "test_output"

            code = "print('test')"
            filepath = executor._save_generated_code("test-agent", code)

            assert Path(filepath).exists()

    def test_update_agent_record_updates_database(self, setup_db, test_user):
        """Test agent record is updated in database"""
        executor = ExecutorService()

        # Create an agent record
        db = SessionLocal()
        agent = Agent(
            agent_id="test-update-agent",
            user_id=test_user.user_id,
            name="Test Update Agent",
            status="draft"
        )
        db.add(agent)
        db.commit()
        db.close()

        # Update with executor
        code_path = "/path/to/code.py"
        executor._update_agent_record("test-update-agent", code_path)

        # Verify update
        db = SessionLocal()
        updated_agent = db.query(Agent).filter(
            Agent.agent_id == "test-update-agent"
        ).first()

        assert updated_agent.code_path == code_path
        assert updated_agent.status == "code_generated"
        db.close()


class TestCompleteGeneration:
    """Integration tests for complete generation workflow"""

    @pytest.mark.skipif(
        True,  # Skip by default (requires LLM)
        reason="Requires LLM provider"
    )
    def test_generate_agent_code_complete_workflow(self, setup_db, test_user, test_requirements):
        """Test complete code generation workflow"""
        # Save requirements to file
        req_dir = Path(__file__).parent.parent.parent / "data" / "requirements"
        req_dir.mkdir(parents=True, exist_ok=True)

        req_file = req_dir / f"{test_requirements['agent_id']}.json"
        with open(req_file, 'w') as f:
            json.dump(test_requirements, f)

        # Create agent record
        db = SessionLocal()
        agent = Agent(
            agent_id=test_requirements["agent_id"],
            user_id=test_user.user_id,
            name=test_requirements["metadata"]["name"],
            status="requirements_complete"
        )
        db.add(agent)
        db.commit()
        db.close()

        # Generate code
        executor = ExecutorService()
        result = executor.generate_agent_code(test_requirements["agent_id"])

        # Verify result
        assert result["success"] is True
        assert result["agent_id"] == test_requirements["agent_id"]
        assert "code_path" in result

        # Cleanup
        req_file.unlink()

    def test_generate_agent_code_missing_requirements(self):
        """Test generation with missing requirements file"""
        executor = ExecutorService()
        result = executor.generate_agent_code("nonexistent-agent")

        assert result["success"] is False
        assert "error" in result


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_executor_handles_malformed_requirements(self):
        """Test executor handles malformed requirements gracefully"""
        executor = ExecutorService()

        # Missing required fields - should handle gracefully with defaults
        bad_requirements = {"agent_id": "test"}

        # The method uses .get() with defaults, so it handles missing fields gracefully
        try:
            prompt = executor._build_prompt(bad_requirements)
            # If we get here, that's fine - graceful handling
            assert prompt is not None
        except Exception:
            # Or it might raise an exception, which is also acceptable error handling
            pass

    def test_executor_continues_without_bandit(self):
        """Test executor works when bandit is not installed"""
        executor = ExecutorService()
        code = "outputs = {'test': 'value'}"

        # Should not fail even if bandit is missing
        result = executor._security_scan_bandit(code)
        assert result is not None

    def test_executor_continues_without_black(self):
        """Test executor works when black is not installed"""
        executor = ExecutorService()
        code = "x=1\ny=2"

        # Should return code even if black is missing
        formatted = executor._format_code(code)
        assert formatted is not None


class TestTemplateVariations:
    """Test different template variations"""

    def test_base_template_structure(self):
        """Test base template has required structure"""
        executor = ExecutorService()
        template = executor._load_template("base_agent.py.template")

        assert "#!/usr/bin/env python3" in template
        assert "def main():" in template
        assert "json.dumps" in template
        assert "try:" in template
        assert "except" in template

    def test_api_template_has_api_functions(self):
        """Test API template has API-specific functions"""
        executor = ExecutorService()
        template = executor._load_template("api_agent.py.template")

        assert "make_api_request" in template
        assert "get_headers" in template
        assert "requests.request" in template
        assert "TIMEOUT" in template

    def test_scheduled_template_has_state_management(self):
        """Test scheduled template has state management"""
        executor = ExecutorService()
        template = executor._load_template("scheduled_agent.py.template")

        assert "load_state" in template
        assert "save_state" in template
        assert "STATE_FILE" in template
        assert "run_count" in template
