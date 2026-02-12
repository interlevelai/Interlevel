# Implementation Tasks - Interlevel POC

## Document Purpose
This document contains **detailed, actionable tasks** for implementing the Interlevel POC. Each task is designed to be picked up by a developer or AI agent and implemented independently.

**Status Tracking**: Mark each task as:
- ⬜ Not Started
- 🟡 In Progress
- ✅ Completed
- ❌ Blocked

---

## 📋 Task Summary

| Phase | Tasks | Est. Time | Status |
|-------|-------|-----------|--------|
| **Setup** | 2 tasks | 1 hour | ⬜ |
| **Phase 1: Foundation** | 6 tasks | 2-3 days | ⬜ |
| **Phase 2: LLM Integration** | 4 tasks | 1-2 days | ⬜ |
| **Phase 3: Clarification** | 5 tasks | 2 days | ⬜ |
| **Phase 4: Requirements Model** | 4 tasks | 2 days | ⬜ |
| **Phase 5: Executor** | 5 tasks | 3 days | ⬜ |
| **Phase 6: Injector** | 4 tasks | 2 days | ⬜ |
| **Phase 7: Integration** | 5 tasks | 3 days | ⬜ |
| **TOTAL** | **35 tasks** | **15-19 days** | |

---

# SETUP PHASE

## SETUP-001: Create Automated Setup Script ⬜
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Dependencies**: None

### Description
Create a bash script that automates project setup including directory creation, dependency installation, and configuration.

### Implementation Details

**File to Create**: `scripts/setup.sh`

```bash
#!/bin/bash
# Interlevel POC - Automated Setup Script

set -e  # Exit on error

echo "======================================"
echo "  Interlevel POC - Setup Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.md" ]; then
    echo "❌ Error: Please run this script from the Interlevel root directory"
    exit 1
fi

# Create POC directory
echo "📁 Creating project structure..."
mkdir -p interlevel-poc
cd interlevel-poc

# Create all subdirectories
mkdir -p src/{api/routes,services,models,llm/providers,utils}
mkdir -p agents/{generated,templates,runtime}
mkdir -p data/{requirements,logs}
mkdir -p tests/{unit,integration}
mkdir -p cli scripts config

echo "✅ Directory structure created"

# Create requirements.txt
echo "📦 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# Core Framework
flask==3.0.0
flask-cors==4.0.0
pydantic==2.5.0
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.23

# LLM Providers
ollama==0.1.6
openai==1.6.0
anthropic==0.8.0

# Utilities
requests==2.31.0
pyjwt==2.8.0

# Development Tools
pytest==7.4.3
pytest-cov==4.1.0
black==23.12.0
ruff==0.1.8
mypy==1.7.0
EOF

echo "✅ requirements.txt created"

# Create .env.example
echo "🔧 Creating .env.example..."
cat > .env.example << 'EOF'
# LLM Provider Configuration
LLM_PROVIDER=ollama  # Options: ollama, openai, anthropic
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=codellama

# OpenAI (if using)
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic (if using)
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Database
DATABASE_URL=sqlite:///data/interlevel.db

# API Configuration
API_PORT=5000
SECRET_KEY=dev-secret-change-in-production

# Agent Configuration
MAX_EXECUTION_TIME=300
DEFAULT_TOKEN_BUDGET=10000
GENERATED_AGENTS_DIR=agents/generated
REQUIREMENTS_DIR=data/requirements
LOGS_DIR=data/logs
EOF

echo "✅ .env.example created"

# Copy to .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env created (using default values)"
else
    echo "ℹ️  .env already exists, skipping"
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create __init__.py files
echo "📄 Creating __init__.py files..."
touch src/__init__.py
touch src/api/__init__.py
touch src/api/routes/__init__.py
touch src/services/__init__.py
touch src/models/__init__.py
touch src/llm/__init__.py
touch src/llm/providers/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

echo "✅ __init__.py files created"

# Create README
echo "📝 Creating README.md..."
cat > README.md << 'EOF'
# Interlevel POC - Local Development

## Quick Start

1. Activate virtual environment:
   ```bash
   source venv/bin/activate  # Mac/Linux
   # venv\Scripts\activate   # Windows
   ```

2. Install Ollama (if not already installed):
   ```bash
   brew install ollama  # Mac
   # Or: curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. Start Ollama and pull model:
   ```bash
   ollama serve  # In one terminal
   ollama pull codellama  # In another terminal
   ```

4. Run tests:
   ```bash
   pytest tests/
   ```

5. Start API server:
   ```bash
   python src/api/app.py
   ```

## Project Structure

See [../poc_readme.md](../poc_readme.md) for full documentation.

## Development

- Run tests: `pytest tests/`
- Format code: `black src/ tests/`
- Lint: `ruff check src/ tests/`
- Type check: `mypy src/`
EOF

echo "✅ README.md created"

echo ""
echo "======================================"
echo "  ✅ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. cd interlevel-poc"
echo "2. source venv/bin/activate"
echo "3. Install Ollama: brew install ollama"
echo "4. Start Ollama: ollama serve"
echo "5. Pull model: ollama pull codellama"
echo "6. Start implementing Phase 1 tasks"
echo ""
echo "See Implementation_Tasks.md for detailed task list"
```

### Acceptance Criteria
- ✅ Script creates all necessary directories
- ✅ Script creates requirements.txt with all dependencies
- ✅ Script creates .env.example and .env files
- ✅ Script creates virtual environment
- ✅ Script installs all dependencies
- ✅ Script creates all __init__.py files
- ✅ Script creates README.md
- ✅ Script is executable: `chmod +x scripts/setup.sh`
- ✅ Script completes without errors

### Testing
```bash
cd /Users/pavisivya/eclipse-workspace/Interlevel
chmod +x scripts/setup.sh
./scripts/setup.sh
```

---

## SETUP-002: Install and Configure Ollama ⬜
**Priority**: HIGH
**Estimated Time**: 15 minutes
**Dependencies**: None

### Description
Install Ollama locally and pull the codellama model for code generation.

### Implementation Details

**Steps**:
1. Install Ollama:
   ```bash
   # Mac
   brew install ollama

   # Or using curl (Mac/Linux)
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. Start Ollama server:
   ```bash
   ollama serve
   ```

3. Pull model (in another terminal):
   ```bash
   ollama pull codellama  # 7GB, best for code generation
   # OR
   ollama pull llama2     # 3.8GB, faster but less specialized
   ```

