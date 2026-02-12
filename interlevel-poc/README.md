# Interlevel POC - Local Development

## Quick Start

1. Activate virtual environment:
   ```bash
   venv\Scripts\activate  # Windows
   ```

2. Install Ollama:
   - Download from: https://ollama.ai/download
   - Or use WSL: curl -fsSL https://ollama.ai/install.sh | sh

3. Start Ollama and pull model:
   ```bash
   # Terminal 1: Start Ollama server
   ollama serve
ECHO is off.
   # Terminal 2: Pull model
   ollama pull codellama
   ```

4. Initialize database:
   ```bash
   python ..\scripts\init_db.py
   ```

5. Run tests:
   ```bash
   pytest tests/
   ```

6. Start development:
   - See [..\poc_readme.md](..\poc_readme.md) for full documentation
   - See [..\Implementation_Tasks.md](..\Implementation_Tasks.md) for task list

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

1. Activate environment: `venv\Scripts\activate`
2. Make changes
3. Run tests: `pytest tests/`
4. Format code: `black src/ tests/`
5. Lint: `ruff check src/ tests/`

## Documentation

- [POC README](..\poc_readme.md) - Quick start guide
- [Implementation Tasks](..\Implementation_Tasks.md) - Detailed task list
- [POC Plan](..\POC_Local_Plan.md) - Full POC plan
- [Architecture Plan](..\Architecture_Plan.md) - Production architecture
- [Architecture Rules](..\Architecture_Rules.md) - Implementation rules

## Next Steps

See [..\Implementation_Tasks.md](..\Implementation_Tasks.md) for detailed tasks.

Start with Phase 1: Foundation
