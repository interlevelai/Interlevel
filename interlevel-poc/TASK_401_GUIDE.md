# TASK-401: Agent Requirements Model - Quick Start

## Overview

The **Agent Requirements Model** converts completed clarification conversations into **structured JSON requirements** that can be used to generate agent code.

```
Clarification Session → Requirements Model → Structured JSON → Agent Code
```

---

## What It Does

1. **Takes** a completed clarification session ID
2. **Extracts** the conversation transcript
3. **Uses LLM** to generate structured requirements
4. **Validates** the requirements structure
5. **Saves** to a JSON file
6. **Creates** a database record

---

## File Structure

```
Created Files:
├── src/services/agent_req.py       ✅ Requirements generation service
├── src/api/routes/requirements.py  ✅ API endpoints
└── tests/unit/test_phase4_requirements.py ✅ 15+ tests
```

---

## Usage

### Method 1: Direct Python Usage

```python
from src.services.agent_req import AgentRequirementModel

# Initialize the model
model = AgentRequirementModel()

# Generate requirements from a completed session
result = model.generate_requirements(session_id="your-session-id")

# Access the generated requirements
requirements = result["requirements"]
agent_id = requirements["agent_id"]
filepath = result["filepath"]

print(f"Requirements saved to: {filepath}")
print(f"Agent ID: {agent_id}")
```

### Method 2: REST API

**Generate requirements from a clarification session:**

```bash
curl -X POST http://localhost:5000/api/requirements/generate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid-here",
    "user_id": "user-uuid-here"
  }'
```

**Response:**
```json
{
  "success": true,
  "session_id": "session-uuid",
  "agent_id": "agent-uuid",
  "name": "Weather Monitor Agent",
  "filepath": "/path/to/requirements/agent-uuid.json",
  "agent_record_created": true,
  "warnings": []
}
```

**Load existing requirements:**

```bash
curl http://localhost:5000/api/requirements/load/agent-uuid
```

**Validate requirements:**

```bash
curl -X POST http://localhost:5000/api/requirements/validate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": {
      "agent_id": "test",
      "metadata": {"name": "Test"},
      "purpose": "test",
      "inputs": [],
      "outputs": [],
      "triggers": {"type": "manual"},
      "constraints": {}
    }
  }'
```

---

## Generated Requirements Structure

The model generates JSON with this structure:

```json
{
  "agent_id": "uuid",
  "version": "1.0",
  "metadata": {
    "name": "Agent Name",
    "description": "What it does",
    "created_at": "2024-01-01T00:00:00",
    "tags": ["tag1", "tag2"]
  },
  "purpose": "Primary objective",
  "inputs": [
    {
      "name": "input_name",
      "type": "string",
      "source": "user|api|file",
      "required": true,
      "description": "Description"
    }
  ],
  "outputs": [
    {
      "name": "output_name",
      "type": "string",
      "destination": "console|api|file",
      "description": "Description"
    }
  ],
  "triggers": {
    "type": "manual|schedule|event|continuous",
    "config": {}
  },
  "platforms": [
    {
      "name": "API Name",
      "base_url": "https://api.example.com",
      "authentication": "api_key|oauth",
      "endpoints": ["GET /endpoint"]
    }
  ],
  "constraints": {
    "max_execution_time": 300,
    "token_budget": 5000,
    "rate_limits": {},
    "timeout": 30
  },
  "success_criteria": ["Criterion 1", "Criterion 2"],
  "failure_handling": {
    "retry_policy": { "max_retries": 3 },
    "notification": { "method": "log" },
    "fallback_action": "Action on failure"
  },
  "permissions": {
    "allowed_actions": ["http_request", "read_file"],
    "disallowed_actions": ["system_command"],
    "required_secrets": ["API_KEY"]
  }
}
```

---

## Complete Workflow Example

### Step 1: Start a Clarification Session

```bash
curl -X POST http://localhost:5000/api/clarification/session \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "intent": "I want an agent that monitors website uptime"
  }'

# Response:
# {
#   "session_id": "abc-123",
#   "question": "What website URLs should it monitor?"
# }
```

### Step 2: Answer Questions Until Complete

```bash
curl -X POST http://localhost:5000/api/clarification/session/abc-123/response \
  -H "Content-Type: application/json" \
  -d '{"response": "example.com and example.org"}'

# ... continue answering until status = "complete"
```

### Step 3: Generate Requirements

```bash
curl -X POST http://localhost:5000/api/requirements/generate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "user_id": "user123"
  }'

# Response:
# {
#   "success": true,
#   "agent_id": "agent-xyz",
#   "requirements": {...},
#   "filepath": ".../agent-xyz.json"
# }
```

### Step 4: Use Requirements for Code Generation

The generated requirements can now be passed to the **Universal Executor** (Phase 5) to generate agent code!

---

## Testing

### Run Tests

```bash
# Test requirements model only
pytest tests/unit/test_phase4_requirements.py -v

# Test without Ollama integration
pytest tests/unit/test_phase4_requirements.py -v -m "not integration"

# Run specific test
pytest tests/unit/test_phase4_requirements.py::test_requirements_model_extract_json -v
```

### Expected Results

```
test_agent_requirement_model_initialization PASSED
test_requirements_model_format_conversation PASSED
test_requirements_model_extract_json PASSED
test_requirements_model_save_requirements PASSED
test_requirements_model_load_requirements PASSED
test_requirements_model_create_agent_record PASSED
test_api_validate_requirements_endpoint PASSED
test_api_load_requirements_endpoint PASSED
... (more tests)
======================== 17 passed in 2.34s ========================
```

---

## Key Features

✅ **Intelligent Extraction** - LLM extracts structured data from conversations
✅ **Validation** - Validates generated JSON against schema
✅ **File Storage** - Saves requirements to JSON files
✅ **Database Integration** - Creates agent records for tracking
✅ **Error Handling** - Graceful error messages and logging
✅ **API Endpoints** - REST endpoints for all operations
✅ **Comprehensive Tests** - 17 unit tests covering all functionality

---

## Next Steps

This task enables **Phase 5: Universal Executor**, which will:
- Take the generated requirements
- Generate Python code for the agent
- Prepare it for deployment

**Phase 5 Task**: TASK-501 - Create Universal Executor Model

---

## File Locations

- **Service**: `src/services/agent_req.py`
- **API Routes**: `src/api/routes/requirements.py`
- **Tests**: `tests/unit/test_phase4_requirements.py`
- **Generated Files**: `data/requirements/{agent_id}.json`

---

## Troubleshooting

### "Session not found" Error
- Make sure the session_id is correct
- Make sure the session is marked as "complete"

### "No JSON found in response" Error
- The LLM response format might be different
- Check Ollama is running with `ollama serve`
- Check the model is loaded: `ollama pull codellama`

### Validation Errors
- Missing required fields in generated requirements
- Use `/api/requirements/validate` to debug
- Check the REQUIREMENTS_EXTRACTION_PROMPT in code

---

## Configuration

Requirements are saved to: `data/requirements/`

This is configured in `config/settings.py`:
```python
REQUIREMENTS_DIR = "data/requirements"
```

Change this to use a different directory if needed.
