# POC Local Development Plan - Interlevel

## Purpose
Build and validate the Interlevel platform locally before incurring cloud costs. This POC demonstrates all core functionality using local/open-source alternatives to AWS services, with a clear migration path to production AWS architecture.

---

## 🎯 POC Success Criteria

By the end of this POC, you should be able to:
1. ✅ Describe a task in natural language
2. ✅ Have the system clarify requirements interactively
3. ✅ Generate a requirements JSON specification
4. ✅ Generate executable Python agent code
5. ✅ Deploy and run the agent locally
6. ✅ Track token consumption
7. ✅ Verify the agent performs the intended task (e.g., call a REST API)

**Timeline**: 2-4 weeks
**Team Size**: 1-2 developers
**Cost**: $0-50 (optional: OpenAI API credits)

---

## 🏗️ Local Architecture

### Simplified Component Map

```
┌─────────────────────────────────────────────────────────┐
│               Local Development Setup                   │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  Web UI      │         │  CLI Tool    │             │
│  │  (Optional)  │         │  (Primary)   │             │
│  │  React/HTML  │         │  Python      │             │
│  └──────┬───────┘         └──────┬───────┘             │
│         │                        │                      │
│         └────────┬───────────────┘                      │
│                  │                                      │
│         ┌────────▼─────────┐                           │
│         │   Flask API      │  (Replaces API Gateway)   │
│         │   (Port 5000)    │                           │
│         └────────┬─────────┘                           │
│                  │                                      │
│    ┌─────────────┼─────────────┐                       │
│    │             │             │                       │
│ ┌──▼──────┐ ┌───▼────┐ ┌─────▼──────┐                │
│ │Clarify  │ │AgentReq│ │ Executor   │                │
│ │Service  │ │ Model  │ │ Model      │                │
│ │(Module) │ │(Module)│ │ (Module)   │                │
│ └──┬──────┘ └───┬────┘ └─────┬──────┘                │
│    │            │            │                         │
│    └────────────┼────────────┘                         │
│                 │                                       │
│         ┌───────▼────────┐                             │
│         │  LLM Provider  │                             │
│         │  - Ollama      │  (Local, free)             │
│         │  - OpenAI API  │  (Paid, better quality)    │
│         │  - Anthropic   │  (Paid, best for coding)   │
│         └───────┬────────┘                             │
│                 │                                       │
│    ┌────────────┴────────────┐                        │
│    │                         │                         │
│ ┌──▼─────────┐      ┌────────▼──────┐                │
│ │  SQLite DB │      │  File System  │                │
│ │  (agents,  │      │  (code, logs) │                │
│ │   users,   │      │               │                │
│ │  tokens)   │      │               │                │
│ └────────────┘      └───────────────┘                │
│                                                        │
│    ┌────────────────────────────┐                    │
│    │  Generated Agents          │                    │
│    │  (Local Python scripts)    │                    │
│    │  Run via subprocess/exec   │                    │
│    └────────────────────────────┘                    │
└────────────────────────────────────────────────────────┘
```

---

## 📦 Technology Stack (Local)

| Component | Local Alternative | Production (AWS) | Migration Effort |
|-----------|------------------|------------------|------------------|
| **API Layer** | Flask/FastAPI | API Gateway | Low (change endpoints) |
| **Compute** | Python modules | Lambda | Low (wrap in handler) |
| **Database** | SQLite | DynamoDB | Medium (change queries) |
| **Storage** | Filesystem | S3 | Low (change I/O calls) |
| **LLM** | Ollama/OpenAI API | Bedrock | Low (change client) |
| **Auth** | Simple JWT | Cognito | Medium (identity mgmt) |
| **Logging** | Python logging | CloudWatch | Low (change logger) |
| **Triggers** | Manual/Cron | EventBridge | Low (change scheduler) |
| **Secrets** | .env file | Secrets Manager | Low (change config) |

---

## 🛠️ Project Structure

