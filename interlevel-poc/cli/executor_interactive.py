#!/usr/bin/env python3
"""
Interactive Universal Executor Testing Tool
Test the executor with different scenarios interactively
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.executor import ExecutorService
from src.services.agent_req import AgentRequirementModel
from src.models.database import SessionLocal, Agent, User
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


class InteractiveExecutorTool:
    """Interactive executor testing tool"""

    def __init__(self):
        self.executor = ExecutorService()
        self.req_model = AgentRequirementModel()
        self.db = SessionLocal()

    def clear_screen(self):
        """Clear terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_menu(self):
        """Print main menu"""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "UNIVERSAL EXECUTOR - Interactive Testing Tool" + " " * 13 + "║")
        print("╚" + "═" * 78 + "╝")
        print("\n🔧 Available Tests:\n")
        print("  1️⃣  Test Template Selection")
        print("  2️⃣  Test Template Loading")
        print("  3️⃣  Test Code Extraction")
        print("  4️⃣  Test Syntax Validation")
        print("  5️⃣  Test Security Scanning")
        print("  6️⃣  Test Prompt Building")
        print("  7️⃣  Test Code Assembly")
        print("  8️⃣  Test Complete Validation Pipeline")
        print("  9️⃣  Test Authentication Headers")
        print("  🔟 Simulate Complete Code Generation")
        print("  🔟 Test with Sample Requirements")
        print("  0️⃣  Exit")
        print("\n" + "─" * 80)

    def get_choice(self) -> str:
        """Get user choice"""
        choice = input("\n➤ Enter your choice (0-11): ").strip()
        return choice

    # ========================================================================
    # TEST 1: Template Selection
    # ========================================================================

    def test_template_selection(self):
        """Interactive template selection test"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 1: Template Selection")
        print("=" * 80)

        print("\nSelect agent type:\n")
        print("  1. Manual Agent (no scheduling, no APIs)")
        print("  2. API Agent (calls external APIs)")
        print("  3. Scheduled Agent (runs on schedule)")

        choice = input("\n➤ Enter choice (1-3): ").strip()

        templates = {
            "1": ("manual", {"triggers": {"type": "manual"}, "platforms": []}),
            "2": ("api", {"triggers": {"type": "manual"}, "platforms": [{"name": "API"}]}),
            "3": ("scheduled", {"triggers": {"type": "schedule"}, "platforms": []}),
        }

        if choice not in templates:
            print("❌ Invalid choice")
            return

        agent_type, requirements = templates[choice]

        selected = self.executor._select_template(requirements)

        print(f"\n✅ Selected template for {agent_type} agent:")
        print(f"   {selected}")
        print(f"\nTemplate path: {self.executor.templates_dir / selected}")

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 2: Template Loading
    # ========================================================================

    def test_template_loading(self):
        """Interactive template loading test"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 2: Template Loading")
        print("=" * 80)

        print("\nAvailable templates:\n")
        templates = ["base_agent.py.template", "api_agent.py.template", "scheduled_agent.py.template"]

        for i, template in enumerate(templates, 1):
            print(f"  {i}. {template}")

        choice = input("\n➤ Enter choice (1-3): ").strip()

        if choice not in ["1", "2", "3"]:
            print("❌ Invalid choice")
            return

        template_name = templates[int(choice) - 1]

        try:
            template = self.executor._load_template(template_name)
            size_kb = len(template) / 1024

            print(f"\n✅ Successfully loaded {template_name}")
            print(f"   Size: {size_kb:.1f} KB")
            print(f"   Lines: {len(template.splitlines())}")

            print(f"\n📋 First 500 characters:")
            print("─" * 80)
            print(template[:500])
            print("─" * 80)

        except Exception as e:
            print(f"❌ Failed to load template: {e}")

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 3: Code Extraction
    # ========================================================================

    def test_code_extraction(self):
        """Interactive code extraction test"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 3: Code Extraction from LLM Response")
        print("=" * 80)

        print("\nPaste LLM response (or choose sample):\n")
        print("  1. Sample: Markdown code block")
        print("  2. Sample: Plain code block")
        print("  3. Sample: Raw code")
        print("  4. Enter custom response")

        samples = {
            "1": '''Here's the code:
```python
outputs = {"status": "healthy"}
logger.info("Check complete")
```
This should work.''',
            "2": '''```
result = "test"
outputs = {"result": result}
```''',
            "3": "outputs = {'fallback': True}"
        }

        choice = input("\n➤ Enter choice (1-4): ").strip()

        if choice == "4":
            print("\nEnter response (press Ctrl+D on new line when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            response = "\n".join(lines)
        elif choice in samples:
            response = samples[choice]
        else:
            print("❌ Invalid choice")
            return

        extracted = self.executor._extract_code_blocks(response)

        print("\n" + "=" * 80)
        print("EXTRACTED CODE:")
        print("=" * 80)
        print(extracted)
        print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 4: Syntax Validation
    # ========================================================================

    def test_syntax_validation(self):
        """Interactive syntax validation"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 4: Syntax Validation")
        print("=" * 80)

        print("\nChoose code to validate:\n")
        print("  1. Valid simple code")
        print("  2. Valid complex code")
        print("  3. Invalid code (syntax error)")
        print("  4. Enter custom code")

        samples = {
            "1": """outputs = {"status": "success"}""",
            "2": """
def process(inputs):
    data = inputs.get("data", [])
    result = sum(data) if data else 0
    outputs = {"result": result}
    return outputs
""",
            "3": "def broken(\n    invalid syntax here"
        }

        choice = input("\n➤ Enter choice (1-4): ").strip()

        if choice == "4":
            print("\nEnter Python code (press Ctrl+D on new line when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            code = "\n".join(lines)
        elif choice in samples:
            code = samples[choice]
        else:
            print("❌ Invalid choice")
            return

        result = self.executor._validate_syntax(code)

        print("\n" + "=" * 80)
        if result.is_valid:
            print("✅ CODE IS VALID")
        else:
            print("❌ CODE IS INVALID")
            if result.errors:
                print("\nErrors:")
                for error in result.errors:
                    print(f"  - {error}")
        print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 5: Security Scanning
    # ========================================================================

    def test_security_scanning(self):
        """Interactive security scanning"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 5: Security Scanning")
        print("=" * 80)

        print("\nChoose code to scan:\n")
        print("  1. Safe code")
        print("  2. Dangerous: eval()")
        print("  3. Dangerous: exec()")
        print("  4. Enter custom code")

        samples = {
            "1": """
result = inputs.get("data", "")
logger.info(f"Processing {result}")
outputs = {"processed": result}
""",
            "2": "eval(user_input)",
            "3": "exec(code_string)"
        }

        choice = input("\n➤ Enter choice (1-4): ").strip()

        if choice == "4":
            print("\nEnter Python code (press Ctrl+D on new line when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            code = "\n".join(lines)
        elif choice in samples:
            code = samples[choice]
        else:
            print("❌ Invalid choice")
            return

        result = self.executor._security_scan_patterns(code)

        print("\n" + "=" * 80)
        if result.is_valid:
            print("✅ CODE IS SAFE")
        else:
            print("❌ CODE HAS SECURITY ISSUES")
            if result.errors:
                print("\nIssues:")
                for error in result.errors:
                    print(f"  - {error}")
        print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 6: Prompt Building
    # ========================================================================

    def test_prompt_building(self):
        """Interactive prompt building"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 6: Prompt Building")
        print("=" * 80)

        requirements = {
            "purpose": "Monitor API health status",
            "inputs": [
                {"name": "api_url", "type": "string", "description": "URL to monitor"}
            ],
            "outputs": [
                {"name": "status", "type": "string", "description": "Health status"}
            ],
            "platforms": [{"name": "REST API"}],
            "constraints": {"timeout": 30},
            "permissions": {"allowed_actions": ["http_request"]},
            "success_criteria": ["Returns valid status"]
        }

        print("\nGenerating prompt for API monitoring agent...")
        prompt = self.executor._build_prompt(requirements)

        print(f"\n✅ Prompt generated ({len(prompt)} characters)")

        print("\n" + "=" * 80)
        print("GENERATED PROMPT (first 1000 chars):")
        print("=" * 80)
        print(prompt[:1000])
        print("...[truncated]...")
        print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 7: Code Assembly
    # ========================================================================

    def test_code_assembly(self):
        """Interactive code assembly"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 7: Code Assembly")
        print("=" * 80)

        requirements = {
            "agent_id": "test-assembly-agent",
            "metadata": {"name": "Test Assembly Agent", "description": "Test agent"},
            "inputs": [{"name": "data", "type": "string"}],
            "outputs": [{"name": "result", "type": "string"}],
            "triggers": {"type": "manual"},
            "platforms": [],
            "constraints": {"timeout": 30},
            "permissions": {"allowed_actions": []}
        }

        business_logic = """
