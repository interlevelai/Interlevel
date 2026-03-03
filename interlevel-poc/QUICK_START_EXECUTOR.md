# Quick Start: Testing the Universal Executor

**Time**: 5 minutes | **Difficulty**: Easy | **Status**: ✅ Phase 5 Complete

---

## 🎯 What is the Universal Executor?

The Universal Executor converts **requirements JSON** into **executable Python agent code**:

```
Phase 4 Output (Requirements)  →  [Executor]  →  Phase 5 Output (Code)

agent_requirements.json         agent_code.py
├─ Purpose                      ├─ Imports & setup
├─ Inputs/Outputs               ├─ Input validation
├─ APIs & Constraints           ├─ Business logic
├─ Security Rules               ├─ API calls
└─ Success Criteria             └─ Output generation
```

---

## ⚡ 30-Second Test

```bash
cd interlevel-poc

# Run the automated test suite
python cli/test_executor.py
```

**Expected output**:
```
✅ TEST 1: Template Management - PASS
✅ TEST 2: Prompt Building - PASS
✅ TEST 3: Code Extraction - PASS
✅ TEST 4: Syntax Validation - PASS
✅ TEST 5: Security Scanning - PASS
✅ TEST 6: Code Assembly - PASS
✅ TEST 7: Validation Pipeline - PASS
✅ TEST 8: Auth Headers - PASS
✅ TEST 9: File Operations - PASS
✅ TEST 10: Complete Workflow - PASS

Tests Completed: 10
Passed: 10
Success Rate: 100%
```

---

## 🎮 Interactive Testing (2 minutes)

```bash
python cli/executor_interactive.py
```

**Menu**:
```
1. Test Template Selection
2. Test Template Loading
3. Test Code Extraction
4. Test Syntax Validation
5. Test Security Scanning
6. Test Prompt Building
7. Test Code Assembly
8. Test Validation Pipeline
9. Test Authentication Headers
10. Simulate Complete Code Generation
11. Test with Sample Requirements
0. Exit
```

**Try this**:
1. Press `10` → See complete code generation
2. Press `11` → Test with sample agents (Weather, Data Transform, Email)
3. Press `0` → Exit

---

## 🧪 Detailed Unit Tests

```bash
# Test template selection
pytest tests/unit/test_phase5_executor.py::TestTemplateSelection -v

# Test code validation
pytest tests/unit/test_phase5_executor.py::TestValidationPipeline -v

# Test file operations
pytest tests/unit/test_phase5_executor.py::TestFileOperations -v

# Run ALL executor tests
pytest tests/unit/test_phase5_executor.py -v
```

---

## 📊 What Gets Tested

| Feature | Test | Time |
|---------|------|------|
| Template Loading | Load 3 templates | 1s |
| Template Selection | Pick correct template | <1s |
| Code Extraction | Parse LLM responses | 1s |
| Syntax Validation | Check Python syntax | <1s |
| Security Scanning | Detect dangerous patterns | 1s |
| Code Assembly | Combine template + logic | 1s |
| Validation Pipeline | Full validation | 2s |
| Auth Headers | Generate auth code | <1s |
| File Operations | Save generated code | 1s |
| End-to-End | Complete workflow | 3s |

---

## 📋 Test Results Summary

### Automated Test Suite
```
Tests:      10 categories
Passed:     10/10 (100%)
Time:       ~30 seconds
```

### Interactive Tool
```
Tests:      11 interactive scenarios
All:        100% interactive
Time:       Instant feedback
```

### Unit Tests (pytest)
```
Tests:      30+ unit tests
Passed:     30+/30+ (100%)
Coverage:   All executor code
Time:       ~2 minutes
```

---

## ✅ What Works

✅ **Templates**
- Base agent template
- API agent template
- Scheduled agent template

✅ **Code Generation**
- LLM prompt building
- Code extraction from LLM
- Business logic placement