```
interlevel-poc/
├── README.md
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Local secrets (git-ignored)
├── config/
│   └── settings.py           # Configuration management
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py            # Flask/FastAPI app
│   │   └── routes/
│   │       ├── agents.py     # Agent CRUD endpoints
│   │       ├── sessions.py   # Clarification sessions
│   │       └── auth.py       # Simple JWT auth
│   ├── services/
│   │   ├── __init__.py
│   │   ├── clarification.py  # Clarification Service
│   │   ├── agent_req.py      # Agent-Requirement Model
│   │   ├── executor.py       # Universal Executor
│   │   ├── injector.py       # Injector (local deployment)
│   │   └── token_manager.py  # Token tracking
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py       # SQLite setup
│   │   └── schemas.py        # Data models
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py         # LLM abstraction layer
│   │   └── providers/
│   │       ├── ollama.py     # Local LLM
│   │       ├── openai.py     # OpenAI API
│   │       └── anthropic.py  # Claude API
│   └── utils/
│       ├── __init__.py
│       ├── logger.py         # Logging setup
│       └── validators.py     # Input validation
├── agents/
│   ├── generated/            # Generated agent code
│   ├── templates/            # Agent code templates
│   └── runtime/              # Agent execution environment
├── data/
│   ├── interlevel.db         # SQLite database
│   ├── requirements/         # Requirements JSON files
│   └── logs/                 # Execution logs
├── tests/
│   ├── unit/
│   └── integration/
├── cli/
│   └── interlevel_cli.py     # Command-line interface
└── scripts/
    ├── setup.sh              # Initial setup
    └── run_agent.py          # Manual agent runner
```

---

## 🚀 Phase-by-Phase Implementation

### Phase 1: Foundation (Week 1, Days 1-3)
**Goal**: Set up project structure and basic infrastructure

#### Tasks:
1. **Project Setup**
   ```bash
   mkdir interlevel-poc && cd interlevel-poc
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. **Install Dependencies**
   ```txt
   # requirements.txt
   flask==3.0.0
   flask-cors==4.0.0
   pydantic==2.5.0
   python-dotenv==1.0.0
   sqlalchemy==2.0.23
   openai==1.6.0              # Optional: if using OpenAI
   anthropic==0.8.0           # Optional: if using Claude
   ollama==0.1.6              # Optional: if using local LLM
   pyjwt==2.8.0
   pytest==7.4.3
   black==23.12.0
   ruff==0.1.8
   ```

3. **Database Schema (SQLite)**
   ```sql
   -- data/schema.sql

   CREATE TABLE users (
       user_id TEXT PRIMARY KEY,
       email TEXT UNIQUE NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       token_balance INTEGER DEFAULT 100000
   );

   CREATE TABLE agents (
       agent_id TEXT PRIMARY KEY,
       user_id TEXT NOT NULL,
       name TEXT NOT NULL,
       description TEXT,
       requirements_json TEXT,
       code_path TEXT,
       status TEXT DEFAULT 'draft',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(user_id)
   );

   CREATE TABLE executions (
       execution_id TEXT PRIMARY KEY,
       agent_id TEXT NOT NULL,
       user_id TEXT NOT NULL,
       status TEXT DEFAULT 'pending',
       tokens_used INTEGER DEFAULT 0,
       started_at TIMESTAMP,
       completed_at TIMESTAMP,
       error_message TEXT,
       FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
   );

   CREATE TABLE sessions (
       session_id TEXT PRIMARY KEY,
       user_id TEXT NOT NULL,
       conversation_state TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       expires_at TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(user_id)
   );
   ```

4. **Configuration Management**
   ```python
   # config/settings.py
   import os
   from dotenv import load_dotenv

   load_dotenv()

   class Settings:
       # Database
       DATABASE_URL = "sqlite:///data/interlevel.db"

       # LLM Provider (choose one)
       LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama|openai|anthropic
       OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
       ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
       OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

       # API
       API_PORT = 5000
       SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")

       # Paths
       GENERATED_AGENTS_DIR = "agents/generated"
       REQUIREMENTS_DIR = "data/requirements"
       LOGS_DIR = "data/logs"

       # Token limits
       DEFAULT_TOKEN_BUDGET = 10000
       MAX_EXECUTION_TIME = 300  # seconds

   settings = Settings()
   ```

**Deliverables**:
- ✅ Project structure created
- ✅ Dependencies installed
- ✅ SQLite database initialized
- ✅ Configuration system working

---

### Phase 2: LLM Integration (Week 1, Days 4-5)
**Goal**: Connect to an LLM provider and test basic prompting

#### Option A: Ollama (Free, Local, Recommended for POC)
```bash
# Install Ollama (Mac/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2        # Smaller, faster
# or
ollama pull codellama     # Better for code generation

# Run Ollama server (runs on localhost:11434)
ollama serve
```

#### Option B: OpenAI (Paid, Better Quality)
```bash
# Set API key in .env
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
```

#### Option C: Anthropic Claude (Paid, Best for Code)
```bash
# Set API key in .env
ANTHROPIC_API_KEY=sk-ant-your-key-here
LLM_PROVIDER=anthropic
```

#### Implementation:
```python
# src/llm/client.py
from config.settings import settings

