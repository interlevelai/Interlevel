# Testing Guide - Interlevel POC

This document explains how to run tests for all completed phases.

## Quick Start

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run only unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_phase1_foundation.py -v

# Run specific test function
pytest tests/unit/test_phase1_foundation.py::test_settings_loaded -v
```

## Test Structure

```
tests/
├── unit/
│   ├── test_phase1_foundation.py    # Phase 1: Foundation tests
│   ├── test_phase2_llm.py           # Phase 2: LLM Integration tests
│   └── test_phase3_clarification.py # Phase 3: Clarification tests
└── integration/
    └── (future: API integration tests)
```

## Phase 1: Foundation Tests

**Tests for**: Configuration, Database, Logging, Validators

```bash
pytest tests/unit/test_phase1_foundation.py -v
```

### What's Tested:
- ✅ Settings loading and configuration
- ✅ Database models (User, Agent, Execution, Session)
- ✅ Pydantic schemas
- ✅ Logging utilities
- ✅ Email validation
- ✅ JSON validation
- ✅ Code security validation
- ✅ Requirements JSON validation

### Expected Output:
```
test_settings_loaded PASSED
test_settings_path_resolution PASSED
test_settings_directories_exist PASSED
test_database_models_import PASSED
test_database_user_model PASSED
test_database_agent_model PASSED
test_database_execution_model PASSED
test_database_session_model PASSED
test_logger_initialization PASSED
test_validator_email_valid PASSED
... (10+ more tests)
```

---

## Phase 2: LLM Integration Tests

**Tests for**: LLM Client, Ollama Provider

```bash
# Run all LLM tests
pytest tests/unit/test_phase2_llm.py -v

# Run only fast tests (no Ollama required)
pytest tests/unit/test_phase2_llm.py -v -m "not integration"

# Run integration tests (requires Ollama running)
pytest tests/unit/test_phase2_llm.py -v -m integration
```

### Prerequisites:
- Ollama running on localhost:11434
- `codellama` model pulled

### What's Tested:
- ✅ LLM Client initialization
- ✅ Model name retrieval
- ✅ Token counting
- ✅ Ollama provider connection
- ✅ Text generation
- ✅ Chat functionality

### Expected Output:
```
test_llm_client_initialization PASSED
test_llm_client_model_name PASSED
test_llm_client_token_counting PASSED
test_ollama_provider_initialization PASSED
test_ollama_provider_connection PASSED
test_ollama_provider_model_name PASSED
```

---

## Phase 3: Clarification Service Tests

**Tests for**: Clarification Service, Clarification API, Database Integration

```bash
# Run all clarification tests
pytest tests/unit/test_phase3_clarification.py -v

# Run only fast tests (no LLM generation)
pytest tests/unit/test_phase3_clarification.py -v -m "not integration"

# Run with detailed output
pytest tests/unit/test_phase3_clarification.py -v -s
```

### Prerequisites:
- Ollama running (for some tests)
- Flask app context (automatically handled)

### What's Tested:
- ✅ Service initialization
- ✅ Session creation
- ✅ Session retrieval
- ✅ Response handling
- ✅ Session state management
- ✅ API endpoints
- ✅ Complete workflows

### Expected Output:
```
test_clarification_service_initialization PASSED
test_clarification_start_session PASSED
test_clarification_get_session PASSED
test_clarification_add_response PASSED
test_api_health_endpoint PASSED
test_api_status_endpoint PASSED
test_api_start_session_endpoint PASSED
test_api_add_response_endpoint PASSED
test_api_workflow_complete_conversation PASSED
```

---

## Running All Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run all tests and stop on first failure
pytest tests/ -v -x

# Run all tests with 4 workers (parallel)
pytest tests/ -v -n 4
```

## Test Markers

```bash
# Run only unit tests
pytest -m "not integration" tests/

# Run only integration tests (slow)
pytest -m integration tests/

# Run only tests requiring Ollama
pytest -m ollama tests/
```

## Troubleshooting

### "Ollama server not running" Error
If you see this error:
```
ConnectionError: Cannot connect to Ollama at http://localhost:11434
```

**Solution**: Start Ollama in another terminal:
```bash
ollama serve
```

### Database Lock Error
If you see "database is locked":

**Solution**: This usually means another test is using the database. Run tests sequentially:
```bash
pytest tests/ -v --tb=short
```

### Import Errors
If you see "ModuleNotFoundError":

**Solution**: Make sure you're in the `interlevel-poc` directory and venv is activated:
```bash
cd interlevel-poc
source venv/Scripts/activate  # Windows
pytest tests/ -v
```

---

## Test Coverage

To see which parts of your code are tested:

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

---

## Next Steps

After Phase 3 tests pass, you're ready for:
- **Phase 4**: Requirements Model tests
- **Phase 5**: Executor tests
- **Phase 6**: Injector tests

Each phase will have its own test file following the same pattern.
