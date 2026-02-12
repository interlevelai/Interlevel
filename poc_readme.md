# Interlevel POC - Local Development Guide

## 🎯 POC Overview

Build and validate the Interlevel AI Agent Platform **locally** before incurring cloud costs. This POC demonstrates all core functionality using local/open-source alternatives to AWS services.

**Timeline**: 2-4 weeks
**Team**: 1-2 developers
**Cost**: $0-50 (using Ollama - FREE)
**Goal**: Prove the concept works before AWS investment

---

## 🔄 What You Can Build Locally

```
Natural Language Input
    ↓
Clarification Service (Interactive Q&A)
    ↓
Requirements Model (Generate JSON spec)
    ↓
Universal Executor (Generate Python code)
    ↓
Injector Service (Deploy & execute locally)
    ↓
Agent Execution & Results
```

---

## 💰 Cost Comparison

### POC (Local)
| Component | Technology | Cost |
|-----------|-----------|------|
| Compute | Local Python | $0 |
| Database | SQLite | $0 |
| Storage | Filesystem | $0 |
| LLM | **Ollama** | **$0** |
| API | Flask | $0 |
| **TOTAL** | | **$0/month** |

### Production (AWS, 100 users)
| Component | Technology | Cost |
|-----------|-----------|------|
| Compute | Lambda | ~$20 |
| Database | DynamoDB | ~$10 |
| Storage | S3 | ~$5 |
| LLM | Bedrock | ~$100 |
| API | API Gateway | ~$15 |
| **TOTAL** | | **~$150-200/month** |

**💡 Savings during POC**: $150-200/month while validating concept

---

## 🏗️ Local Architecture

### AWS Service Replacements

| AWS Service | Local Alternative | Migration Effort |
|-------------|------------------|------------------|
| **Lambda** | Python scripts | ✅ Low - wrap in handler |
| **DynamoDB** | SQLite | ⚠️ Medium - change queries |
| **S3** | Filesystem | ✅ Low - change I/O calls |
| **Bedrock** | Ollama (local LLM) | ✅ Low - change client |
| **API Gateway** | Flask/FastAPI | ✅ Low - change endpoints |
| **Cognito** | Simple JWT | ⚠️ Medium - add identity mgmt |
| **CloudWatch** | Python logging | ✅ Low - change logger |
| **EventBridge** | Manual/Cron | ✅ Low - change scheduler |
| **Secrets Manager** | .env file | ✅ Low - change config |

---

## 📋 7-Phase Implementation Plan

### Phase 1: Foundation (Days 1-3)
- ✅ Project structure & dependencies
- ✅ SQLite database setup
- ✅ Configuration management
- ✅ Environment setup

### Phase 2: LLM Integration (Days 4-5)
- ✅ Install & configure Ollama
- ✅ LLM abstraction layer
- ✅ Test basic prompting

### Phase 3: Clarification Service (Days 6-7)
- ✅ Interactive Q&A system
- ✅ Multi-turn conversations
- ✅ Session management

### Phase 4: Agent-Requirement Model (Week 2, Days 1-2)
- ✅ Conversation → JSON conversion
- ✅ Requirements validation
- ✅ File storage

### Phase 5: Universal Executor (Week 2, Days 3-5)
- ✅ Python code generation
- ✅ Syntax validation
- ✅ Code templates

### Phase 6: Injector Service (Week 2, Days 6-7)
- ✅ Security scanning
- ✅ Local deployment
- ✅ Agent execution

### Phase 7: Integration (Week 3, Days 1-3)
- ✅ End-to-end CLI workflow
- ✅ Error handling
- ✅ Logging & debugging

---

## 🚀 Quick Start

### 1. Install Ollama
```bash
# Mac
brew install ollama

# Or using curl (Mac/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve

# Pull a code-generation model (in another terminal)
ollama pull codellama    # Recommended for code generation (7GB)
```

### 2. Set Up Project
```bash
cd /Users/pavisivya/eclipse-workspace/Interlevel

# Create POC directory
mkdir interlevel-poc && cd interlevel-poc

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Create requirements.txt
cat > requirements.txt << EOF
flask==3.0.0
flask-cors==4.0.0
pydantic==2.5.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
ollama==0.1.6
pytest==7.4.3
black==23.12.0
ruff==0.1.8
requests==2.31.0
EOF

# Install dependencies
pip install -r requirements.txt
```

### 3. Create .env Configuration
```bash
cat > .env << EOF
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=codellama
SECRET_KEY=dev-secret-change-later
DATABASE_URL=sqlite:///data/interlevel.db
EOF
```

### 4. Create Directory Structure
```bash
mkdir -p src/{api,services,models,llm/providers,utils}
mkdir -p agents/{generated,templates,runtime}
mkdir -p data/{requirements,logs}
mkdir -p tests/{unit,integration}
mkdir -p cli scripts config
```

---

## 📁 Project Structure

```
interlevel-poc/
├── README.md
├── requirements.txt
├── .env
├── config/
│   └── settings.py              # Configuration management
├── src/
│   ├── api/
│   │   ├── app.py               # Flask API
│   │   └── routes/              # API endpoints
│   ├── services/
│   │   ├── clarification.py     # Step 1: Interactive Q&A
│   │   ├── agent_req.py         # Step 2: Generate JSON
│   │   ├── executor.py          # Step 3: Generate code
│   │   ├── injector.py          # Step 4: Deploy & run
│   │   └── token_manager.py     # Token tracking
│   ├── models/
│   │   ├── database.py          # SQLite setup
│   │   └── schemas.py           # Data models
│   ├── llm/
│   │   ├── client.py            # LLM abstraction
│   │   └── providers/
│   │       ├── ollama.py        # Local LLM (FREE)
│   │       ├── openai.py        # OpenAI API
│   │       └── anthropic.py     # Claude API
│   └── utils/
│       └── logger.py
├── agents/
│   └── generated/               # Generated agent code
├── data/
│   ├── interlevel.db            # SQLite database
│   ├── requirements/            # Requirements JSON
│   └── logs/                    # Execution logs
├── cli/
│   └── interlevel_cli.py        # Command-line interface
└── tests/
```