class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self._init_client()

    def _init_client(self):
        if self.provider == "ollama":
            from .providers.ollama import OllamaProvider
            self.client = OllamaProvider()
        elif self.provider == "openai":
            from .providers.openai import OpenAIProvider
            self.client = OpenAIProvider()
        elif self.provider == "anthropic":
            from .providers.anthropic import AnthropicProvider
            self.client = AnthropicProvider()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text from prompt"""
        return self.client.generate(prompt, max_tokens)

    def chat(self, messages: list[dict]) -> str:
        """Chat-style interaction"""
        return self.client.chat(messages)
```

**Test Script**:
```python
# tests/test_llm.py
from src.llm.client import LLMClient

def test_llm_connection():
    client = LLMClient()
    response = client.generate("Say 'Hello, Interlevel!'")
    print(f"LLM Response: {response}")
    assert len(response) > 0

if __name__ == "__main__":
    test_llm_connection()
```

**Deliverables**:
- ✅ LLM provider connected and tested
- ✅ Basic prompt/response working
- ✅ Abstraction layer allows easy provider switching

---

### Phase 3: Clarification Service (Week 1, Days 6-7)
**Goal**: Interactive requirements gathering

#### Implementation:
```python
# src/services/clarification.py
from src.llm.client import LLMClient
from src.models.schemas import Session
import uuid

CLARIFICATION_SYSTEM_PROMPT = """
You are an AI assistant helping users define requirements for autonomous agents.

Your goal is to ask targeted questions to clarify:
1. What task should the agent perform?
2. What inputs does it need?
3. What outputs should it produce?
4. When should it run? (trigger conditions)
5. What platforms/APIs are involved?
6. What are the constraints? (time limits, budgets, etc.)

Ask ONE question at a time. Be specific and actionable.
When you have enough information, respond with: "REQUIREMENTS_COMPLETE"
"""

class ClarificationService:
    def __init__(self):
        self.llm = LLMClient()

    def start_session(self, user_id: str, initial_task: str) -> Session:
        session_id = str(uuid.uuid4())
        conversation = [
            {"role": "system", "content": CLARIFICATION_SYSTEM_PROMPT},
            {"role": "user", "content": initial_task}
        ]

        # Get first clarifying question
        response = self.llm.chat(conversation)
        conversation.append({"role": "assistant", "content": response})

        # Save to DB (simplified)
        session = Session(
            session_id=session_id,
            user_id=user_id,
            conversation=conversation,
            status="active"
        )
        # db.save(session)

        return session

    def continue_session(self, session_id: str, user_response: str) -> dict:
        # Load session from DB
        # session = db.get_session(session_id)

        conversation = session.conversation
        conversation.append({"role": "user", "content": user_response})

        response = self.llm.chat(conversation)
        conversation.append({"role": "assistant", "content": response})

        if "REQUIREMENTS_COMPLETE" in response:
            return {
                "status": "complete",
                "message": "Requirements gathering complete!",
                "conversation": conversation
            }

        return {
            "status": "continue",
            "question": response,
            "conversation": conversation
        }
```

**CLI Test**:
```python
# cli/interlevel_cli.py
from src.services.clarification import ClarificationService

def run_clarification():
    service = ClarificationService()

    print("=== Interlevel Agent Creator ===\n")
    task = input("Describe what you want your agent to do:\n> ")

    session = service.start_session("test-user", task)
    print(f"\n🤖 {session.conversation[-1]['content']}\n")

    while True:
        user_input = input("> ")
        result = service.continue_session(session.session_id, user_input)

        if result["status"] == "complete":
            print(f"\n✅ {result['message']}")
            break

        print(f"\n🤖 {result['question']}\n")

if __name__ == "__main__":
    run_clarification()
```

**Deliverables**:
- ✅ Interactive CLI for task clarification
- ✅ Multi-turn conversation with LLM
- ✅ Session management

---

### Phase 4: Agent-Requirement Model (Week 2, Days 1-2)
**Goal**: Convert conversation to structured JSON

#### Implementation:
```python
# src/services/agent_req.py
from src.llm.client import LLMClient
import json

REQUIREMENTS_EXTRACTION_PROMPT = """
Based on the following conversation, extract a structured requirements document in JSON format.

