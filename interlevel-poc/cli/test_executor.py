#!/usr/bin/env python3
"""
Universal Executor Test Interface
Comprehensive testing tool for the executor service
Tests code generation, validation, and integration
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.executor import ExecutorService
from src.services.agent_req import AgentRequirementModel
from src.models.database import SessionLocal, User, Agent, Session as DBSession
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


class ExecutorTestInterface:
    """Test interface for executor service"""

    def __init__(self):
        self.executor = ExecutorService()
        self.req_model = AgentRequirementModel()
        self.db = SessionLocal()
        self.test_results = []

    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)

    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{'─' * 80}")
        print(f"  {title}")
        print(f"{'─' * 80}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")

    def print_code(self, code: str, title: str = "Code"):
        """Print code with formatting"""
        print(f"\n{title}:")
        print("```python")
        print(code[:500] + "..." if len(code) > 500 else code)
        print("```")

    # ========================================================================
    # TEST 1: Template Management
    # ========================================================================

    def test_templates(self):
        """Test template loading and selection"""
        self.print_section("TEST 1: Template Management")

        test_results = {}

        # Test 1.1: Load templates
        print("\n[1.1] Loading all templates...")
        templates = ["base_agent.py.template", "api_agent.py.template", "scheduled_agent.py.template"]

        for template_name in templates:
            try:
                template = self.executor._load_template(template_name)
                size_kb = len(template) / 1024
                self.print_success(f"Loaded {template_name} ({size_kb:.1f} KB)")
                test_results[template_name] = True
            except Exception as e:
                self.print_error(f"Failed to load {template_name}: {e}")
                test_results[template_name] = False

        # Test 1.2: Template selection logic
        print("\n[1.2] Testing template selection logic...")

        # Base agent
        base_req = {"triggers": {"type": "manual"}, "platforms": []}
        selected = self.executor._select_template(base_req)
        if selected == "base_agent.py.template":
            self.print_success(f"Correct template selected for manual agent: {selected}")
        else:
            self.print_error(f"Wrong template for manual agent: {selected}")

        # API agent
        api_req = {"triggers": {"type": "manual"}, "platforms": [{"name": "REST API"}]}
        selected = self.executor._select_template(api_req)
        if selected == "api_agent.py.template":
            self.print_success(f"Correct template selected for API agent: {selected}")
        else:
            self.print_error(f"Wrong template for API agent: {selected}")

        # Scheduled agent
        sched_req = {"triggers": {"type": "schedule"}, "platforms": []}
        selected = self.executor._select_template(sched_req)
        if selected == "scheduled_agent.py.template":
            self.print_success(f"Correct template selected for scheduled agent: {selected}")
        else:
            self.print_error(f"Wrong template for scheduled agent: {selected}")

        return test_results

    # ========================================================================
    # TEST 2: Prompt Building
    # ========================================================================

    def test_prompt_building(self):
        """Test LLM prompt generation"""
        self.print_section("TEST 2: Prompt Building")

        requirements = {
            "purpose": "Monitor API health",
            "inputs": [
                {"name": "api_url", "type": "string", "description": "URL to monitor"}
            ],
            "outputs": [
                {"name": "status", "type": "string", "description": "Health status"}
            ],
            "platforms": [{"name": "REST API", "base_url": "https://api.example.com"}],
            "constraints": {"timeout": 30},
            "permissions": {"allowed_actions": ["http_request"]},
            "success_criteria": ["Returns valid status"]
        }

        prompt = self.executor._build_prompt(requirements)

        print("\n[2.1] Generated prompt analysis:")
        print(f"Prompt length: {len(prompt)} characters")

        checks = [
            ("Contains purpose", requirements["purpose"] in prompt),
            ("Contains input description", "URL to monitor" in prompt),
            ("Contains output description", "Health status" in prompt),
            ("Contains constraints", "timeout" in prompt.lower()),
            ("Contains success criteria", "Returns valid status" in prompt),
        ]

        for check_name, result in checks:
            if result:
                self.print_success(check_name)
            else:
                self.print_error(check_name)

        self.print_code(prompt[:800], "Sample Prompt")

        return all(result for _, result in checks)

    # ========================================================================
    # TEST 3: Code Extraction
    # ========================================================================

    def test_code_extraction(self):
        """Test code block extraction from LLM responses"""
        self.print_section("TEST 3: Code Extraction")

        test_cases = [
            {
                "name": "Markdown Python code block",
                "response": """Here's the code:
```python
outputs = {"status": "healthy"}
logger.info("Check complete")
```
This should work.""",
                "expected": "outputs"
            },
            {
                "name": "Code block without language",
                "response": """```
result = "test"
outputs = {"result": result}
```""",
                "expected": "outputs"
            },
            {
                "name": "Raw code (no blocks)",
                "response": "outputs = {'fallback': True}",
                "expected": "outputs"
            }
        ]

        results = {}
        for test in test_cases:
            code = self.executor._extract_code_blocks(test["response"])
            success = test["expected"] in code
            results[test["name"]] = success

            if success:
                self.print_success(f"{test['name']}")
            else:
                self.print_error(f"{test['name']}")

        return results

    # ========================================================================
    # TEST 4: Syntax Validation
    # ========================================================================

    def test_syntax_validation(self):
        """Test Python syntax validation"""
        self.print_section("TEST 4: Syntax Validation")

        test_cases = [
            {
                "name": "Valid Python code",
                "code": """def process():
    outputs = {"status": "success"}
    return outputs
""",
                "should_pass": True
            },
            {
                "name": "Invalid syntax",
                "code": "def broken(\n    invalid",
                "should_pass": False
            },
            {
                "name": "Complex valid code",
                "code": """
inputs = {"data": [1, 2, 3]}
result = sum(inputs.get("data", []))
outputs = {"sum": result}
""",
                "should_pass": True
            }
        ]

        results = {}
        for test in test_cases:
            result = self.executor._validate_syntax(test["code"])
            success = result.is_valid == test["should_pass"]
            results[test["name"]] = success

            if success:
                self.print_success(f"{test['name']} - {'Valid' if result.is_valid else 'Invalid'}")
            else:
                self.print_error(f"{test['name']} - Expected {'valid' if test['should_pass'] else 'invalid'}")
                if result.errors:
                    print(f"   Errors: {result.errors}")

        return results

    # ========================================================================
    # TEST 5: Security Scanning
    # ========================================================================

    def test_security_scanning(self):
        """Test code security scanning"""
        self.print_section("TEST 5: Security Scanning")

        test_cases = [
            {
                "name": "Safe code",
                "code": """
result = inputs.get("data", "")
logger.info(f"Processing {result}")
outputs = {"processed": result}
""",
                "should_pass": True
            },
            {
                "name": "Dangerous eval()",
                "code": "eval(user_input)",
                "should_pass": False
            },
            {
                "name": "Dangerous exec()",
                "code": "exec(code_string)",
                "should_pass": False
            }
        ]

        results = {}
        for test in test_cases:
            result = self.executor._security_scan_patterns(test["code"])
            success = result.is_valid == test["should_pass"]
            results[test["name"]] = success

            if success:
                self.print_success(f"{test['name']} - {'Safe' if result.is_valid else 'Unsafe'}")
            else:
                self.print_error(f"{test['name']}")
                if result.errors:
                    print(f"   Errors: {result.errors}")

        return results

    # ========================================================================
    # TEST 6: Code Assembly
    # ========================================================================

    def test_code_assembly(self):
        """Test template + logic assembly"""
        self.print_section("TEST 6: Code Assembly")

        requirements = {
            "agent_id": "test-executor-agent",
            "metadata": {
                "name": "Test Executor Agent",
                "description": "Test agent for executor"
            },
            "inputs": [{"name": "param1", "type": "string"}],
            "outputs": [{"name": "result", "type": "string"}],
            "triggers": {"type": "manual"},
            "platforms": [],
            "constraints": {"timeout": 30},
            "permissions": {"allowed_actions": [], "disallowed_actions": []}
        }

        business_logic = """
