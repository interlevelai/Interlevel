# Universal Executor (Phase 5) - Testing & Verification Guide

**Last Updated**: 2026-03-02
**Status**: ✅ Phase 5 Complete & Ready for Testing

---

## 📋 Overview

This guide provides comprehensive instructions for testing the **Universal Executor Service** which converts requirements JSON into executable Python agent code.

### What the Executor Does

```
Requirements JSON (from Phase 4)
    ↓
[Universal Executor]
    ├→ Template Selection
    ├→ LLM Code Generation
    ├→ Code Assembly
    ├→ Validation (syntax + security + formatting)
    └→ File Save & Database Update
    ↓
Generated Python Agent Code
```

---

## 🚀 Quick Start (3 minutes)

### Option 1: Automated Test Suite

Run all executor tests at once:

```bash
cd interlevel-poc
python cli/test_executor.py
```

**Expected Output**: 10 test categories, 100% pass rate

### Option 2: Interactive Testing Tool

Test the executor step-by-step interactively:

```bash
cd interlevel-poc
python cli/executor_interactive.py
```

**Features**:
- 11 interactive tests
- Choose what to test
- See real code generation results
- Test with sample agents

### Option 3: Run Unit Tests

Run pytest tests for Phase 5:

```bash
cd interlevel-poc
pytest tests/unit/test_phase5_executor.py -v
```

**Expected**: 30+ tests passing

---

## 📝 Detailed Testing Guide

### Test 1: Template Management

**What it tests**: Template selection and loading

```bash
# Via test interface
python cli/test_executor.py
# → Test 1: Template Management

# Via pytest
pytest tests/unit/test_phase5_executor.py::TestTemplateSelection -v
pytest tests/unit/test_phase5_executor.py::TestTemplateLoading -v
```

**What happens**:
1. ✅ Loads 3 templates (base, API, scheduled)
2. ✅ Selects correct template based on requirements
3. ✅ Verifies template content

**Expected Results**:
```
✅ Loaded base_agent.py.template (2.5 KB)
✅ Loaded api_agent.py.template (3.2 KB)
✅ Loaded scheduled_agent.py.template (3.1 KB)
✅ Correct template selected for manual agent: base_agent.py.template
✅ Correct template selected for API agent: api_agent.py.template
✅ Correct template selected for scheduled agent: scheduled_agent.py.template
```

---

### Test 2: Prompt Building

**What it tests**: LLM prompt generation from requirements

```bash
python cli/test_executor.py
# → Test 2: Prompt Building
```

**What happens**:
1. ✅ Takes requirements dict
2. ✅ Formats inputs, outputs, platforms, constraints
3. ✅ Builds detailed LLM prompt
4. ✅ Validates prompt structure

**Expected Results**:
```
✅ Contains purpose
✅ Contains input description
✅ Contains output description
✅ Contains constraints
✅ Contains success criteria
Prompt length: 1200+ characters
```

---

### Test 3: Code Extraction

**What it tests**: Extract Python code from LLM responses

```bash
python cli/test_executor.py
# → Test 3: Code Extraction
```

**Handles**:
- ✅ Markdown code blocks: ` ```python ... ``` `
- ✅ Plain code blocks: ` ``` ... ``` `
- ✅ Raw code (no markers)

**Example**:
```python
# Input: LLM response with markdown
"""
Here's the code:
```python
outputs = {"status": "healthy"}
```
"""

# Output: Extracted code
outputs = {"status": "healthy"}
```

---

### Test 4: Syntax Validation

**What it tests**: Python syntax correctness

```bash
python cli/test_executor.py
# → Test 4: Syntax Validation
```

**Tests**:
- ✅ Valid code passes
- ✅ Invalid code fails with error
- ✅ Complex valid code passes

**Example**:
```python
# Valid code
def process():
    outputs = {"status": "success"}
    return outputs
# ✅ PASS

# Invalid code
def broken(\n    invalid
# ❌ FAIL - SyntaxError
```

---

### Test 5: Security Scanning

**What it tests**: Detects dangerous code patterns

```bash
python cli/test_executor.py
# → Test 5: Security Scanning
```

**Detects**:
- ✅ `eval()` - Code execution
- ✅ `exec()` - Code execution
- ✅ `__import__()` - Dynamic imports
- ✅ `os.system()` - System commands
- ✅ SQL injection patterns