---

## 🎬 Demo Scenarios (Test These)

### Scenario 1: Weather Alert Agent
```
Input: "I want an agent that checks the weather API and logs if it's going to rain"

Flow:
1. Clarification: Which API? When to check? How to alert?
2. Requirements JSON generated
3. Python code created (requests library)
4. Agent executes: Calls OpenWeatherMap API → Logs result
```

### Scenario 2: REST API Monitor
```
Input: "Create an agent that monitors my /health endpoint"

Flow:
1. Clarification: URL? Check frequency? What's a failure?
2. Requirements JSON generated
3. Python code created
4. Agent executes: GET /health → Logs status code
```

### Scenario 3: Data Transformer
```
Input: "Fetch JSON from an API and convert to CSV"

Flow:
1. Clarification: Which API? What fields? Where to save?
2. Requirements JSON generated
3. Python code created (requests + csv)
4. Agent executes: Fetches data → Writes CSV file
```

---

## 🔍 What Gets Validated

By completing this POC, you prove:

- ✅ **LLM Integration**: Can generate code from natural language
- ✅ **Requirements Extraction**: Converts conversations to structured specs
- ✅ **Code Quality**: Generated code is executable and correct
- ✅ **Security**: Basic validation catches dangerous patterns
- ✅ **Token Tracking**: Can estimate costs
- ✅ **End-to-End Flow**: All 4 models work together
- ✅ **Architecture**: Design is sound before cloud investment

---

## 🔄 Migration Path to AWS (Later)

When POC succeeds, migrate one component at a time:

### Week 1: API Layer
```python
# Local: Flask
@app.route('/agents', methods=['POST'])
def create_agent():
    return jsonify(result)

# AWS: Lambda
def lambda_handler(event, context):
    body = json.loads(event['body'])
    return {'statusCode': 200, 'body': json.dumps(result)}
```

### Week 2: Database
```python
# Local: SQLite
cursor.execute("SELECT * FROM agents WHERE user_id=?", (user_id,))

# AWS: DynamoDB
table.query(KeyConditionExpression=Key('user_id').eq(user_id))
```

### Week 3: Storage
```python
# Local: File write
with open(f'agents/{agent_id}.py', 'w') as f:
    f.write(code)

# AWS: S3
s3.put_object(Bucket='interlevel', Key=f'{agent_id}.py', Body=code)
```

### Week 4: LLM
```python
# Local: Ollama
ollama.generate(model='codellama', prompt=prompt)

# AWS: Bedrock
bedrock.invoke_model(modelId='anthropic.claude-v2', body=payload)
```

---

## ✅ POC Success Checklist

Before moving to AWS, ensure:

- [ ] End-to-end workflow works (task → requirements → code → execution)
- [ ] Tested at least 3 different agent types successfully
- [ ] Code generation quality is acceptable (>80% success rate)
- [ ] Security scanning catches obvious issues (eval, exec, os.system)
- [ ] Token tracking is reasonably accurate (±10%)
- [ ] Error handling works (bad input, failed API calls)
- [ ] Performance is acceptable (< 2 minutes total creation time)
- [ ] Team understands the architecture

---

## 📊 Key Metrics to Track

During POC development, measure:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Agent Creation Time** | < 2 min | Start to finish |
| **Code Generation Success** | > 80% | Manual review |
| **Code Execution Success** | > 90% | Run tests |
| **Security Scan Accuracy** | 100% catch dangerous patterns | Test with malicious code |
| **Token Estimation Error** | < 10% | Compare estimate vs actual |

---

## 🎓 Learning Resources

- **Ollama**: https://ollama.ai/
- **Flask**: https://flask.palletsprojects.com/
- **SQLite**: https://www.sqlitetutorial.net/
- **LangChain** (optional): https://python.langchain.com/
- **Full POC Plan**: See [POC_Local_Plan.md](POC_Local_Plan.md)

---

## 📞 Next Steps After POC

### If POC Succeeds ✅
1. Review full [Architecture_Plan.md](Architecture_Plan.md)
2. Set up AWS accounts (dev/staging/prod)
3. Begin migration (start with API layer)
4. Add production features (auth, monitoring)
5. Launch MVP

### If POC Has Issues ⚠️
1. Identify bottlenecks (LLM quality? Architecture?)
2. Refine prompts and templates
3. Consider different LLM provider
4. Adjust requirements or scope
5. Iterate and retest

---

## 🤝 Support

- **Architecture Questions**: See [Architecture_Plan.md](Architecture_Plan.md)
- **Implementation Rules**: See [Architecture_Rules.md](Architecture_Rules.md)
- **Detailed POC Guide**: See [POC_Local_Plan.md](POC_Local_Plan.md)
- **Requirements**: See [requirements.md](requirements.md)

---

**Document Version**: 1.0
**Last Updated**: 2026-02-07
**Status**: Ready to start
**Estimated Completion**: 2-4 weeks