param = inputs.get("param1", "default")
result = f"Processed: {param}"
outputs = {"result": result}
"""

        template = self.executor._load_template("base_agent.py.template")
        assembled = self.executor._assemble_code(template, business_logic, requirements)

        print("\n[6.1] Code assembly checks:")

        checks = [
            ("Template included", len(assembled) > len(business_logic)),
            ("Agent ID present", "test-executor-agent" in assembled),
            ("Agent name present", "Test Executor Agent" in assembled),
            ("Business logic included", "Processed:" in assembled),
            ("Is valid Python", self.executor._validate_syntax(assembled).is_valid),
        ]

        for check_name, result in checks:
            if result:
                self.print_success(check_name)
            else:
                self.print_error(check_name)

        self.print_code(assembled, "Generated Agent Code (first 500 chars)")

        return all(result for _, result in checks)

    # ========================================================================
    # TEST 7: Validation Pipeline
    # ========================================================================

    def test_validation_pipeline(self):
        """Test complete validation pipeline"""
        self.print_section("TEST 7: Complete Validation Pipeline")

        code = """
# Test agent
inputs = {}
result = 42
outputs = {"result": result}
logger.info(f"Output: {outputs}")
"""

        print("\n[7.1] Running complete validation pipeline...")
        start = time.time()
        is_valid, formatted, errors = self.executor.validate_and_format(code)
        elapsed = time.time() - start

        print(f"Pipeline completed in {elapsed:.2f}s")

        if is_valid:
            self.print_success("Code passed all validation stages")
        else:
            self.print_error(f"Code failed validation: {errors}")

        checks = [
            ("Is valid", is_valid),
            ("Has formatted code", formatted is not None and len(formatted) > 0),
            ("No errors", len(errors) == 0),
        ]

        for check_name, result in checks:
            if result:
                self.print_success(check_name)
            else:
                self.print_error(check_name)

        self.print_code(formatted, "Formatted Code")

        return is_valid

    # ========================================================================
    # TEST 8: Authorization Headers
    # ========================================================================

    def test_auth_headers(self):
        """Test authentication header generation"""
        self.print_section("TEST 8: Authentication Headers")

        test_cases = [
            {
                "name": "API Key auth",
                "auth_type": "api_key",
                "permissions": {"required_secrets": ["API_KEY"]},
                "check": "Authorization"
            },
            {
                "name": "Bearer token auth",
                "auth_type": "bearer",
                "permissions": {"required_secrets": ["BEARER_TOKEN"]},
                "check": "Bearer"
            },
            {
                "name": "OAuth auth",
                "auth_type": "oauth",
                "permissions": {"required_secrets": ["OAUTH_TOKEN"]},
                "check": "Bearer"
            },
            {
                "name": "No auth",
                "auth_type": "none",
                "permissions": {},
                "check": "No authentication"
            }
        ]

        results = {}
        for test in test_cases:
            auth_code = self.executor._build_auth_headers(test["auth_type"], test["permissions"])
            success = test["check"] in auth_code
            results[test["name"]] = success

            if success:
                self.print_success(f"{test['name']}")
            else:
                self.print_error(f"{test['name']}")

        return results

    # ========================================================================
    # TEST 9: File Operations
    # ========================================================================

    def test_file_operations(self):
        """Test code saving operations"""
        self.print_section("TEST 9: File Operations")

        test_agent_id = f"test-file-ops-{int(time.time())}"
        test_code = '#!/usr/bin/env python3\nprint("test")'

        print(f"\n[9.1] Saving generated code...")
        try:
            filepath = self.executor._save_generated_code(test_agent_id, test_code)
            self.print_success(f"Saved to: {filepath}")

            # Verify file exists
            if Path(filepath).exists():
                self.print_success("File exists on disk")

                # Verify content
                with open(filepath, 'r') as f:
                    saved_code = f.read()

                if saved_code == test_code:
                    self.print_success("File content matches")
                else:
                    self.print_error("File content mismatch")

                # Cleanup
                Path(filepath).unlink()
                self.print_success("Cleanup successful")

                return True
            else:
                self.print_error("File does not exist")
                return False

        except Exception as e:
            self.print_error(f"File operation failed: {e}")
            return False

    # ========================================================================
    # TEST 10: Complete Workflow Simulation
    # ========================================================================

    def test_complete_workflow(self):
        """Test complete executor workflow with sample requirements"""
        self.print_section("TEST 10: Complete Workflow Simulation")

        # Create sample requirements
        requirements = {
            "agent_id": "test-complete-workflow",
            "version": "1.0",
            "metadata": {
                "name": "Test Complete Workflow Agent",
                "description": "Agent for testing complete executor workflow",
                "created_at": datetime.utcnow().isoformat()
            },
            "purpose": "Test the complete executor workflow",
            "inputs": [
                {"name": "test_input", "type": "string", "required": True, "description": "Test input"}
            ],
            "outputs": [
                {"name": "test_output", "type": "string", "description": "Test output"}
            ],
            "triggers": {"type": "manual"},
            "platforms": [],
            "constraints": {
                "max_execution_time": 300,
                "token_budget": 5000,
                "timeout": 30
            },
            "success_criteria": ["Returns valid output"],
            "failure_handling": {"retry_policy": {"max_retries": 3}},
            "permissions": {"allowed_actions": [], "disallowed_actions": []}
        }

        print("\n[10.1] Workflow Steps:")

        # Step 1: Template selection
        print("\n  1. Template Selection...")
        template_name = self.executor._select_template(requirements)
        self.print_success(f"Selected template: {template_name}")

        # Step 2: Load template
        print("\n  2. Loading Template...")
        try:
            template = self.executor._load_template(template_name)
            self.print_success(f"Loaded template ({len(template)} chars)")
        except Exception as e:
            self.print_error(f"Failed to load template: {e}")
            return False

        # Step 3: Build prompt
        print("\n  3. Building LLM Prompt...")
        prompt = self.executor._build_prompt(requirements)
        self.print_success(f"Built prompt ({len(prompt)} chars)")

        # Step 4: Simulate business logic (no LLM call)
        print("\n  4. Generating Business Logic...")
        business_logic = """