4. Test connection:
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "codellama",
     "prompt": "Write a Python function that adds two numbers"
   }'
   ```

### Acceptance Criteria
- ✅ Ollama installed successfully
- ✅ Ollama server running on localhost:11434
- ✅ codellama model downloaded
- ✅ Test API call returns valid response

---

# PHASE 1: FOUNDATION (Days 1-3)

## TASK-101: Create Configuration Management System ⬜
**Priority**: HIGH
**Estimated Time**: 1 hour
**Dependencies**: SETUP-001

### Description
Create a centralized configuration management system using Pydantic settings.

### Implementation Details

**File to Create**: `config/settings.py`

```python
"""
Configuration management for Interlevel POC
Uses environment variables with sensible defaults
"""
import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent
    GENERATED_AGENTS_DIR: str = "agents/generated"
    REQUIREMENTS_DIR: str = "data/requirements"
    LOGS_DIR: str = "data/logs"

    # Database
    DATABASE_URL: str = "sqlite:///data/interlevel.db"

    # LLM Provider Configuration
    LLM_PROVIDER: str = Field(default="ollama", description="LLM provider: ollama, openai, anthropic")

    # Ollama settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "codellama"

    # OpenAI settings (optional)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Anthropic settings (optional)
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    # API Configuration
    API_PORT: int = 5000
    API_HOST: str = "0.0.0.0"
    SECRET_KEY: str = "dev-secret-change-in-production"

    # Agent execution limits
    MAX_EXECUTION_TIME: int = 300  # seconds
    DEFAULT_TOKEN_BUDGET: int = 10000
    MAX_RETRIES: int = 3

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute based on BASE_DIR"""
        return self.BASE_DIR / relative_path

    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        dirs = [
            self.GENERATED_AGENTS_DIR,
            self.REQUIREMENTS_DIR,
            self.LOGS_DIR,
            "data"
        ]
        for dir_path in dirs:
            path = self.get_absolute_path(dir_path)
            path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories()
```

### Acceptance Criteria
- ✅ Settings class uses Pydantic BaseSettings
- ✅ All configuration loaded from environment variables
- ✅ Sensible defaults provided
- ✅ Directory creation helper method
- ✅ Global settings instance created
- ✅ Type hints for all fields
- ✅ Imports without errors

### Testing
```python
# tests/unit/test_settings.py
from config.settings import settings

def test_settings_loaded():
    assert settings.LLM_PROVIDER in ["ollama", "openai", "anthropic"]
    assert settings.MAX_EXECUTION_TIME > 0
    assert settings.DATABASE_URL.startswith("sqlite")

def test_path_resolution():
    path = settings.get_absolute_path("data/test.txt")
    assert path.is_absolute()

def test_directories_created():
    import os
    assert os.path.exists("agents/generated")
    assert os.path.exists("data/requirements")
    assert os.path.exists("data/logs")
```

---

## TASK-102: Create Database Schema and Models ⬜
**Priority**: HIGH
**Estimated Time**: 2 hours
**Dependencies**: TASK-101

### Description
Create SQLite database schema with SQLAlchemy ORM models for users, agents, executions, and sessions.

### Implementation Details

**File to Create**: `src/models/database.py`

```python
"""
Database models and setup for Interlevel POC
Uses SQLAlchemy ORM with SQLite
"""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config.settings import settings
import uuid

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    token_balance = Column(Integer, default=100000)

    # Relationships
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="user")

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', email='{self.email}')>"


class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    requirements_json = Column(JSON)  # Stored as JSON
    code_path = Column(String)
    status = Column(String, default="draft")  # draft, deployed, active, failed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="agents")
    executions = relationship("Execution", back_populates="agent")

    def __repr__(self):
        return f"<Agent(agent_id='{self.agent_id}', name='{self.name}', status='{self.status}')>"


class Execution(Base):
    """Agent execution model"""
    __tablename__ = "executions"

    execution_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.agent_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    status = Column(String, default="pending")  # pending, running, success, failed, timeout
    tokens_used = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    output = Column(Text)

    # Relationships
    agent = relationship("Agent", back_populates="executions")
    user = relationship("User", back_populates="executions")

    def __repr__(self):
        return f"<Execution(execution_id='{self.execution_id}', status='{self.status}')>"

    @property
    def duration(self):
        """Calculate execution duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class Session(Base):
    """Clarification session model"""
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    conversation_state = Column(JSON)  # Stored as JSON array of messages
    status = Column(String, default="active")  # active, complete, abandoned
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(session_id='{self.session_id}', status='{self.status}')>"

    @property
    def is_expired(self):
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at


# Database engine and session
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_test_user(email: str = "test@interlevel.com") -> User:
    """Create a test user for development"""
    db = SessionLocal()
    try:
        user = User(email=email, token_balance=100000)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
    print("Database schema created successfully")
```

**File to Create**: `src/models/schemas.py`

```python
"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")