data = inputs.get("data", "default")
result = f"Processed: {data}"
outputs = {"result": result}
logger.info(f"Done: {result}")
"""

        print("\nAssembling code from template + business logic...")

        template = self.executor._load_template("base_agent.py.template")
        assembled = self.executor._assemble_code(template, business_logic, requirements)

        print(f"\n✅ Code assembled ({len(assembled)} characters)")

        # Validate
        validation_result = self.executor._validate_syntax(assembled)
        if validation_result.is_valid:
            print("✅ Assembled code is valid Python")
        else:
            print("❌ Assembled code has syntax errors")

        print("\n" + "=" * 80)
        print("ASSEMBLED CODE (first 1000 chars):")
        print("=" * 80)
        print(assembled[:1000])
        print("...[truncated]...")
        print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 8: Complete Validation Pipeline
    # ========================================================================

    def test_validation_pipeline(self):
        """Interactive validation pipeline"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 8: Complete Validation Pipeline")
        print("=" * 80)

        code = """
# Test agent code
inputs = {}
result = 42
outputs = {"result": result}
logger.info(f"Output: {outputs}")
"""

        print("\nRunning validation pipeline...")
        print("  1. Syntax validation")
        print("  2. Security scanning")
        print("  3. Code formatting")

        start = time.time()
        is_valid, formatted, errors = self.executor.validate_and_format(code)
        elapsed = time.time() - start

        print(f"\n✅ Pipeline completed in {elapsed:.2f}s")

        if is_valid:
            print("✅ All validation stages passed")
        else:
            print("❌ Validation failed")
            if errors:
                print("Errors:")
                for error in errors:
                    print(f"  - {error}")

        print("\n" + "=" * 80)
        print("VALIDATED & FORMATTED CODE:")
        print("=" * 80)
        print(formatted[:1000])
        if len(formatted) > 1000:
            print("...[truncated]...")
        print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 9: Authentication Headers
    # ========================================================================

    def test_auth_headers(self):
        """Interactive auth headers"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 9: Authentication Headers")
        print("=" * 80)

        print("\nSelect authentication type:\n")
        print("  1. API Key")
        print("  2. Bearer Token")
        print("  3. OAuth")
        print("  4. None")

        choice = input("\n➤ Enter choice (1-4): ").strip()

        auth_map = {
            "1": ("api_key", {"required_secrets": ["API_KEY"]}),
            "2": ("bearer", {"required_secrets": ["BEARER_TOKEN"]}),
            "3": ("oauth", {"required_secrets": ["OAUTH_TOKEN"]}),
            "4": ("none", {})
        }

        if choice not in auth_map:
            print("❌ Invalid choice")
            return

        auth_type, permissions = auth_map[choice]
        auth_code = self.executor._build_auth_headers(auth_type, permissions)

        print("\n" + "=" * 80)
        print(f"AUTHENTICATION CODE ({auth_type.upper()}):")
        print("=" * 80)
        print(auth_code)
        print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 10: Complete Simulation
    # ========================================================================

    def test_complete_simulation(self):
        """Interactive complete code generation simulation"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 10: Complete Code Generation Simulation")
        print("=" * 80)

        requirements = {
            "agent_id": "test-complete-simulation",
            "version": "1.0",
            "metadata": {
                "name": "Test Complete Simulation Agent",
                "description": "Simulated agent for testing"
            },
            "purpose": "Test complete workflow",
            "inputs": [{"name": "input", "type": "string"}],
            "outputs": [{"name": "output", "type": "string"}],
            "triggers": {"type": "manual"},
            "platforms": [],
            "constraints": {"timeout": 30},
            "success_criteria": ["Returns valid output"],
            "failure_handling": {},
            "permissions": {"allowed_actions": []}
        }

        print("\n🔄 Simulating complete code generation workflow...\n")

        # Step 1
        print("  [1/6] Selecting template...")
        template_name = self.executor._select_template(requirements)
        print(f"       ✅ {template_name}")

        # Step 2
        print("  [2/6] Loading template...")
        template = self.executor._load_template(template_name)
        print(f"       ✅ {len(template)} chars loaded")

        # Step 3
        print("  [3/6] Building LLM prompt...")
        prompt = self.executor._build_prompt(requirements)
        print(f"       ✅ {len(prompt)} chars")

        # Step 4
        print("  [4/6] Generating business logic...")
        business_logic = """
input_val = inputs.get("input", "default")
output_val = f"Processed: {input_val}"
outputs = {"output": output_val}
"""
        print(f"       ✅ {len(business_logic)} chars")

        # Step 5
        print("  [5/6] Assembling code...")
        complete_code = self.executor._assemble_code(template, business_logic, requirements)
        print(f"       ✅ {len(complete_code)} chars")

        # Step 6
        print("  [6/6] Validating...")
        is_valid, formatted, errors = self.executor.validate_and_format(complete_code)
        if is_valid:
            print(f"       ✅ All validation passed")
        else:
            print(f"       ❌ Validation failed: {errors}")

        print("\n" + "=" * 80)
        print("FINAL GENERATED CODE (first 1500 chars):")
        print("=" * 80)
        print(formatted[:1500])
        if len(formatted) > 1500:
            print("...[truncated]...")
        print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # TEST 11: Sample Requirements
    # ========================================================================

    def test_with_sample_requirements(self):
        """Test with pre-defined sample requirements"""
        self.clear_screen()
        print("=" * 80)
        print("TEST 11: Test with Sample Requirements")
        print("=" * 80)

        samples = {
            "1": {
                "name": "Weather Monitor Agent",
                "req": {
                    "agent_id": "weather-monitor",
                    "metadata": {"name": "Weather Monitor", "description": "Monitors weather"},
                    "purpose": "Monitor weather for locations",
                    "inputs": [{"name": "city", "type": "string"}],
                    "outputs": [{"name": "weather", "type": "string"}],
                    "triggers": {"type": "schedule", "config": {"schedule": "0 0 * * *"}},
                    "platforms": [{"name": "Weather API"}],
                    "constraints": {"timeout": 30},
                    "permissions": {"allowed_actions": ["http_request"]}
                }
            },
            "2": {
                "name": "Data Transformer Agent",
                "req": {
                    "agent_id": "data-transformer",
                    "metadata": {"name": "Data Transformer", "description": "Transforms data"},
                    "purpose": "Transform input data to output format",
                    "inputs": [{"name": "json_data", "type": "string"}],
                    "outputs": [{"name": "transformed_data", "type": "string"}],
                    "triggers": {"type": "manual"},
                    "platforms": [],
                    "constraints": {"timeout": 60},
                    "permissions": {"allowed_actions": []}
                }
            },
            "3": {
                "name": "Email Notification Agent",
                "req": {
                    "agent_id": "email-notifier",
                    "metadata": {"name": "Email Notifier", "description": "Sends emails"},
                    "purpose": "Send email notifications",
                    "inputs": [{"name": "recipient", "type": "string"}, {"name": "message", "type": "string"}],
                    "outputs": [{"name": "status", "type": "string"}],
                    "triggers": {"type": "event"},
                    "platforms": [{"name": "Email Service"}],
                    "constraints": {"timeout": 30},
                    "permissions": {"allowed_actions": ["send_email"]}
                }
            }
        }

        print("\nAvailable samples:\n")
        for key, value in samples.items():
            print(f"  {key}. {value['name']}")

        choice = input("\n➤ Select sample (1-3): ").strip()

        if choice not in samples:
            print("❌ Invalid choice")
            return

        sample = samples[choice]
        requirements = sample["req"]

        print(f"\n🔄 Testing with: {sample['name']}\n")

        # Step through workflow
        print("  [1] Template selection...")
        template_name = self.executor._select_template(requirements)
        print(f"      ✅ {template_name}")

        print("  [2] Template loading...")
        template = self.executor._load_template(template_name)
        print(f"      ✅ Loaded")

        print("  [3] Code assembly...")
        business_logic = "# Business logic here\noutputs = {'status': 'success'}"
        assembled = self.executor._assemble_code(template, business_logic, requirements)
        print(f"      ✅ {len(assembled)} chars")

        print("  [4] Validation...")
        is_valid, formatted, errors = self.executor.validate_and_format(assembled)
        status = "✅ PASSED" if is_valid else f"❌ FAILED - {errors}"
        print(f"      {status}")

        if is_valid:
            print("\n" + "=" * 80)
            print("GENERATED CODE PREVIEW:")
            print("=" * 80)
            print(formatted[:2000])
            if len(formatted) > 2000:
                print("...[truncated]...")
            print("=" * 80)

        input("\nPress Enter to continue...")

    # ========================================================================
    # Main Loop
    # ========================================================================

    def run(self):
        """Run interactive tool"""
        while True:
            self.print_menu()
            choice = self.get_choice()

            if choice == "0":
                print("\n✅ Goodbye!\n")
                break
            elif choice == "1":
                self.test_template_selection()
            elif choice == "2":
                self.test_template_loading()
            elif choice == "3":
                self.test_code_extraction()
            elif choice == "4":
                self.test_syntax_validation()
            elif choice == "5":
                self.test_security_scanning()
            elif choice == "6":
                self.test_prompt_building()
            elif choice == "7":
                self.test_code_assembly()
            elif choice == "8":
                self.test_validation_pipeline()
            elif choice == "9":
                self.test_auth_headers()
            elif choice == "10":
                self.test_complete_simulation()
            elif choice == "11":
                self.test_with_sample_requirements()
            else:
                print("❌ Invalid choice. Try again.")
                input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    try:
        tool = InteractiveExecutorTool()
        tool.run()
    except KeyboardInterrupt:
        print("\n\n✅ Interrupted. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