Output ONLY valid JSON with this structure:
{
  "agent_id": "generate-uuid",
  "metadata": {
    "name": "Short agent name",
    "description": "Brief description"
  },
  "purpose": "What the agent does",
  "inputs": [{"name": "input1", "type": "string", "source": "api|user|file"}],
  "outputs": [{"name": "output1", "type": "string", "destination": "api|user|file"}],
  "triggers": {
    "type": "manual|schedule|event",
    "config": {}
  },
  "constraints": {
    "max_execution_time": 300,
    "token_budget": 5000
  },
  "platforms": ["REST API", "HTTP"],
  "success_criteria": ["criteria1", "criteria2"],
  "permissions": {
    "allowed_actions": ["http_request", "read_file"],
    "disallowed_actions": ["system_command", "file_write"]
  }
}

Conversation:
{conversation}
"""

class AgentRequirementModel:
    def __init__(self):
        self.llm = LLMClient()

    def generate_requirements(self, conversation: list[dict]) -> dict:
        # Format conversation
        conv_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation
        ])

        prompt = REQUIREMENTS_EXTRACTION_PROMPT.format(conversation=conv_text)
        response = self.llm.generate(prompt, max_tokens=2000)

        # Parse JSON
        try:
            # Extract JSON from response (in case LLM adds extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]

            requirements = json.loads(json_str)

            # Validate
            self._validate_requirements(requirements)

            return requirements
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse requirements JSON: {e}")

    def _validate_requirements(self, req: dict):
        required_fields = ["metadata", "purpose", "inputs", "outputs", "triggers"]
        for field in required_fields:
            if field not in req:
                raise ValueError(f"Missing required field: {field}")

    def save_requirements(self, requirements: dict) -> str:
        """Save requirements JSON to file"""
        agent_id = requirements.get("agent_id", str(uuid.uuid4()))
        requirements["agent_id"] = agent_id

        filepath = f"data/requirements/{agent_id}.json"
        with open(filepath, 'w') as f:
            json.dump(requirements, f, indent=2)

        return filepath
```

**Deliverables**:
- ✅ Convert conversation → JSON requirements
- ✅ Validate requirements structure
- ✅ Save to filesystem

---

### Phase 5: Universal Executor (Week 2, Days 3-5)
**Goal**: Generate executable Python code

#### Implementation:
```python
# src/services/executor.py
from src.llm.client import LLMClient
import json

CODE_GENERATION_PROMPT = """
You are a code generator. Generate a complete, executable Python script based on these requirements.

Requirements:
{requirements}

Generate a Python script with:
1. All necessary imports
2. A main() function that executes the task
3. Error handling
4. Logging
5. Return structured results

Output ONLY the Python code, no explanations.
"""

AGENT_TEMPLATE = '''
#!/usr/bin/env python3
"""
Auto-generated agent: {name}
Description: {description}
Generated: {timestamp}
"""

import requests
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main agent logic"""
    logger.info("Starting agent: {name}")

    try:
        # TODO: Implement agent logic
        {agent_logic}

        logger.info("Agent completed successfully")
        return {{"status": "success", "timestamp": datetime.now().isoformat()}}

    except Exception as e:
        logger.error(f"Agent failed: {{e}}")
        return {{"status": "error", "error": str(e)}}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