**Example**:
```python
# Safe code
result = inputs.get("data", "")
outputs = {"processed": result}
# ✅ PASS

# Dangerous code
eval(user_input)
# ❌ FAIL - eval() not allowed
```

---

### Test 6: Code Assembly

**What it tests**: Template + business logic assembly

```bash
python cli/test_executor.py
# → Test 6: Code Assembly
```

**Process**:
1. Load template
2. Extract placeholders
3. Generate business logic
4. Replace placeholders
5. Validate result

**Example**:
```python
# Template placeholder
{business_logic_placeholder}

# Generated logic
param = inputs.get("param1", "default")
result = f"Processed: {param}"
outputs = {"result": result}

# Result: Complete agent code with logic inserted
```

---

### Test 7: Validation Pipeline

**What it tests**: Complete validation (syntax + security + formatting)

```bash
python cli/test_executor.py
# → Test 7: Complete Validation Pipeline
```

**Stages**:
1. **Syntax Validation**: `ast.parse()` ✅
2. **Security Scanning**: Pattern detection + Bandit ✅
3. **Code Formatting**: Black auto-formatter ✅

**Example**:
```python
# Input: Unformatted code
x=1
y=2
outputs={'test':'value'}

# Output: Formatted code
x = 1
y = 2
outputs = {"test": "value"}
```

---

### Test 8: Authentication Headers

**What it tests**: Generate auth code for different auth types

```bash
python cli/test_executor.py
# → Test 8: Authentication Headers
```

**Supported Auth Types**:
1. **API Key**: Bearer token from environment
2. **Bearer**: Bearer token authentication
3. **OAuth**: OAuth token handling
4. **None**: No authentication

**Example**:
```python
# API Key auth
api_key = os.environ.get("API_KEY")
if api_key:
    headers["Authorization"] = f"Bearer {api_key}"

# Bearer auth
token = os.environ.get("BEARER_TOKEN")
if token:
    headers["Authorization"] = f"Bearer {token}"
```

---

### Test 9: File Operations

**What it tests**: Save generated code to disk

```bash
python cli/test_executor.py
# → Test 9: File Operations
```

**Tests**:
- ✅ Creates directory if needed
- ✅ Saves file with correct content
- ✅ File is readable and valid
- ✅ Cleanup works

**Output**:
```
✅ Saved to: agents/generated/test-agent.py
✅ File exists on disk
✅ File content matches
✅ Cleanup successful
```

---

### Test 10: Complete Workflow Simulation

**What it tests**: Full end-to-end simulation

```bash
python cli/test_executor.py
# → Test 10: Complete Workflow Simulation
```

**Workflow**:
1. Load requirements
2. Select template
3. Load template
4. Build prompt
5. Generate business logic
6. Assemble code
7. Validate & format
8. Save to disk
9. Update database

**Expected Output**:
```
[1/9] Loading requirements... ✅
[2/9] Selecting template... ✅
[3/9] Loading template... ✅
[4/9] Building prompt... ✅
[5/9] Generating logic... ✅
[6/9] Assembling code... ✅
[7/9] Validating... ✅
[8/9] Formatting... ✅
[9/9] Complete workflow... ✅
```

---

## 🧪 Running Individual Tests

### Test Specific Component

```bash
# Test template loading only
pytest tests/unit/test_phase5_executor.py::TestTemplateLoading -v

# Test validation pipeline only
pytest tests/unit/test_phase5_executor.py::TestValidationPipeline -v

# Test security scanning only
pytest tests/unit/test_phase5_executor.py::test_security_scan_patterns_safe_code -v
```

### Test with Verbose Output

```bash
pytest tests/unit/test_phase5_executor.py -v -s
```

### Test with Full Traceback

```bash
pytest tests/unit/test_phase5_executor.py --tb=long
```

---

## 📊 Test Coverage by Component

| Component | Tests | Status |
|-----------|-------|--------|
| Executor Service Init | 1 | ✅ |
| Template Selection | 3 | ✅ |
| Template Loading | 4 | ✅ |
| Code Generation | 8 | ✅ |
| Validation Pipeline | 6 | ✅ |
| Code Assembly | 2 | ✅ |
| File Operations | 3 | ✅ |
| Error Handling | 3 | ✅ |
| Template Variations | 3 | ✅ |
| **TOTAL** | **33** | **✅** |

---

## ✅ Success Criteria

All tests should show:

```
✅ ExecutorService initializes correctly
✅ Templates load successfully (3 templates)
✅ Template selection logic works (base, API, scheduled)
✅ Code generation prompts build correctly
✅ Code extraction handles multiple formats
✅ Syntax validation works (valid & invalid)
✅ Security scanning detects dangerous patterns
✅ Code assembly replaces all placeholders
✅ Complete validation pipeline passes
✅ Authentication headers generate correctly
✅ File operations save and load correctly
✅ End-to-end workflow completes successfully
```

---

## 🔍 Debugging Failed Tests

### If Template Loading Fails

```bash
# Check templates directory
ls interlevel-poc/agents/templates/

# Verify template files exist
ls -la agents/templates/*.template
```

### If Validation Fails

```bash
# Check if dependencies installed
pip install black bandit

# Test syntax directly
python -c "import ast; ast.parse('your code here')"
```

### If Security Scan Fails

```bash
# Check bandit installation
bandit --version

# Run manually
bandit -r agents/generated/
```

---

## 📚 Using the Interactive Tool

```bash
python cli/executor_interactive.py
```

**Menu Options**:
1. Test Template Selection - Choose agent type
2. Test Template Loading - Load specific template
3. Test Code Extraction - Parse LLM responses
4. Test Syntax Validation - Validate Python code
5. Test Security Scanning - Check for dangers
6. Test Prompt Building - See LLM prompts
7. Test Code Assembly - See assembled code
8. Test Validation Pipeline - Full validation
9. Test Auth Headers - See auth code
10. Complete Simulation - End-to-end test
11. Sample Requirements - Pre-built scenarios

---

## 🎯 Sample Agents to Test

The interactive tool includes 3 sample agents:

### 1. Weather Monitor Agent
```json
{
  "name": "Weather Monitor",
  "triggers": "schedule (daily)",
  "platforms": "Weather API",
  "input": "city (string)",
  "output": "weather (string)"
}
```

### 2. Data Transformer Agent
```json
{
  "name": "Data Transformer",
  "triggers": "manual",
  "platforms": "None",
  "input": "json_data (string)",
  "output": "transformed_data (string)"
}
```

### 3. Email Notification Agent
```json
{
  "name": "Email Notifier",
  "triggers": "event",
  "platforms": "Email Service",
  "input": "recipient, message (string)",
  "output": "status (string)"
}
```

---

## 🚨 Known Issues & Workarounds

### Bandit Not Installed
```bash
# Install bandit
pip install bandit

# Or skip bandit tests
# The executor will continue without it
```

### Black Not Installed
```bash
# Install black
pip install black

# Code will work unformatted if black unavailable
```

### LLM Timeout (Expected)
```
One test is marked SKIP because it requires LLM
This is expected behavior
```

---

## 📈 Performance Expectations

| Test | Time |
|------|------|
| Template tests | < 1s |
| Code generation | < 2s |
| Validation pipeline | < 1s |
| Security scanning | < 2s |
| File operations | < 1s |
| **Total suite** | **~30 seconds** |

---

## 🔗 Related Documentation

- [Phase 4: Requirements Model](./TASK_401_GUIDE.md)
- [Phase 5: Universal Executor](./EXECUTOR_TESTING_GUIDE.md)
- [Complete Test Report](./TEST_REPORT_TASK_402_403.md)
- [Completion Summary](./COMPLETION_SUMMARY.md)

---

## ✨ Next Steps After Testing

Once Phase 5 testing is complete and passing:

1. **Phase 6: Injector Service** - Deploy and execute agents
   - `src/services/injector.py`
   - `cli/run_agent.py`
   - `src/services/token_manager.py`

2. **Phase 7: Integration** - End-to-end workflow
   - `cli/interlevel.py` (unified CLI)
   - Complete E2E tests
   - Demo scenarios

---

## 📞 Testing Checklist

- [ ] Run automated test suite (`python cli/test_executor.py`)
- [ ] Test interactively (`python cli/executor_interactive.py`)
- [ ] Run unit tests (`pytest tests/unit/test_phase5_executor.py -v`)
- [ ] Verify all templates load
- [ ] Test code generation with samples
- [ ] Check validation pipeline
- [ ] Verify file operations
- [ ] Test with different agent types
- [ ] Verify database updates
- [ ] Check error handling

---

**Status**: ✅ Phase 5 Complete & Ready for Testing
**Last Verified**: 2026-03-02
**Test Pass Rate**: 96%+ expected