✅ **Validation**
- Syntax checking
- Security scanning
- Code formatting

✅ **Integration**
- File saving
- Database updates
- Error handling

---

## 🚀 Next Steps

After testing Phase 5:

1. **Phase 6**: Injector Service
   - Deploy agents
   - Execute agents
   - Token management

2. **Phase 7**: Integration
   - End-to-end CLI
   - Complete workflow
   - Demo scenarios

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `cli/test_executor.py` | Automated test suite |
| `cli/executor_interactive.py` | Interactive testing tool |
| `src/services/executor.py` | Executor service (637 lines) |
| `src/api/routes/executor.py` | API endpoints (192 lines) |
| `tests/unit/test_phase5_executor.py` | Unit tests (530 lines) |
| `agents/templates/*.template` | 3 agent templates |
| `agents/generated/` | Generated agent code |

---

## 🎓 Understanding the Code Generation Pipeline

### 1. Template Selection
```python
requirements = {"triggers": {"type": "schedule"}, "platforms": [...]}
template = executor._select_template(requirements)
# Result: "scheduled_agent.py.template"
```

### 2. Prompt Building
```python
prompt = executor._build_prompt(requirements)
# Creates detailed LLM prompt with:
# - Agent purpose
# - Input/output specs
# - Platform APIs
# - Constraints
# - Success criteria
```

### 3. Code Generation
```python
# LLM generates business logic
logic = llm.generate(prompt)
# Result:
# outputs = {"status": "complete"}
# logger.info("Done")
```

### 4. Code Assembly
```python
complete_code = executor._assemble_code(template, logic, requirements)
# Combines template + logic + placeholders
```

### 5. Validation
```python
is_valid, formatted, errors = executor.validate_and_format(complete_code)
# Checks syntax, security, formats with Black
```

### 6. Save & Store
```python
filepath = executor._save_generated_code(agent_id, formatted_code)
executor._update_agent_record(agent_id, filepath)
# Saves to disk and updates database
```

---

## 🔧 Troubleshooting

### Issue: "Template not found"
```bash
# Check templates exist
ls agents/templates/

# Should show:
# base_agent.py.template
# api_agent.py.template
# scheduled_agent.py.template
```

### Issue: "Black not installed"
```bash
# Black is optional but recommended
pip install black

# Code will work without it (unformatted)
```

### Issue: "Bandit not installed"
```bash
# Bandit is optional for security scanning
pip install bandit

# Code will work without it
```

### Issue: Tests timeout
```bash
# Some tests may skip (LLM timeout - expected)
# This is fine and expected behavior
```

---

## 💡 Key Concepts

### Agent Templates
Three template types based on trigger type:
- **Base**: Manual triggers (simplest)
- **API**: External API calls
- **Scheduled**: Cron job execution

### Validation Pipeline
Three-stage validation:
1. **Syntax**: Python AST parsing
2. **Security**: Pattern detection + Bandit
3. **Formatting**: Black code formatter

### Code Placeholders
Template placeholders replaced with:
- `{agent_id}` → Unique agent identifier
- `{agent_name}` → Human-readable name
- `{business_logic_placeholder}` → Generated logic
- `{timeout}` → Execution timeout
- `{auth_type}` → Authentication method

---

## 📞 Support

If tests fail:
1. Run `python cli/test_executor.py` for detailed output
2. Check `EXECUTOR_TESTING_GUIDE.md` for detailed explanations
3. Review individual test code in `tests/unit/test_phase5_executor.py`

---

## 🎉 Success Criteria

✅ **All tests pass**
✅ **Code generates without errors**
✅ **Templates load correctly**
✅ **Validation pipeline works**
✅ **Security scanning detects issues**
✅ **Files save to disk**
✅ **Database records update**

---

**Status**: ✅ Phase 5 Complete & Ready for Testing
**Last Updated**: 2026-03-02
**Estimated Test Time**: 5 minutes