class UserResponse(BaseModel):
    user_id: str
    email: str
    token_balance: int
    created_at: datetime

    class Config:
        from_attributes = True


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class AgentResponse(BaseModel):
    agent_id: str
    user_id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    execution_id: str
    agent_id: str
    status: str
    tokens_used: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    output: Optional[str]

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class Message(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ConversationState(BaseModel):
    messages: List[Message]
    metadata: Optional[Dict[str, Any]] = {}
```

### Acceptance Criteria
- ✅ All 4 models defined (User, Agent, Execution, Session)
- ✅ Proper relationships between models
- ✅ UUID primary keys
- ✅ Timestamps with defaults
- ✅ JSON columns for flexible data
- ✅ SQLite database created
- ✅ SessionLocal and get_db() working
- ✅ init_db() creates tables successfully
- ✅ Pydantic schemas for validation

### Testing
```bash
# Run the database script
python src/models/database.py

# Check if database file created
ls -lh data/interlevel.db
```

---

## TASK-103: Create Logging Utility ⬜
**Priority**: MEDIUM
**Estimated Time**: 30 minutes
**Dependencies**: TASK-101

### Description
Create a structured logging utility with JSON formatting and correlation IDs.

### Implementation Details

**File to Create**: `src/utils/logger.py`

```python
"""
Structured logging utility for Interlevel POC
Provides JSON-formatted logs with correlation IDs
"""
import logging
import json
import sys
from datetime import datetime
from typing import Optional
from config.settings import settings
import uuid


class StructuredLogger:
    """Structured logger with JSON output"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))

        # Console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)

        self.correlation_id: Optional[str] = None

    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for request tracking"""
        self.correlation_id = correlation_id

    def _build_log_entry(self, level: str, message: str, **kwargs) -> dict:
        """Build structured log entry"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.logger.name,
            "message": message,
        }

        if self.correlation_id:
            entry["correlation_id"] = self.correlation_id

        # Add any additional context
        entry.update(kwargs)

        return entry

    def debug(self, message: str, **kwargs):
        self.logger.debug(json.dumps(self._build_log_entry("DEBUG", message, **kwargs)))

    def info(self, message: str, **kwargs):
        self.logger.info(json.dumps(self._build_log_entry("INFO", message, **kwargs)))

    def warning(self, message: str, **kwargs):
        self.logger.warning(json.dumps(self._build_log_entry("WARNING", message, **kwargs)))

    def error(self, message: str, **kwargs):
        self.logger.error(json.dumps(self._build_log_entry("ERROR", message, **kwargs)))

    def critical(self, message: str, **kwargs):
        self.logger.critical(json.dumps(self._build_log_entry("CRITICAL", message, **kwargs)))


class JsonFormatter(logging.Formatter):
    """JSON formatter for standard logging"""

    def format(self, record):
        # If message is already JSON, return as-is
        if record.getMessage().startswith('{'):
            return record.getMessage()

        # Otherwise, wrap in JSON
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)


def generate_correlation_id() -> str:
    """Generate a new correlation ID"""
    return str(uuid.uuid4())


# Example usage
if __name__ == "__main__":
    logger = get_logger("test")
    logger.set_correlation_id(generate_correlation_id())

    logger.info("Test log message", user_id="user-123", action="test")
    logger.error("Error occurred", error_code="ERR001")
```

### Acceptance Criteria
- ✅ Structured JSON logging
- ✅ Correlation ID support
- ✅ Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Additional context via kwargs
- ✅ Console output
- ✅ Respects LOG_LEVEL from settings

---

## TASK-104: Create Input Validation Utilities ⬜
**Priority**: MEDIUM
**Estimated Time**: 1 hour
**Dependencies**: None

### Description
Create utility functions for validating user inputs, agent code, and requirements.

### Implementation Details

**File to Create**: `src/utils/validators.py`

```python
"""
Validation utilities for Interlevel POC
"""
import re
import json
from typing import Dict, Any, List
from pydantic import BaseModel, ValidationError


class ValidationResult(BaseModel):
    """Result of validation"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


# Dangerous patterns in generated code
DANGEROUS_PATTERNS = [
    (r'\bos\.system\(', "os.system() - command injection risk"),
    (r'\beval\(', "eval() - arbitrary code execution"),
    (r'\bexec\(', "exec() - arbitrary code execution"),
    (r'\b__import__\(', "__import__() - dynamic imports"),
    (r'subprocess\.[a-z]+\([^)]*shell\s*=\s*True', "subprocess with shell=True - command injection"),
    (r'open\([^)]*[\'"]w[\'"]', "file write operations - potential overwrite"),
    (r'rm\s+-rf', "rm -rf command - destructive operation"),
    (r'DROP\s+TABLE', "DROP TABLE - database destruction"),
]

# Required fields in requirements JSON
REQUIRED_REQUIREMENTS_FIELDS = [
    "agent_id",
    "metadata",
    "purpose",
    "inputs",
    "outputs",
    "triggers",
    "constraints"
]


def validate_email(email: str) -> ValidationResult:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(pattern, email):
        return ValidationResult(is_valid=True)
    else:
        return ValidationResult(
            is_valid=False,
            errors=["Invalid email format"]
        )


def validate_agent_code(code: str) -> ValidationResult:
    """Validate generated agent code for security issues"""
    errors = []
    warnings = []

    # Check syntax
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        errors.append(f"Syntax error: {e}")

    # Check for dangerous patterns
    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            errors.append(f"Dangerous pattern detected: {description}")

    # Check for hardcoded credentials
    credential_patterns = [
        r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
        r'password\s*=\s*[\'"][^\'"]+[\'"]',
        r'secret\s*=\s*[\'"][^\'"]+[\'"]',
        r'token\s*=\s*[\'"][^\'"]+[\'"]',
    ]

    for pattern in credential_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            warnings.append("Potential hardcoded credentials detected")
            break

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_requirements_json(requirements: Dict[str, Any]) -> ValidationResult:
    """Validate requirements JSON structure"""
    errors = []
    warnings = []

    # Check required fields
    for field in REQUIRED_REQUIREMENTS_FIELDS:
        if field not in requirements:
            errors.append(f"Missing required field: {field}")

    # Validate metadata
    if "metadata" in requirements:
        metadata = requirements["metadata"]
        if not isinstance(metadata, dict):
            errors.append("metadata must be a dictionary")
        elif "name" not in metadata:
            errors.append("metadata.name is required")

    # Validate inputs/outputs are arrays
    for field in ["inputs", "outputs"]:
        if field in requirements:
            if not isinstance(requirements[field], list):
                errors.append(f"{field} must be an array")

    # Validate triggers
    if "triggers" in requirements:
        triggers = requirements["triggers"]
        if not isinstance(triggers, dict):
            errors.append("triggers must be a dictionary")
        elif "type" not in triggers:
            errors.append("triggers.type is required")
        elif triggers["type"] not in ["manual", "schedule", "event", "continuous"]:
            errors.append("Invalid trigger type")

    # Validate constraints
    if "constraints" in requirements:
        constraints = requirements["constraints"]
        if "max_execution_time" in constraints:
            if not isinstance(constraints["max_execution_time"], int):
                errors.append("constraints.max_execution_time must be integer")
            elif constraints["max_execution_time"] > 900:  # 15 minutes
                warnings.append("Execution time > 15 minutes may timeout")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_json_string(json_string: str) -> ValidationResult:
    """Validate JSON string can be parsed"""
    try:
        json.loads(json_string)
        return ValidationResult(is_valid=True)
    except json.JSONDecodeError as e:
        return ValidationResult(
            is_valid=False,
            errors=[f"Invalid JSON: {e}"]
        )
```

### Acceptance Criteria
- ✅ Email validation
- ✅ Code security validation (dangerous patterns)
- ✅ Requirements JSON validation
- ✅ JSON parsing validation
- ✅ Returns ValidationResult with errors/warnings

---

## TASK-105: Create Database Initialization Script ⬜
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Dependencies**: TASK-102

### Description
Create a script to initialize the database and optionally seed with test data.

### Implementation Details

**File to Create**: `scripts/init_db.py`

```python
"""
Database initialization script
Creates tables and optionally seeds test data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "interlevel-poc"))

from src.models.database import init_db, create_test_user, SessionLocal
from src.models.database import User, Agent, Execution, Session
from config.settings import settings
import json


def seed_test_data():
    """Seed database with test data"""
    db = SessionLocal()

    try:
        # Create test user
        print("Creating test user...")
        test_user = User(
            email="test@interlevel.com",
            token_balance=100000
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Test user created: {test_user.user_id}")

        # Create sample agent
        print("Creating sample agent...")
        sample_agent = Agent(
            user_id=test_user.user_id,
            name="Weather Checker",
            description="Checks weather API and logs results",
            requirements_json={
                "purpose": "Check weather and alert if rain",
                "inputs": [{"name": "location", "type": "string"}],
                "outputs": [{"name": "alert", "type": "string"}],
                "triggers": {"type": "manual"}
            },
            status="draft"
        )
        db.add(sample_agent)
        db.commit()
        db.refresh(sample_agent)
        print(f"✅ Sample agent created: {sample_agent.agent_id}")

        print("\n✅ Test data seeded successfully")
        print(f"   User ID: {test_user.user_id}")
        print(f"   Email: {test_user.email}")
        print(f"   Token Balance: {test_user.token_balance}")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  Interlevel POC - Database Initialization")
    print("=" * 60)
    print()

    # Initialize database
    print("Creating database schema...")
    init_db()

    # Ask to seed test data
    response = input("\nSeed with test data? (y/n): ")
    if response.lower() == 'y':
        seed_test_data()

    print("\n✅ Database initialization complete!")
    print(f"   Database location: {settings.DATABASE_URL}")
```

### Acceptance Criteria
- ✅ Creates all database tables
- ✅ Optionally seeds test data
- ✅ Creates test user with token balance
- ✅ Creates sample agent
- ✅ Prints success messages with IDs
- ✅ Handles errors gracefully

### Testing
```bash
cd interlevel-poc
python ../scripts/init_db.py
```

---

## TASK-106: Create Project README ⬜
**Priority**: LOW
**Estimated Time**: 15 minutes
**Dependencies**: All Phase 1 tasks

### Description
Create a comprehensive README for the POC project with setup instructions.

### Implementation Details

**File to Create**: `interlevel-poc/README.md`
(This is already created by setup script, this task is to verify and enhance it)

### Acceptance Criteria
- ✅ Clear project description
- ✅ Setup instructions
- ✅ Development workflow
- ✅ Testing instructions
- ✅ Links to other documentation

---

# PHASE 2: LLM INTEGRATION (Days 4-5)

## TASK-201: Create LLM Client Abstraction ⬜
**Priority**: HIGH
**Estimated Time**: 2 hours
**Dependencies**: TASK-101, TASK-103

### Description
Create an abstraction layer for LLM providers (Ollama, OpenAI, Anthropic) with a unified interface.

### Implementation Details

**File to Create**: `src/llm/client.py`

```python
"""
LLM client abstraction layer
Provides unified interface for different LLM providers
"""
from typing import List, Dict, Optional
from config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Unified LLM client interface"""

    def __init__(self, provider: Optional[str] = None):
        """Initialize LLM client with specified provider"""
        self.provider = provider or settings.LLM_PROVIDER
        self._client = None
        self._init_provider()

    def _init_provider(self):
        """Initialize the appropriate provider client"""
        logger.info(f"Initializing LLM provider: {self.provider}")

        if self.provider == "ollama":
            from src.llm.providers.ollama import OllamaProvider
            self._client = OllamaProvider()
        elif self.provider == "openai":
            from src.llm.providers.openai import OpenAIProvider
            self._client = OpenAIProvider()
        elif self.provider == "anthropic":
            from src.llm.providers.anthropic import AnthropicProvider
            self._client = AnthropicProvider()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

        logger.info(f"LLM provider initialized: {self.provider}")

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text from a prompt

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Generated text
        """
        logger.debug("Generating text", prompt_length=len(prompt), max_tokens=max_tokens)

        try:
            response = self._client.generate(prompt, max_tokens, temperature)
            logger.debug("Text generated successfully", response_length=len(response))
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Chat-style interaction with messages

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Assistant's response
        """
        logger.debug("Chat interaction", num_messages=len(messages))

        try:
            response = self._client.chat(messages, max_tokens, temperature)
            logger.debug("Chat response generated", response_length=len(response))
            return response
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        # This is a rough approximation
        return len(text) // 4

    @property
    def model_name(self) -> str:
        """Get current model name"""
        return self._client.model_name if hasattr(self._client, 'model_name') else "unknown"


class BaseLLMProvider:
    """Base class for LLM providers"""

    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        raise NotImplementedError

    def chat(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        raise NotImplementedError
```

### Acceptance Criteria
- ✅ Unified interface for all providers
- ✅ generate() and chat() methods
- ✅ Token counting (estimation)
- ✅ Error handling and logging
- ✅ Provider auto-detection from settings

---

## TASK-202: Implement Ollama Provider ⬜
**Priority**: HIGH
**Estimated Time**: 1 hour
**Dependencies**: TASK-201

### Description
Implement Ollama-specific provider for local LLM inference.

### Implementation Details

**File to Create**: `src/llm/providers/ollama.py`

```python
"""
Ollama LLM provider implementation
Uses local Ollama server for inference
"""
from typing import List, Dict
import requests
from config.settings import settings
from src.llm.client import BaseLLMProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""

    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        self.model_name = self.model

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"Connected to Ollama server at {self.host}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise ConnectionError(f"Cannot connect to Ollama at {self.host}. Is the server running?")

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using Ollama"""
        url = f"{self.host}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise TimeoutError("Ollama generation timed out after 120 seconds")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Chat using Ollama"""
        url = f"{self.host}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except requests.exceptions.Timeout:
            logger.error("Ollama chat timed out")
            raise TimeoutError("Ollama chat timed out after 120 seconds")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama chat failed: {e}")
            raise
```

### Acceptance Criteria
- ✅ Connects to local Ollama server
- ✅ Implements generate() method
- ✅ Implements chat() method
- ✅ Handles timeouts and errors
- ✅ Tests connection on initialization
- ✅ Uses settings for host and model

---

## TASK-203: Implement OpenAI Provider (Optional) ⬜
**Priority**: LOW
**Estimated Time**: 1 hour
**Dependencies**: TASK-201

### Description
Implement OpenAI API provider as an alternative to Ollama.

### Implementation Details

**File to Create**: `src/llm/providers/openai.py`

```python
"""
OpenAI LLM provider implementation
"""
from typing import List, Dict
from openai import OpenAI
from config.settings import settings
from src.llm.client import BaseLLMProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider"""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.model_name = self.model

        logger.info(f"OpenAI provider initialized with model: {self.model}")

    def generate(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Generate text using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Chat using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat failed: {e}")
            raise
```

### Acceptance Criteria
- ✅ Connects to OpenAI API
- ✅ Implements generate() and chat()
- ✅ API key validation
- ✅ Error handling

---

## TASK-204: Create LLM Testing Script ⬜
**Priority**: HIGH
**Estimated Time**: 30 minutes
**Dependencies**: TASK-201, TASK-202

### Description
Create a script to test LLM connection and basic functionality.

### Implementation Details

**File to Create**: `scripts/test_llm.py`

```python
"""
Test LLM provider connections
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "interlevel-poc"))

