@echo off
REM Interlevel POC - Automated Setup Script (Windows)

echo ======================================
echo   Interlevel POC - Setup Script
echo ======================================
echo.

REM Check if we're in the right directory
if not exist "requirements.md" (
    echo Error: Please run this script from the Interlevel root directory
    exit /b 1
)

REM Create POC directory
echo Creating project structure...
if not exist "interlevel-poc" mkdir interlevel-poc
cd interlevel-poc

REM Create all subdirectories
mkdir src\api\routes 2>nul
mkdir src\services 2>nul
mkdir src\models 2>nul
mkdir src\llm\providers 2>nul
mkdir src\utils 2>nul
mkdir agents\generated 2>nul
mkdir agents\templates 2>nul
mkdir agents\runtime 2>nul
mkdir data\requirements 2>nul
mkdir data\logs 2>nul
mkdir tests\unit 2>nul
mkdir tests\integration 2>nul
mkdir cli 2>nul
mkdir scripts 2>nul
mkdir config 2>nul

echo Directory structure created

REM Create requirements.txt
echo Creating requirements.txt...
(
echo # Core Framework
echo flask==3.0.0
echo flask-cors==4.0.0
echo pydantic==2.5.0
echo pydantic-settings==2.1.0
echo python-dotenv==1.0.0
echo.
echo # Database
echo sqlalchemy==2.0.23
echo.
echo # LLM Providers
echo ollama==0.1.6
echo openai==1.6.0
echo anthropic==0.8.0
echo.
echo # Utilities
echo requests==2.31.0
echo pyjwt==2.8.0
echo.
echo # Development Tools
echo pytest==7.4.3
echo pytest-cov==4.1.0
echo black==23.12.0
echo ruff==0.1.8
echo mypy==1.7.0
) > requirements.txt

echo requirements.txt created

REM Create .env.example
echo Creating .env.example...
(
echo # LLM Provider Configuration
echo LLM_PROVIDER=ollama  # Options: ollama, openai, anthropic
echo OLLAMA_HOST=http://localhost:11434
echo OLLAMA_MODEL=codellama
echo.
echo # OpenAI ^(if using^)
echo # OPENAI_API_KEY=sk-your-key-here
echo # OPENAI_MODEL=gpt-4-turbo-preview
echo.
echo # Anthropic ^(if using^)
echo # ANTHROPIC_API_KEY=sk-ant-your-key-here
echo # ANTHROPIC_MODEL=claude-3-sonnet-20240229
echo.
echo # Database
echo DATABASE_URL=sqlite:///data/interlevel.db
echo.
echo # API Configuration
echo API_PORT=5000
echo SECRET_KEY=dev-secret-change-in-production
echo.
echo # Agent Configuration
echo MAX_EXECUTION_TIME=300
echo DEFAULT_TOKEN_BUDGET=10000
echo GENERATED_AGENTS_DIR=agents/generated
echo REQUIREMENTS_DIR=data/requirements
echo LOGS_DIR=data/logs
echo.
echo # Logging
echo LOG_LEVEL=INFO
) > .env.example

echo .env.example created

REM Copy to .env if it doesn't exist
if not exist ".env" (
    copy .env.example .env >nul
    echo .env created ^(using default values^)
) else (
    echo .env already exists, skipping
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    echo Make sure Python 3.7+ is installed and in PATH
    exit /b 1
)
echo Virtual environment created

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Some dependencies may have failed to install
)
echo Dependencies installed

REM Create __init__.py files
echo Creating __init__.py files...
type nul > src\__init__.py
type nul > src\api\__init__.py
type nul > src\api\routes\__init__.py
type nul > src\services\__init__.py
type nul > src\models\__init__.py
type nul > src\llm\__init__.py
type nul > src\llm\providers\__init__.py
type nul > src\utils\__init__.py
type nul > tests\__init__.py
type nul > tests\unit\__init__.py
type nul > tests\integration\__init__.py

echo __init__.py files created

REM Create .gitkeep files for empty directories
echo Creating .gitkeep files...
type nul > agents\generated\.gitkeep
type nul > agents\templates\.gitkeep
type nul > data\requirements\.gitkeep
type nul > data\logs\.gitkeep

echo .gitkeep files created

REM Create README
echo Creating README.md...
(
echo # Interlevel POC - Local Development
echo.
echo ## Quick Start
echo.
echo 1. Activate virtual environment:
echo    ```bash
echo    venv\Scripts\activate  # Windows
echo    ```
echo.
echo 2. Install Ollama:
echo    - Download from: https://ollama.ai/download
echo    - Or use WSL: curl -fsSL https://ollama.ai/install.sh ^| sh
echo.
echo 3. Start Ollama and pull model:
echo    ```bash
echo    # Terminal 1: Start Ollama server
echo    ollama serve
echo
echo    # Terminal 2: Pull model
echo    ollama pull codellama
echo    ```
echo.
echo 4. Initialize database:
echo    ```bash
echo    python ..\scripts\init_db.py
echo    ```
echo.
echo 5. Run tests:
echo    ```bash
echo    pytest tests/
echo    ```
echo.
echo 6. Start development:
echo    - See [..\poc_readme.md]^(..\poc_readme.md^) for full documentation
echo    - See [..\Implementation_Tasks.md]^(..\Implementation_Tasks.md^) for task list
echo.
echo ## Project Structure
echo.
echo ```
echo interlevel-poc/
echo ├── src/                    # Source code
echo │   ├── api/               # Flask API
echo │   ├── services/          # Business logic
echo │   ├── models/            # Database models
echo │   ├── llm/               # LLM providers
echo │   └── utils/             # Utilities
echo ├── agents/                # Agent code
echo │   ├── generated/         # Generated agents
echo │   └── templates/         # Agent templates
echo ├── data/                  # Runtime data
echo │   ├── interlevel.db      # SQLite database
echo │   ├── requirements/      # Requirements JSON
echo │   └── logs/              # Execution logs
echo ├── cli/                   # Command-line tools
echo ├── tests/                 # Unit ^& integration tests
echo └── config/                # Configuration
echo ```
echo.
echo ## Development Workflow
echo.
echo 1. Activate environment: `venv\Scripts\activate`
echo 2. Make changes
echo 3. Run tests: `pytest tests/`
echo 4. Format code: `black src/ tests/`
echo 5. Lint: `ruff check src/ tests/`
echo.
echo ## Documentation
echo.
echo - [POC README]^(..\poc_readme.md^) - Quick start guide
echo - [Implementation Tasks]^(..\Implementation_Tasks.md^) - Detailed task list
echo - [POC Plan]^(..\POC_Local_Plan.md^) - Full POC plan
echo - [Architecture Plan]^(..\Architecture_Plan.md^) - Production architecture
echo - [Architecture Rules]^(..\Architecture_Rules.md^) - Implementation rules
echo.
echo ## Next Steps
echo.
echo See [..\Implementation_Tasks.md]^(..\Implementation_Tasks.md^) for detailed tasks.
echo.
echo Start with Phase 1: Foundation
) > README.md

echo README.md created

echo.
echo ======================================
echo   Setup Complete!
echo ======================================
echo.
echo Next steps:
echo 1. cd interlevel-poc
echo 2. venv\Scripts\activate
echo 3. Install Ollama from: https://ollama.ai/download
echo 4. Start Ollama: ollama serve
echo 5. Pull model: ollama pull codellama
echo 6. Initialize database: python ..\scripts\init_db.py
echo.
echo See Implementation_Tasks.md for detailed task list
