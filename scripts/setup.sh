#!/bin/bash
# Interlevel POC - Automated Setup Script (Mac/Linux)
# Create interlevel-poc/ directory structure
# Generate requirements.txt with all dependencies
# Create .env.example and .env files
# Create Python virtual environment (venv/)
# Install all dependencies
# Create all __init__.py files
# Create .gitkeep files for empty dirs
# Generate README.md
#scripts/setup.sh
#scripts/setup.bat
# .gitignore
# interlevel-poc/requirements.txt
# interlevel-poc/.env.example
# interlevel-poc/README.md
# Directory structure (.gitkeep files)

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
pydantic-settings==2.1.0
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

# Logging
LOG_LEVEL=INFO
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

# Create .gitkeep files for empty directories
echo "📄 Creating .gitkeep files..."
touch agents/generated/.gitkeep
touch agents/templates/.gitkeep
touch data/requirements/.gitkeep
touch data/logs/.gitkeep

echo "✅ .gitkeep files created"

# Create README
echo "📝 Creating README.md..."
cat > README.md << 'EOF'
# Interlevel POC - Local Development

## Quick Start

1. Activate virtual environment:
   ```bash
   source venv/bin/activate  # Mac/Linux
   ```

2. Install Ollama (if not already installed):
   ```bash
   # Mac
   brew install ollama

   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. Start Ollama and pull model:
   ```bash
   # Terminal 1: Start Ollama server
   ollama serve

   # Terminal 2: Pull model
   ollama pull codellama
   ```

4. Initialize database:
   ```bash
   python ../scripts/init_db.py
   ```

5. Run tests:
   ```bash
   pytest tests/
   ```

6. Start development:
   - See [../poc_readme.md](../poc_readme.md) for full documentation
   - See [../Implementation_Tasks.md](../Implementation_Tasks.md) for task list

## Project Structure

```
interlevel-poc/
├── src/                    # Source code
│   ├── api/               # Flask API
│   ├── services/          # Business logic
│   ├── models/            # Database models
│   ├── llm/               # LLM providers
│   └── utils/             # Utilities
├── agents/                # Agent code
│   ├── generated/         # Generated agents
│   └── templates/         # Agent templates
├── data/                  # Runtime data
│   ├── interlevel.db      # SQLite database
│   ├── requirements/      # Requirements JSON
│   └── logs/              # Execution logs
├── cli/                   # Command-line tools
├── tests/                 # Unit & integration tests
└── config/                # Configuration
```

## Development Workflow

1. Activate environment: `source venv/bin/activate`
2. Make changes
3. Run tests: `pytest tests/`
4. Format code: `black src/ tests/`
5. Lint: `ruff check src/ tests/`

## Documentation

- [POC README](../poc_readme.md) - Quick start guide
- [Implementation Tasks](../Implementation_Tasks.md) - Detailed task list
- [POC Plan](../POC_Local_Plan.md) - Full POC plan
- [Architecture Plan](../Architecture_Plan.md) - Production architecture
- [Architecture Rules](../Architecture_Rules.md) - Implementation rules

## Next Steps

See [../Implementation_Tasks.md](../Implementation_Tasks.md) for detailed tasks.

Start with Phase 1: Foundation
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
echo "3. Install Ollama:"
echo "   - Mac: brew install ollama"
echo "   - Linux: curl -fsSL https://ollama.ai/install.sh | sh"
echo "4. Start Ollama: ollama serve"
echo "5. Pull model: ollama pull codellama"
echo "6. Initialize database: python ../scripts/init_db.py"
echo ""
echo "See Implementation_Tasks.md for detailed task list"