from src.llm.client import LLMClient
from config.settings import settings


def test_generate():
    """Test basic text generation"""
    print("\n" + "="*60)
    print("Testing Text Generation")
    print("="*60)

    client = LLMClient()
    print(f"Provider: {client.provider}")
    print(f"Model: {client.model_name}")

    prompt = "Write a Python function that adds two numbers. Include docstring."
    print(f"\nPrompt: {prompt}\n")

    response = client.generate(prompt, max_tokens=500)
    print(f"Response:\n{response}\n")

    print("✅ Generation test passed")


def test_chat():
    """Test chat-style interaction"""
    print("\n" + "="*60)
    print("Testing Chat Interaction")
    print("="*60)

    client = LLMClient()

    messages = [
        {"role": "system", "content": "You are a helpful Python programming assistant."},
        {"role": "user", "content": "How do I read a JSON file in Python?"}
    ]

    print("Messages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")

    response = client.chat(messages, max_tokens=300)
    print(f"\nResponse:\n{response}\n")

    print("✅ Chat test passed")


def test_token_counting():
    """Test token counting"""
    print("\n" + "="*60)
    print("Testing Token Counting")
    print("="*60)

    client = LLMClient()

    text = "This is a test sentence to count tokens."
    tokens = client.count_tokens(text)

    print(f"Text: {text}")
    print(f"Estimated tokens: {tokens}")

    print("✅ Token counting test passed")