test_input = inputs.get("test_input", "default")
test_output = f"Test result: {test_input}"
outputs = {"test_output": test_output}
logger.info(f"Processing complete: {outputs}")
"""
        self.print_success("Generated business logic")

        # Step 5: Assemble code
        print("\n  5. Assembling Complete Code...")
        complete_code = self.executor._assemble_code(template, business_logic, requirements)
        self.print_success(f"Assembled code ({len(complete_code)} chars)")

        # Step 6: Validate
        print("\n  6. Validating Code...")
        is_valid, formatted_code, errors = self.executor.validate_and_format(complete_code)

        if is_valid:
            self.print_success("Code validation passed")
        else:
            self.print_error(f"Code validation failed: {errors}")
            return False

        # Step 7: Summary
        print("\n[10.2] Workflow Summary:")
        print(f"  ✅ Requirements loaded")
        print(f"  ✅ Template selected: {template_name}")
        print(f"  ✅ Code generated: {len(formatted_code)} chars")
        print(f"  ✅ Code validated: All checks passed")

        return is_valid

    # ========================================================================
    # Main Test Suite
    # ========================================================================

    def run_all_tests(self):
        """Run complete test suite"""
        self.print_header("UNIVERSAL EXECUTOR TEST SUITE")
        print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        results = {
            "Templates": self.test_templates(),
            "Prompts": self.test_prompt_building(),
            "Code Extraction": self.test_code_extraction(),
            "Syntax Validation": self.test_syntax_validation(),
            "Security Scanning": self.test_security_scanning(),
            "Code Assembly": self.test_code_assembly(),
            "Validation Pipeline": self.test_validation_pipeline(),
            "Auth Headers": self.test_auth_headers(),
            "File Operations": self.test_file_operations(),
            "Complete Workflow": self.test_complete_workflow(),
        }

        # Print summary
        self.print_header("TEST SUMMARY")

        passed = sum(1 for r in results.values() if isinstance(r, bool) and r)
        total_tests = len(results)

        print(f"\nTests Completed: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {total_tests - passed}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")

        print("\nDetailed Results:")
        for test_name, result in results.items():
            if isinstance(result, bool):
                status = "✅ PASS" if result else "❌ FAIL"
            elif isinstance(result, dict):
                passed_checks = sum(1 for v in result.values() if v)
                status = f"✅ {passed_checks}/{len(result)} passed"
            else:
                status = "✅ PASS"

            print(f"  {status:20} - {test_name}")

        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        return passed == total_tests


def main():
    """Main entry point"""
    try:
        tester = ExecutorTestInterface()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