'''

class UniversalExecutor:
    def __init__(self):
        self.llm = LLMClient()

    def generate_agent_code(self, requirements: dict) -> str:
        """Generate Python code from requirements"""

        # Create prompt
        req_json = json.dumps(requirements, indent=2)
        prompt = CODE_GENERATION_PROMPT.format(requirements=req_json)

        # Generate code
        code = self.llm.generate(prompt, max_tokens=3000)

        # Clean up (remove markdown code blocks if present)
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]

        # Validate syntax
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            raise ValueError(f"Generated code has syntax errors: {e}")

        return code

    def save_agent_code(self, agent_id: str, code: str) -> str:
        """Save generated code to file"""
        filepath = f"agents/generated/{agent_id}.py"

        with open(filepath, 'w') as f:
            f.write(code)

        # Make executable
        import os
        os.chmod(filepath, 0o755)

        return filepath
```

**Deliverables**:
- ✅ Generate Python code from requirements
- ✅ Validate syntax
- ✅ Save executable script

---

### Phase 6: Injector Service (Week 2, Days 6-7)
**Goal**: Deploy agent locally (just save & mark ready)

#### Implementation:
```python
# src/services/injector.py
import subprocess
import json
from pathlib import Path

class InjectorService:
    def deploy_agent(self, agent_id: str, code_path: str) -> dict:
        """
        Deploy agent locally (for POC, just validate and mark ready)
        In production, this would deploy to Lambda
        """

        # Validate file exists
        if not Path(code_path).exists():
            raise FileNotFoundError(f"Agent code not found: {code_path}")

        # Run security checks (basic for POC)
        self._security_scan(code_path)

        # Update agent status in DB
        # db.update_agent(agent_id, status="deployed")

        return {
            "agent_id": agent_id,
            "status": "deployed",
            "code_path": code_path,
            "execution_command": f"python {code_path}"
        }

    def _security_scan(self, code_path: str):
        """Basic security validation"""
        with open(code_path, 'r') as f:
            code = f.read()

        # Prohibit dangerous patterns
        dangerous = ["os.system", "eval(", "exec(", "__import__"]
        for pattern in dangerous:
            if pattern in code:
                raise SecurityError(f"Dangerous pattern detected: {pattern}")

    def execute_agent(self, agent_id: str, code_path: str) -> dict:
        """Execute agent and capture output"""

        try:
            # Run agent as subprocess
            result = subprocess.run(
                ["python", code_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Parse output
            output = result.stdout
            if result.returncode != 0:
                return {
                    "status": "error",
                    "error": result.stderr,
                    "exit_code": result.returncode
                }

            return {
                "status": "success",
                "output": output,
                "exit_code": 0
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Agent execution timeout (5 minutes)"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
```

**Deliverables**:
- ✅ Security validation
- ✅ Agent execution via subprocess
- ✅ Output capture

---

### Phase 7: End-to-End Integration (Week 3, Days 1-3)
**Goal**: Wire everything together in a CLI

#### Complete CLI:
```python
# cli/interlevel_cli.py
from src.services.clarification import ClarificationService
from src.services.agent_req import AgentRequirementModel
from src.services.executor import UniversalExecutor
from src.services.injector import InjectorService
import json

def create_agent_workflow():
    print("=" * 60)
    print("  INTERLEVEL - AI Agent Creator (Local POC)")
    print("=" * 60)
    print()

    # Step 1: Clarification
    print("STEP 1: Task Clarification")
    print("-" * 60)
    clarify = ClarificationService()

    task = input("Describe your agent task:\n> ")
    session = clarify.start_session("demo-user", task)

    conversation = session.conversation
    print(f"\n🤖 {conversation[-1]['content']}\n")

    while True:
        user_input = input("> ")
        result = clarify.continue_session(session.session_id, user_input)

        if result["status"] == "complete":
            conversation = result["conversation"]
            print(f"\n✅ {result['message']}\n")
            break

        print(f"\n🤖 {result['question']}\n")

    # Step 2: Generate Requirements
    print("\nSTEP 2: Generating Requirements JSON")
    print("-" * 60)

    agent_req = AgentRequirementModel()
    requirements = agent_req.generate_requirements(conversation)
    req_path = agent_req.save_requirements(requirements)

    print(f"✅ Requirements saved: {req_path}")
    print(f"\n{json.dumps(requirements, indent=2)}\n")

    # Step 3: Generate Code
    print("\nSTEP 3: Generating Agent Code")
    print("-" * 60)

    executor = UniversalExecutor()
    code = executor.generate_agent_code(requirements)
    agent_id = requirements["agent_id"]
    code_path = executor.save_agent_code(agent_id, code)

    print(f"✅ Agent code generated: {code_path}\n")
    print("Generated code preview:")
    print("-" * 60)
    print(code[:500] + "..." if len(code) > 500 else code)
    print("-" * 60)

    # Step 4: Deploy & Execute
    print("\nSTEP 4: Deploy & Test Agent")
    print("-" * 60)

    injector = InjectorService()
    deployment = injector.deploy_agent(agent_id, code_path)

    print(f"✅ Agent deployed: {deployment['agent_id']}")
    print(f"   Status: {deployment['status']}")
    print(f"   Command: {deployment['execution_command']}\n")

    # Ask to run
    run_now = input("Run agent now? (y/n): ")
    if run_now.lower() == 'y':
        print("\n🚀 Executing agent...\n")
        result = injector.execute_agent(agent_id, code_path)

        print("Execution Result:")
        print("-" * 60)
        print(json.dumps(result, indent=2))
        print("-" * 60)

    print("\n✅ Agent creation complete!")
    print(f"   Agent ID: {agent_id}")
    print(f"   Requirements: {req_path}")
    print(f"   Code: {code_path}")

if __name__ == "__main__":
    try:
        create_agent_workflow()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
```

**Deliverables**:
- ✅ End-to-end workflow working
- ✅ Agent created from natural language
- ✅ Agent executes successfully

---

## 📊 POC Demo Scenarios

### Scenario 1: Weather Alert Agent
```
User: "I want an agent that checks the weather API every morning and sends me an alert if it's going to rain"

Expected Flow:
1. Clarification: Which weather API? What time? How to send alert?
2. Requirements: Use OpenWeatherMap API, check at 7 AM, log to console
3. Code Generation: Python script that calls weather API
4. Execution: Runs and logs "Rain expected today" or "Clear skies"
```

### Scenario 2: REST API Monitor
```
User: "Create an agent that calls my /health endpoint and logs if it's down"

Expected Flow:
1. Clarification: What's the URL? How often to check? What counts as "down"?
2. Requirements: Call https://my-api.com/health every 5 minutes, log if non-200
3. Code Generation: Python script with requests library
4. Execution: Makes HTTP request, logs status
```

### Scenario 3: Data Transformer
```
User: "I need an agent that fetches JSON from an API and converts it to CSV"

Expected Flow:
1. Clarification: Which API? What fields to include? Where to save CSV?
2. Requirements: Call API, extract fields, write to file
3. Code Generation: Python with requests + csv module
4. Execution: Fetches data, writes CSV file
```

---

## 🔄 Migration Path to AWS

When ready to move to production AWS:

### 1. API → API Gateway
```python
# Local: Flask route
@app.route('/agents', methods=['POST'])
def create_agent():
    return jsonify(result)

# AWS: Lambda handler
def lambda_handler(event, context):
    body = json.loads(event['body'])
    # Same logic
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

### 2. SQLite → DynamoDB
```python
# Local: SQLite
cursor.execute("SELECT * FROM agents WHERE user_id=?", (user_id,))

# AWS: DynamoDB
table.query(KeyConditionExpression=Key('user_id').eq(user_id))
```

### 3. Filesystem → S3
```python
# Local: File write
with open(f'agents/{agent_id}.py', 'w') as f:
    f.write(code)

# AWS: S3 upload
s3.put_object(Bucket='interlevel-agents', Key=f'{agent_id}.py', Body=code)
```

### 4. Ollama/OpenAI → Bedrock
```python
# Local: Direct API
client.chat.completions.create(model="gpt-4", messages=messages)

# AWS: Bedrock
bedrock.invoke_model(modelId='anthropic.claude-v2', body=payload)
```

### 5. Manual Execution → EventBridge
```python
# Local: subprocess.run()
result = subprocess.run(['python', 'agent.py'])

# AWS: EventBridge triggers Lambda automatically
# (No code change needed, just configuration)
```

---

## 💰 Cost Comparison

### POC (Local)
- Compute: $0 (local machine)
- Storage: $0 (local disk)
- LLM: $0-50/month (Ollama free, or minimal OpenAI usage)
- **Total: $0-50/month**

### Production (AWS, 100 users)
- Lambda: ~$20/month
- DynamoDB: ~$10/month
- S3: ~$5/month
- Bedrock: ~$100/month (variable)
- API Gateway: ~$15/month
- **Total: ~$150-200/month**

**Savings during POC**: $150-200/month while validating concept

---

## ✅ POC Success Checklist

Before moving to AWS, ensure:

- [ ] End-to-end workflow works (task → requirements → code → execution)
- [ ] At least 3 different agent types tested successfully
- [ ] Code generation quality is acceptable
- [ ] Security scanning catches obvious issues
- [ ] Token tracking is reasonably accurate
- [ ] Error handling works as expected
- [ ] Performance is acceptable (< 2 minutes total creation time)
- [ ] Team is comfortable with the architecture

---

## 🚀 Next Steps After POC

Once POC is validated:
1. Review Architecture_Plan.md for full AWS design
2. Set up AWS account and infrastructure (CDK/SAM)
3. Migrate one component at a time (start with API)
4. Add production features (auth, monitoring, scaling)
5. Launch MVP

---

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Ollama Setup Guide](https://ollama.ai/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Python Best Practices](https://docs.python-guide.org/)

---

**Document Version**: 1.0
**Last Updated**: 2026-02-07
**Estimated Completion**: 2-4 weeks (1-2 developers)