if __name__ == "__main__":
    print("="*60)
    print("  Interlevel POC - LLM Provider Test")
    print("="*60)
    print(f"  Provider: {settings.LLM_PROVIDER}")
    print("="*60)

    try:
        test_generate()
        test_chat()
        test_token_counting()

        print("\n" + "="*60)
        print("  ✅ All LLM tests passed!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
```

### Acceptance Criteria
- ✅ Tests text generation
- ✅ Tests chat interaction
- ✅ Tests token counting
- ✅ Clear output formatting
- ✅ Error handling

### Testing
```bash
cd interlevel-poc
python ../scripts/test_llm.py
```

---

# PHASE 3: CLARIFICATION SERVICE (Days 6-7)

## TASK-301: Create Clarification Service ⬜
**Priority**: HIGH
**Estimated Time**: 3 hours
**Dependencies**: TASK-102, TASK-201

### Description
Implement the interactive clarification service that asks targeted questions to refine user intent.

### Implementation Details

**File to Create**: `src/services/clarification.py`

```python
"""
Clarification Service - Interactive requirements gathering
Asks targeted questions to refine user intent into detailed requirements
"""
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta

from src.llm.client import LLMClient
from src.models.database import SessionLocal, Session, User
from src.models.schemas import Message, ConversationState
from src.utils.logger import get_logger

logger = get_logger(__name__)


CLARIFICATION_SYSTEM_PROMPT = """You are an expert AI assistant helping users define requirements for autonomous agents.

Your goal is to gather complete information about:
1. **Task Purpose**: What should the agent accomplish?
2. **Inputs**: What data/information does it need?
3. **Outputs**: What should it produce/return?
4. **Triggers**: When/how should it run? (manual, scheduled, event-based)
5. **Platforms**: What APIs/services will it interact with?
6. **Constraints**: Time limits, token budgets, rate limits
7. **Success Criteria**: How do we know it worked?
8. **Failure Handling**: What happens if it fails?

**RULES**:
- Ask ONE specific question at a time
- Be direct and actionable
- Avoid generic questions like "anything else?"
- Focus on technical details (URLs, authentication, data formats)
- When you have complete information, respond EXACTLY with: "REQUIREMENTS_COMPLETE"

**CURRENT FOCUS**: Start by understanding the core task, then systematically gather details.
"""


class ClarificationService:
    """Service for interactive requirements clarification"""

    def __init__(self):
        self.llm = LLMClient()
        self.db = SessionLocal()
        logger.info("Clarification service initialized")

    def start_session(self, user_id: str, initial_task: str) -> Dict:
        """
        Start a new clarification session

        Args:
            user_id: User ID
            initial_task: User's initial task description

        Returns:
            Session info with first question
        """
        logger.info("Starting clarification session", user_id=user_id)

        # Build conversation
        conversation = [
            {"role": "system", "content": CLARIFICATION_SYSTEM_PROMPT},
            {"role": "user", "content": f"I want to create an agent that: {initial_task}"}
        ]

        # Get first clarifying question
        try:
            response = self.llm.chat(conversation, max_tokens=500, temperature=0.7)
            conversation.append({"role": "assistant", "content": response})

            # Create session in database
            session = Session(
                user_id=user_id,
                conversation_state=conversation,
                status="active",
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )

            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

            logger.info("Clarification session started",
                       session_id=session.session_id,
                       user_id=user_id)

            return {
                "session_id": session.session_id,
                "status": "active",
                "question": response,
                "message_count": len(conversation)
            }

        except Exception as e:
            logger.error(f"Failed to start session: {e}", user_id=user_id)
            self.db.rollback()
            raise

    def continue_session(self, session_id: str, user_response: str) -> Dict:
        """
        Continue an existing clarification session

        Args:
            session_id: Session ID
            user_response: User's answer to the previous question

        Returns:
            Next question or completion status
        """
        logger.info("Continuing clarification session", session_id=session_id)

        # Load session
        session = self.db.query(Session).filter(Session.session_id == session_id).first()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.status != "active":
            raise ValueError(f"Session is not active: {session.status}")

        if session.is_expired:
            session.status = "expired"
            self.db.commit()
            raise ValueError("Session has expired")

        # Load conversation
        conversation = session.conversation_state

        # Add user response
        conversation.append({"role": "user", "content": user_response})

        # Get next question
        try:
            response = self.llm.chat(conversation, max_tokens=500, temperature=0.7)
            conversation.append({"role": "assistant", "content": response})

            # Check if complete
            if "REQUIREMENTS_COMPLETE" in response:
                session.status = "complete"
                logger.info("Clarification complete", session_id=session_id)

                # Update session
                session.conversation_state = conversation
                self.db.commit()

                return {
                    "session_id": session_id,
                    "status": "complete",
                    "message": "Requirements gathering complete!",
                    "conversation": conversation,
                    "message_count": len(conversation)
                }

            # Update session
            session.conversation_state = conversation
            self.db.commit()

            logger.info("Next question generated",
                       session_id=session_id,
                       message_count=len(conversation))

            return {
                "session_id": session_id,
                "status": "continue",
                "question": response,
                "message_count": len(conversation)
            }

        except Exception as e:
            logger.error(f"Failed to continue session: {e}", session_id=session_id)
            self.db.rollback()
            raise

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session details"""
        session = self.db.query(Session).filter(Session.session_id == session_id).first()

        if not session:
            return None

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "message_count": len(session.conversation_state) if session.conversation_state else 0
        }

    def abandon_session(self, session_id: str):
        """Mark session as abandoned"""
        session = self.db.query(Session).filter(Session.session_id == session_id).first()

        if session:
            session.status = "abandoned"
            self.db.commit()
            logger.info("Session abandoned", session_id=session_id)

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
```

### Acceptance Criteria
- ✅ start_session() creates new session
- ✅ continue_session() continues conversation
- ✅ Detects completion ("REQUIREMENTS_COMPLETE")
- ✅ Stores conversation in database
- ✅ Session expiration handling
- ✅ Error handling and logging

---

## TASK-302: Create Clarification CLI ⬜
**Priority**: HIGH
**Estimated Time**: 1 hour
**Dependencies**: TASK-301

### Description
Create a command-line interface for testing the clarification service.

### Implementation Details

**File to Create**: `cli/clarify.py`

```python
"""
CLI tool for testing clarification service
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.clarification import ClarificationService
from src.models.database import init_db, create_test_user


def run_clarification_cli():
    """Run interactive clarification CLI"""
    print("="*70)
    print("  INTERLEVEL - Agent Requirements Clarification")
    print("="*70)
    print()
    print("This tool will help you define your agent by asking targeted questions.")
    print("Type 'quit' at any time to exit.")
    print()

    # Initialize
    service = ClarificationService()

    # Get or create test user
    user_id = "test-user-001"

    # Get initial task
    print("Describe what you want your agent to do:")
    print("(Be as detailed or as brief as you like - we'll clarify together)")
    print()
    task = input("Task: ")

    if task.lower() == 'quit':
        print("\nGoodbye!")
        return

    # Start session
    print("\n" + "-"*70)
    try:
        result = service.start_session(user_id, task)
        session_id = result["session_id"]

        print(f"\nSession ID: {session_id}")
        print(f"\n🤖 {result['question']}\n")

        # Continue conversation
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() == 'quit':
                service.abandon_session(session_id)
                print("\nSession abandoned. Goodbye!")
                break

            if not user_input:
                print("Please provide a response.\n")
                continue

            # Continue session
            result = service.continue_session(session_id, user_input)

            if result["status"] == "complete":
                print("\n" + "="*70)
                print("  ✅ REQUIREMENTS GATHERING COMPLETE!")
                print("="*70)
                print(f"\nSession ID: {session_id}")
                print(f"Total messages: {result['message_count']}")
                print("\nYou can now proceed to generate the agent requirements JSON.")
                print(f"Use: python cli/generate_requirements.py {session_id}")
                break

            print(f"\n🤖 {result['question']}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Ensure database exists
    init_db()

    try:
        run_clarification_cli()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled. Goodbye!")
```

### Acceptance Criteria
- ✅ Interactive Q&A flow
- ✅ Creates session and continues conversation
- ✅ Handles user input
- ✅ Detects completion
- ✅ Allows quitting at any time
- ✅ Clear UI with formatting

### Testing
```bash
cd interlevel-poc
python cli/clarify.py
```

---

## TASK-303: Create Clarification Unit Tests ⬜
**Priority**: MEDIUM
**Estimated Time**: 1 hour
**Dependencies**: TASK-301

### Description
Create unit tests for the clarification service.

### Implementation Details

**File to Create**: `tests/unit/test_clarification.py`

```python
"""
Unit tests for clarification service
"""
import pytest
from src.services.clarification import ClarificationService
from src.models.database import init_db, SessionLocal, Session, User


@pytest.fixture(scope="module")
def setup_db():
    """Setup test database"""
    init_db()
    yield
    # Cleanup after tests


@pytest.fixture
def test_user():
    """Create test user"""
    db = SessionLocal()
    user = User(email="test@example.com", token_balance=10000)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.close()


@pytest.fixture
def service():
    """Create clarification service"""
    return ClarificationService()


def test_start_session(setup_db, service, test_user):
    """Test starting a clarification session"""
    result = service.start_session(
        test_user.user_id,
        "Create an agent that checks weather"
    )

    assert "session_id" in result
    assert result["status"] == "active"
    assert "question" in result
    assert len(result["question"]) > 0


def test_continue_session(setup_db, service, test_user):
    """Test continuing a session"""
    # Start session
    start_result = service.start_session(
        test_user.user_id,
        "Monitor my website uptime"
    )

    session_id = start_result["session_id"]

    # Continue session
    continue_result = service.continue_session(
        session_id,
        "Check https://example.com every 5 minutes"
    )

    assert continue_result["status"] in ["continue", "complete"]
    assert "question" in continue_result or continue_result["status"] == "complete"


def test_get_session(setup_db, service, test_user):
    """Test retrieving session details"""
    # Create session
    start_result = service.start_session(
        test_user.user_id,
        "Test task"
    )

    session_id = start_result["session_id"]

    # Get session
    session_info = service.get_session(session_id)

    assert session_info is not None
    assert session_info["session_id"] == session_id
    assert session_info["user_id"] == test_user.user_id
    assert session_info["status"] == "active"


def test_invalid_session(setup_db, service):
    """Test handling of invalid session ID"""
    with pytest.raises(ValueError):
        service.continue_session("invalid-session-id", "test response")
```

### Acceptance Criteria
- ✅ Tests session creation
- ✅ Tests session continuation
- ✅ Tests session retrieval
- ✅ Tests error handling
- ✅ Uses fixtures for setup
- ✅ All tests pass

---

## TASK-304: Create Clarification Service Documentation ⬜
**Priority**: LOW
**Estimated Time**: 30 minutes
**Dependencies**: TASK-301

### Description
Document the clarification service API and usage.

### Implementation Details

Add comprehensive docstrings and create usage examples in the code.

### Acceptance Criteria
- ✅ All public methods documented
- ✅ Usage examples provided
- ✅ Parameter descriptions
- ✅ Return value descriptions

---

## TASK-305: Add Session Management Endpoints (Optional) ⬜
**Priority**: LOW
**Estimated Time**: 1 hour
**Dependencies**: TASK-301

### Description
Add REST API endpoints for managing clarification sessions (for future web UI).

### Implementation Details

**File to Create**: `src/api/routes/sessions.py`

(Implementation deferred until API layer is built in Phase 7)

---

# PHASE 4: REQUIREMENTS MODEL (Days 1-2 of Week 2)

## TASK-401: Create Agent Requirements Model ⬜
**Priority**: HIGH
**Estimated Time**: 3 hours
**Dependencies**: TASK-301

### Description
Implement the service that converts completed clarification conversations into structured JSON requirements.

### Implementation Details

**File to Create**: `src/services/agent_req.py`

```python
"""
Agent Requirements Model
Converts clarification conversations into structured JSON specifications
"""
from typing import Dict, Any, List
import json
import uuid
from datetime import datetime

from src.llm.client import LLMClient
from src.models.database import SessionLocal, Session, Agent
from src.utils.logger import get_logger
from src.utils.validators import validate_requirements_json, validate_json_string
from config.settings import settings

logger = get_logger(__name__)


REQUIREMENTS_EXTRACTION_PROMPT = """You are an expert at extracting structured requirements from conversations.

Based on the following conversation between a user and an assistant, extract a complete requirements document in JSON format.

**OUTPUT ONLY VALID JSON** with this EXACT structure:

```json
{
  "agent_id": "GENERATE_UUID_HERE",
  "version": "1.0",
  "metadata": {
    "name": "Short descriptive agent name",
    "description": "Brief description of what the agent does",
    "created_at": "ISO8601_TIMESTAMP",
    "tags": ["tag1", "tag2"]
  },
  "purpose": "Clear statement of the agent's primary objective",
  "inputs": [
    {
      "name": "input_name",
      "type": "string|integer|boolean|object|array",
      "source": "user|api|file|database|environment",
      "required": true,
      "description": "What this input is for"
    }
  ],
  "outputs": [
    {
      "name": "output_name",
      "type": "string|integer|boolean|object|array",
      "destination": "console|api|file|database|user",
      "description": "What this output represents"
    }
  ],
  "triggers": {
    "type": "manual|schedule|event|continuous",
    "config": {
      "schedule": "cron_expression (if schedule type)",
      "event_source": "api|webhook|file (if event type)",
      "interval_seconds": 300
    }
  },
  "platforms": [
    {
      "name": "REST API|GraphQL|Database|etc",
      "base_url": "https://api.example.com",
      "authentication": "api_key|oauth|bearer|none",
      "endpoints": ["GET /endpoint1", "POST /endpoint2"]
    }
  ],
  "constraints": {
    "max_execution_time": 300,
    "token_budget": 5000,
    "rate_limits": {
      "requests_per_minute": 60
    },
    "timeout": 30
  },
  "success_criteria": [
    "Specific measurable criterion 1",
    "Specific measurable criterion 2"
  ],
  "failure_handling": {
    "retry_policy": {
      "max_retries": 3,
      "backoff_seconds": 5
    },
    "notification": {
      "method": "log|email|webhook",
      "destination": "where to notify"
    },
    "fallback_action": "what to do if all retries fail"
  },
  "permissions": {
    "allowed_actions": [
      "http_request",
      "read_file",
      "write_log"
    ],
    "disallowed_actions": [
      "system_command",
      "file_write",
      "database_write"
    ],
    "required_secrets": ["API_KEY", "DATABASE_URL"]
  }
}
```

**CONVERSATION:**
{conversation}

**CRITICAL RULES:**
1. Output ONLY the JSON, no explanations before or after
2. Use actual values from the conversation, not placeholders
3. Generate a real UUID for agent_id
4. Use current timestamp for created_at
5. Be specific - no generic descriptions
6. If information wasn't discussed, use sensible defaults
7. Validate that all required fields are present

Now output the JSON:
"""


class AgentRequirementModel:
    """Service for generating structured requirements from conversations"""

    def __init__(self):
        self.llm = LLMClient()
        self.db = SessionLocal()
        logger.info("Agent Requirement Model initialized")

    def generate_requirements(self, session_id: str) -> Dict[str, Any]:
        """
        Generate requirements JSON from a completed clarification session

        Args:
            session_id: Completed clarification session ID

        Returns:
            Structured requirements dictionary
        """
        logger.info("Generating requirements", session_id=session_id)

        # Load session
        session = self.db.query(Session).filter(Session.session_id == session_id).first()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.status != "complete":
            raise ValueError(f"Session is not complete. Status: {session.status}")

        # Format conversation
        conversation = session.conversation_state
        conv_text = self._format_conversation(conversation)

        # Generate requirements
        prompt = REQUIREMENTS_EXTRACTION_PROMPT.format(conversation=conv_text)

        try:
            response = self.llm.generate(prompt, max_tokens=2000, temperature=0.3)

            # Extract JSON from response
            requirements = self._extract_json(response)

            # Validate requirements
            validation = validate_requirements_json(requirements)

            if not validation.is_valid:
                logger.error("Generated requirements invalid",
                           errors=validation.errors)
                raise ValueError(f"Invalid requirements: {', '.join(validation.errors)}")

            if validation.warnings:
                logger.warning("Requirements validation warnings",
                             warnings=validation.warnings)

            # Save to file
            filepath = self.save_requirements(requirements)

            logger.info("Requirements generated successfully",
                       session_id=session_id,
                       agent_id=requirements.get("agent_id"),
                       filepath=filepath)

            return {
                "requirements": requirements,
                "filepath": filepath,
                "session_id": session_id,
                "warnings": validation.warnings
            }

        except Exception as e:
            logger.error(f"Failed to generate requirements: {e}",
                        session_id=session_id)
            raise

    def _format_conversation(self, conversation: List[Dict]) -> str:
        """Format conversation for prompt"""
        formatted = []

        for msg in conversation:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Skip system messages
            if role == "system":
                continue

            formatted.append(f"{role.upper()}: {content}")

        return "\n\n".join(formatted)

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        # Try to find JSON in response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")

        json_str = response[json_start:json_end]

        # Validate JSON syntax
        validation = validate_json_string(json_str)
        if not validation.is_valid:
            raise ValueError(f"Invalid JSON: {validation.errors[0]}")

        try:
            requirements = json.loads(json_str)

            # Ensure agent_id and timestamp are set
            if "agent_id" not in requirements or requirements["agent_id"] == "GENERATE_UUID_HERE":
                requirements["agent_id"] = str(uuid.uuid4())

            if "metadata" not in requirements:
                requirements["metadata"] = {}

            requirements["metadata"]["created_at"] = datetime.utcnow().isoformat()

            return requirements

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON structure: {e}")

    def save_requirements(self, requirements: Dict[str, Any]) -> str:
        """
        Save requirements JSON to file

        Args:
            requirements: Requirements dictionary

        Returns:
            File path where requirements were saved
        """
        agent_id = requirements.get("agent_id")

        if not agent_id:
            raise ValueError("Requirements must have an agent_id")

        # Create filename
        requirements_dir = settings.get_absolute_path(settings.REQUIREMENTS_DIR)
        requirements_dir.mkdir(parents=True, exist_ok=True)

        filepath = requirements_dir / f"{agent_id}.json"

        # Write to file
        with open(filepath, 'w') as f:
            json.dump(requirements, f, indent=2)

        logger.info(f"Requirements saved to {filepath}")

        return str(filepath)

    def load_requirements(self, agent_id: str) -> Dict[str, Any]:
        """Load requirements from file"""
        requirements_dir = settings.get_absolute_path(settings.REQUIREMENTS_DIR)
        filepath = requirements_dir / f"{agent_id}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"Requirements file not found: {filepath}")

        with open(filepath, 'r') as f:
            return json.load(f)

    def create_agent_record(self, requirements: Dict[str, Any], user_id: str) -> Agent:
        """
        Create an agent database record from requirements

        Args:
            requirements: Requirements dictionary
            user_id: User ID

        Returns:
            Created Agent instance
        """
        agent_id = requirements.get("agent_id")
        metadata = requirements.get("metadata", {})

        agent = Agent(
            agent_id=agent_id,
            user_id=user_id,
            name=metadata.get("name", "Unnamed Agent"),
            description=metadata.get("description", ""),
            requirements_json=requirements,
            status="requirements_complete"
        )

        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)

        logger.info("Agent record created", agent_id=agent_id, user_id=user_id)

        return agent

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
```

### Acceptance Criteria
- ✅ generate_requirements() converts conversation to JSON
- ✅ Validates generated JSON structure
- ✅ Saves requirements to file
- ✅ Creates agent database record
- ✅ Handles errors gracefully
- ✅ Comprehensive logging

---

## TASK-402: Create Requirements Generation CLI ⬜
**Priority**: HIGH
**Estimated Time**: 45 minutes
**Dependencies**: TASK-401

### Description
Create CLI tool to generate requirements from a completed session.

### Implementation Details

**File to Create**: `cli/generate_requirements.py`

```python
"""
CLI tool for generating requirements JSON from clarification session
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.agent_req import AgentRequirementModel
from src.models.database import init_db


def generate_requirements_cli():
    """Generate requirements from session ID"""
    print("="*70)
    print("  INTERLEVEL - Generate Agent Requirements")
    print("="*70)
    print()

    # Get session ID
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
    else:
        session_id = input("Enter session ID: ").strip()

    if not session_id:
        print("❌ Session ID required")
        return

    print(f"\nGenerating requirements for session: {session_id}")
    print("-"*70)

    # Generate requirements
    service = AgentRequirementModel()

    try:
        result = service.generate_requirements(session_id)

        requirements = result["requirements"]
        filepath = result["filepath"]

        print("\n✅ Requirements generated successfully!")
        print(f"\nFile saved: {filepath}")
        print(f"Agent ID: {requirements.get('agent_id')}")
        print(f"Agent Name: {requirements.get('metadata', {}).get('name')}")

        if result.get("warnings"):
            print("\n⚠️  Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")

        print("\n" + "="*70)
        print("  Requirements JSON")
        print("="*70)
        print(json.dumps(requirements, indent=2))
        print("="*70)

        print("\nNext step:")
        print(f"Generate agent code: python cli/generate_code.py {requirements.get('agent_id')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    init_db()

    try:
        generate_requirements_cli()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
```

### Acceptance Criteria
- ✅ Accepts session ID as argument or prompt
- ✅ Generates requirements JSON
- ✅ Displays formatted output
- ✅ Shows file path
- ✅ Suggests next step

### Testing
```bash
cd interlevel-poc
python cli/generate_requirements.py <session-id>
```

---

## TASK-403: Create Requirements Unit Tests ⬜
**Priority**: MEDIUM
**Estimated Time**: 1 hour
**Dependencies**: TASK-401

### Description
Create unit tests for the requirements model service.

### Implementation Details

**File to Create**: `tests/unit/test_agent_req.py`

```python
"""
Unit tests for agent requirements model
"""
import pytest
import json
from src.services.agent_req import AgentRequirementModel
from src.services.clarification import ClarificationService
from src.models.database import init_db, SessionLocal, User


@pytest.fixture(scope="module")
def setup_db():
    """Setup test database"""
    init_db()
    yield


@pytest.fixture
def test_user():
    """Create test user"""
    db = SessionLocal()
    user = User(email="test@example.com", token_balance=10000)
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

    result = service.generate_requirements(completed_session)

    assert "requirements" in result
    assert "filepath" in result
    assert "agent_id" in result["requirements"]
    assert "metadata" in result["requirements"]
    assert "purpose" in result["requirements"]


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
```

### Acceptance Criteria
- ✅ Tests requirements generation
- ✅ Tests file save/load
- ✅ Tests agent record creation
- ✅ All tests pass

---

## TASK-404: Add Requirements Validation Enhancement ⬜
**Priority**: LOW
**Estimated Time**: 1 hour
**Dependencies**: TASK-401

### Description
Enhance requirements validation with more comprehensive checks.

### Implementation Details

Add more validation rules to `src/utils/validators.py`:
- Check for realistic constraints
- Validate URL formats
- Check for required secrets
- Validate trigger configurations

### Acceptance Criteria
- ✅ Additional validation rules implemented
- ✅ Tests updated
- ✅ Documentation updated

---

# PHASE 5: UNIVERSAL EXECUTOR (Days 3-5 of Week 2)

## TASK-501: Create Universal Executor Service ⬜
**Priority**: HIGH
**Estimated Time**: 4 hours
**Dependencies**: TASK-401

### Description
Implement the service that generates executable Python code from requirements JSON.

### Implementation Details

**File to Create**: `src/services/executor.py`

**(Implementation will be ~500+ lines - see POC_Local_Plan.md for reference)**

Key components:
- Code generation from requirements
- Agent template system
- Syntax validation
- Security scanning integration

### Acceptance Criteria
- ✅ generate_agent_code() creates executable Python
- ✅ Validates syntax before returning
- ✅ Uses templates for consistency
- ✅ Includes error handling in generated code
- ✅ Generates proper imports
- ✅ Creates main() function structure

---

## TASK-502: Create Agent Code Templates ⬜
**Priority**: HIGH
**Estimated Time**: 2 hours
**Dependencies**: TASK-501

### Description
Create reusable templates for different agent types.

### Implementation Details

**File to Create**: `agents/templates/base_agent.py.template`
**File to Create**: `agents/templates/api_agent.py.template`
**File to Create**: `agents/templates/scheduled_agent.py.template`

### Acceptance Criteria
- ✅ Base template with standard structure
- ✅ API-calling agent template
- ✅ Scheduled execution template
- ✅ Proper logging and error handling
- ✅ Token tracking hooks

---

## TASK-503: Create Code Generation CLI ⬜
**Priority**: HIGH
**Estimated Time**: 1 hour
**Dependencies**: TASK-501

### Description
Create CLI tool to generate agent code from requirements.

### Implementation Details

**File to Create**: `cli/generate_code.py`

### Acceptance Criteria
- ✅ Accepts agent_id as argument
- ✅ Loads requirements JSON
- ✅ Generates Python code
- ✅ Saves to file
- ✅ Displays generated code
- ✅ Runs security scan

---

## TASK-504: Create Executor Unit Tests ⬜
**Priority**: MEDIUM
**Estimated Time**: 2 hours
**Dependencies**: TASK-501

### Description
Create comprehensive tests for code generation.

### Implementation Details

**File to Create**: `tests/unit/test_executor.py`

### Acceptance Criteria
- ✅ Tests code generation
- ✅ Tests syntax validation
- ✅ Tests security scanning
- ✅ Tests template rendering
- ✅ All tests pass

---

## TASK-505: Add Code Generation Refinement ⬜
**Priority**: LOW
**Estimated Time**: 2 hours
**Dependencies**: TASK-501

### Description
Add refinement loop if generated code has issues.

### Implementation Details

Add retry logic with feedback to LLM if:
- Syntax errors detected
- Security issues found
- Missing required imports

### Acceptance Criteria
- ✅ Retry logic implemented
- ✅ Max retries enforced
- ✅ Feedback loop to LLM
- ✅ Improved success rate

---

# PHASE 6: INJECTOR SERVICE (Days 6-7 of Week 2)

## TASK-601: Create Injector Service ⬜
**Priority**: HIGH
**Estimated Time**: 3 hours
**Dependencies**: TASK-501

### Description
Implement service to deploy and execute agents locally.

### Implementation Details

**File to Create**: `src/services/injector.py`

(See POC_Local_Plan.md for implementation details)

Key features:
- Security validation
- Local deployment (file system)
- Agent execution via subprocess
- Output capture
- Timeout handling

### Acceptance Criteria
- ✅ deploy_agent() validates and prepares code
- ✅ execute_agent() runs as subprocess
- ✅ Captures stdout/stderr
- ✅ Timeout enforcement
- ✅ Error handling
- ✅ Execution logging

---

## TASK-602: Create Agent Execution CLI ⬜
**Priority**: HIGH
**Estimated Time**: 1 hour
**Dependencies**: TASK-601

### Description
Create CLI tool to execute deployed agents.

### Implementation Details

**File to Create**: `cli/run_agent.py`

### Acceptance Criteria
- ✅ Accepts agent_id
- ✅ Executes agent
- ✅ Displays output in real-time
- ✅ Shows execution status
- ✅ Records execution in database

---

## TASK-603: Create Token Manager Service ⬜
**Priority**: MEDIUM
**Estimated Time**: 2 hours
**Dependencies**: TASK-102

### Description
Implement token tracking and budget enforcement.

### Implementation Details

**File to Create**: `src/services/token_manager.py`

### Acceptance Criteria
- ✅ Track tokens per execution
- ✅ Check budget before execution
- ✅ Update token balance
- ✅ Alert on threshold
- ✅ Database integration

---

## TASK-604: Create Injector Unit Tests ⬜
**Priority**: MEDIUM
**Estimated Time**: 1 hour
**Dependencies**: TASK-601

### Description
Create tests for agent deployment and execution.

### Implementation Details

**File to Create**: `tests/unit/test_injector.py`

### Acceptance Criteria
- ✅ Tests deployment validation
- ✅ Tests execution
- ✅ Tests timeout handling
- ✅ Tests error capture

---

# PHASE 7: INTEGRATION (Week 3)

## TASK-701: Create End-to-End CLI ⬜
**Priority**: HIGH
**Estimated Time**: 3 hours
**Dependencies**: All previous tasks

### Description
Create a unified CLI that orchestrates the entire workflow.

### Implementation Details

**File to Create**: `cli/interlevel.py`

Complete workflow:
1. Clarification
2. Requirements generation
3. Code generation
4. Deployment
5. Execution

### Acceptance Criteria
- ✅ Single command workflow
- ✅ Step-by-step progression
- ✅ Clear status updates
- ✅ Error handling at each step
- ✅ Option to pause between steps

---

## TASK-702: Create Integration Tests ⬜
**Priority**: HIGH
**Estimated Time**: 3 hours
**Dependencies**: TASK-701

### Description
Create end-to-end integration tests.

### Implementation Details

**File to Create**: `tests/integration/test_e2e.py`

### Acceptance Criteria
- ✅ Tests complete workflow
- ✅ Tests with different agent types
- ✅ Tests error scenarios
- ✅ All tests pass

---

## TASK-703: Create Flask API (Optional) ⬜
**Priority**: LOW
**Estimated Time**: 4 hours
**Dependencies**: All services

### Description
Create REST API for future web UI integration.

### Implementation Details

**File to Create**: `src/api/app.py`

### Acceptance Criteria
- ✅ CRUD endpoints for agents
- ✅ Session management endpoints
- ✅ Execution endpoints
- ✅ OpenAPI documentation

---

## TASK-704: Create Demo Scenarios ⬜
**Priority**: MEDIUM
**Estimated Time**: 2 hours
**Dependencies**: TASK-701

### Description
Create pre-built demo scenarios for testing.

### Implementation Details

**File to Create**: `scripts/demo_scenarios.py`

Three scenarios:
1. Weather checker
2. API monitor
3. Data transformer

### Acceptance Criteria
- ✅ Automated demo runs
- ✅ All scenarios work
- ✅ Clear output

---

## TASK-705: Create POC Documentation ⬜
**Priority**: MEDIUM
**Estimated Time**: 2 hours
**Dependencies**: All tasks

### Description
Create comprehensive POC documentation.

### Implementation Details

Update README.md with:
- Complete setup guide
- Usage examples
- Troubleshooting
- Next steps

### Acceptance Criteria
- ✅ Clear setup instructions
- ✅ Usage examples
- ✅ Troubleshooting guide
- ✅ Migration path to AWS

---

# Task Dependencies Diagram

```
SETUP-001, SETUP-002
    ↓
TASK-101 (Config)
    ↓
TASK-102 (Database) + TASK-103 (Logging) + TASK-104 (Validators)
    ↓
TASK-105 (Init DB) + TASK-106 (README)
    ↓
TASK-201 (LLM Client)
    ↓
TASK-202 (Ollama) + TASK-203 (OpenAI)
    ↓
TASK-204 (LLM Tests)
    ↓
TASK-301 (Clarification)
    ↓
TASK-302 (Clarify CLI) + TASK-303 (Tests) + TASK-304 (Docs)
    ↓
TASK-401 (Requirements Model)
    ↓
TASK-402 (Req CLI) + TASK-403 (Tests)
    ↓
TASK-501 (Executor)
    ↓
TASK-502 (Templates) + TASK-503 (Code CLI) + TASK-504 (Tests)
    ↓
TASK-601 (Injector) + TASK-603 (Token Manager)
    ↓
TASK-602 (Run CLI) + TASK-604 (Tests)
    ↓
TASK-701 (E2E CLI)
    ↓
TASK-702 (Integration Tests) + TASK-703 (API) + TASK-704 (Demos)
    ↓
TASK-705 (Documentation)
```

---

**Document Version**: 1.0
**Last Updated**: 2026-02-07
**Total Tasks**: 35
**Estimated Total Time**: 15-19 days (1-2 developers)
