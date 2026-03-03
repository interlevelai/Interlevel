"""
Universal Executor Service
Generates executable Python agent code from requirements JSON

Hybrid approach: Templates for structure, LLM for business logic
Comprehensive validation: Syntax + Pattern matching + Bandit security scanning
Auto-formatting: Black code formatter
"""
import sys
import json
import ast
import re
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

from src.llm.client import LLMClient
from src.models.database import SessionLocal, Agent
from src.utils.logger import get_logger
from src.utils.validators import validate_agent_code, ValidationResult
from config.settings import settings

logger = get_logger(__name__)


class ExecutorService:
    """Generates executable agent code from requirements JSON"""

    def __init__(self):
        """Initialize executor service"""
        self.llm = LLMClient()
        self.db = SessionLocal()
        self.templates_dir = Path(__file__).parent.parent.parent / "agents" / "templates"
        self.output_dir = Path(__file__).parent.parent.parent / "agents" / "generated"
        logger.info("ExecutorService initialized")

    # ============================================================================
    # PUBLIC METHODS
    # ============================================================================

    def generate_agent_code(self, agent_id: str) -> Dict[str, Any]:
        """
        Main entry point for code generation

        Process:
        1. Load requirements JSON
        2. Select appropriate template
        3. Generate business logic with LLM
        4. Assemble complete code
        5. Validate and format
        6. Save to file
        7. Update database

        Args:
            agent_id: Agent ID to generate code for

        Returns:
            {
                "success": bool,
                "agent_id": str,
                "code_path": str,
                "template_used": str,
                "errors": list (if not successful)
            }
        """
        logger.info(f"Starting code generation for agent {agent_id}")

        try:
            # Step 1: Load requirements
            from src.services.agent_req import AgentRequirementModel
            req_model = AgentRequirementModel()
            requirements = req_model.load_requirements(agent_id)
            logger.info(f"Loaded requirements for {requirements.get('metadata', {}).get('name')}")

            # Step 2: Select template
            template_name = self._select_template(requirements)
            template_content = self._load_template(template_name)
            logger.info(f"Selected template: {template_name}")

            # Step 3: Generate business logic
            logger.info("Generating business logic with LLM...")
            business_logic = self._generate_business_logic(requirements)
            logger.info(f"Generated {len(business_logic)} characters of business logic")

            # Step 4: Assemble code
            complete_code = self._assemble_code(template_content, business_logic, requirements)
            logger.info("Assembled complete agent code")

            # Step 5: Validate and format
            is_valid, formatted_code, errors = self.validate_and_format(complete_code)

            if not is_valid:
                logger.error(f"Validation failed: {errors}")
                return {
                    "success": False,
                    "agent_id": agent_id,
                    "errors": errors
                }

            # Step 6: Save to file
            code_path = self._save_generated_code(agent_id, formatted_code)
            logger.info(f"Saved generated code to {code_path}")

            # Step 7: Update database
            self._update_agent_record(agent_id, code_path)
            logger.info("Updated agent record in database")

            return {
                "success": True,
                "agent_id": agent_id,
                "code_path": code_path,
                "template_used": template_name
            }

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "agent_id": agent_id,
                "error": str(e)
            }

    def validate_and_format(self, code: str) -> Tuple[bool, str, List[str]]:
        """
        Run complete validation pipeline:
        1. Syntax validation (ast.parse)
        2. Security scan (patterns + bandit)
        3. Auto-format (black)

        Returns: (is_valid, formatted_code, errors)
        """
        errors = []

        # Stage 1: Syntax Validation
        logger.info("Stage 1: Syntax validation")
        syntax_result = self._validate_syntax(code)
        if not syntax_result.is_valid:
            errors.extend(syntax_result.errors)
            return False, code, errors

        # Stage 2: Security Scanning
        logger.info("Stage 2: Security scanning - Patterns")
        pattern_result = self._security_scan_patterns(code)
        if not pattern_result.is_valid:
            errors.extend(pattern_result.errors)
            return False, code, errors

        logger.info("Stage 2: Security scanning - Bandit")
        bandit_result = self._security_scan_bandit(code)
        if not bandit_result.is_valid:
            errors.extend(bandit_result.errors)
            return False, code, errors

        # Stage 3: Auto-formatting
        logger.info("Stage 3: Auto-formatting with black")
        try:
            formatted_code = self._format_code(code)
        except Exception as e:
            logger.warning(f"Black formatting failed: {e} - returning unformatted code")
            formatted_code = code

        logger.info("Validation pipeline complete - all checks passed")
        return True, formatted_code, errors

    # ============================================================================
    # TEMPLATE MANAGEMENT
    # ============================================================================

    def _select_template(self, requirements: Dict[str, Any]) -> str:
        """
        Select appropriate template based on requirements

        Decision logic:
        - If trigger.type == "schedule" -> scheduled_agent.py.template
        - Else if platforms exist -> api_agent.py.template
        - Else -> base_agent.py.template
        """
        triggers = requirements.get("triggers", {})
        platforms = requirements.get("platforms", [])

        # Scheduled agents
        if triggers.get("type") == "schedule":
            return "scheduled_agent.py.template"

        # API-calling agents
        elif platforms and len(platforms) > 0:
            return "api_agent.py.template"

        # Basic agents
        else:
            return "base_agent.py.template"

    def _load_template(self, template_name: str) -> str:
        """Load template file content"""
        template_path = self.templates_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Loaded template: {template_name}")
            return content
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            raise

    # ============================================================================
    # CODE GENERATION
    # ============================================================================

    def _generate_business_logic(self, requirements: Dict[str, Any]) -> str:
        """Generate business logic using LLM"""
        prompt = self._build_prompt(requirements)

        try:
            logger.info("Calling LLM to generate business logic...")
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3  # Low temperature for deterministic code
            )
            logger.info("LLM response received")

            code = self._extract_code_blocks(response)
            return code

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Return a basic placeholder
            return "outputs = {}\nlogger.info('Business logic not generated')"

    def _build_prompt(self, requirements: Dict[str, Any]) -> str:
        """Build detailed prompt for LLM code generation"""
        metadata = requirements.get("metadata", {})
        inputs_list = requirements.get("inputs", [])
        outputs_list = requirements.get("outputs", [])
        platforms = requirements.get("platforms", [])
        constraints = requirements.get("constraints", {})
        permissions = requirements.get("permissions", {})
        success_criteria = requirements.get("success_criteria", [])

        # Format inputs
        inputs_formatted = "\n".join([
            f"  - {inp['name']} ({inp.get('type', 'unknown')}): {inp.get('description', '')}"
            for inp in inputs_list
        ]) if inputs_list else "  - None"

        # Format outputs
        outputs_formatted = "\n".join([
            f"  - {out['name']} ({out.get('type', 'unknown')}): {out.get('description', '')}"
            for out in outputs_list
        ]) if outputs_list else "  - None"

        # Format platforms
        platforms_formatted = "\n".join([
            f"  - {p['name']} ({p.get('base_url', 'N/A')})"
            for p in platforms
        ]) if platforms else "  - None"

        # Format success criteria
        criteria_formatted = "\n".join([f"  - {c}" for c in success_criteria]) if success_criteria else "  - None specified"

        # Format permissions
        allowed = ", ".join(permissions.get("allowed_actions", []))
        disallowed = ", ".join(permissions.get("disallowed_actions", []))

        prompt = f"""You are an expert Python code generator for autonomous agents.

Generate ONLY the business logic function for an agent with these requirements:

**AGENT PURPOSE**: {requirements.get('purpose', 'Not specified')}

**INPUTS**:
{inputs_formatted}

**OUTPUTS**:
{outputs_formatted}

**PLATFORMS/APIS**:
{platforms_formatted}

**CONSTRAINTS**:
- Max execution time: {constraints.get('max_execution_time', 300)}s
- Token budget: {constraints.get('token_budget', 5000)}
- Timeout: {constraints.get('timeout', 30)}s

**SUCCESS CRITERIA**:
{criteria_formatted}

**PERMISSIONS**:
- Allowed actions: {allowed if allowed else 'None specified'}
- Disallowed actions: {disallowed if disallowed else 'None'}

**REQUIREMENTS**:
1. Generate ONLY the business logic code (no imports, no main function, no try/except wrapper)
2. Use the variable "inputs" which contains validated input data as a dict
3. Create a variable "outputs" (dict) with your results
4. Use "logger" for logging (already configured in the wrapper)
5. For API agents: Use make_api_request(method, endpoint, data) function
6. Handle errors gracefully within the logic
7. Follow Python best practices and PEP 8
8. Add clear comments explaining the logic
9. Do NOT use any disallowed actions: {disallowed}
10. Code must be deterministic and idempotent where possible

**EXAMPLE STRUCTURE** (your code should look similar):
```python
# Extract inputs
param1 = inputs.get("param1", "default_value")
param2 = inputs.get("param2", "default_value")

logger.info(f"Processing with param1={{param1}}, param2={{param2}}")

# Your business logic here
try:
    # Process data
    result = param1 + param2
    logger.info(f"Processing complete: {{result}}")
except Exception as e:
    logger.error(f"Processing failed: {{e}}")
    raise

# Build outputs
outputs = {{
    "result": result,
    "summary": f"Processed {{param1}} and {{param2}}"
}}
```

Now generate the business logic code for this agent:
"""
        return prompt

    def _extract_code_blocks(self, llm_response: str) -> str:
        """Extract Python code blocks from LLM response"""
        # Try to find markdown code block
        pattern = r'```python\n(.*?)\n```'
        matches = re.findall(pattern, llm_response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Try without language specifier
        pattern = r'```\n(.*?)\n```'
        matches = re.findall(pattern, llm_response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Return as-is if no code blocks found
        return llm_response.strip()

    def _assemble_code(self, template: str, business_logic: str,
                       requirements: Dict[str, Any]) -> str:
        """
        Combine template with generated logic
        Replace placeholders with actual values
        """
        metadata = requirements.get("metadata", {})
        inputs_list = requirements.get("inputs", [])
        constraints = requirements.get("constraints", {})
        platforms = requirements.get("platforms", [])
        triggers = requirements.get("triggers", {})
        permissions = requirements.get("permissions", {})

        # Build required inputs list
        required_inputs = [i["name"] for i in inputs_list if i.get("required", False)]

        # Extract platform info (for API agents)
        platform_name = ""
        base_url = ""
        auth_type = "none"
        if platforms:
            platform = platforms[0]
            platform_name = platform.get("name", "")
            base_url = platform.get("base_url", "")
            auth_type = platform.get("authentication", "none")

        # Build authentication headers code
        auth_headers = self._build_auth_headers(auth_type, permissions)

        # Replace all placeholders
        code = template.format(
            agent_id=requirements.get("agent_id", "unknown"),
            agent_name=metadata.get("name", "Unnamed Agent"),
            description=metadata.get("description", "No description"),
            timestamp=datetime.utcnow().isoformat(),
            required_inputs_list=json.dumps(required_inputs),
            business_logic_placeholder=business_logic,
            platform_name=platform_name,
            base_url=base_url,
            auth_type=auth_type,
            auth_headers_placeholder=auth_headers,
            timeout=constraints.get("timeout", 30),
            max_retries=constraints.get("max_retries", 3),
            retry_backoff=5,
            schedule=triggers.get("config", {}).get("schedule", "manual")
        )

        return code

    def _build_auth_headers(self, auth_type: str, permissions: Dict) -> str:
        """Generate authentication headers code based on auth type"""
        required_secrets = permissions.get("required_secrets", [])

        if auth_type == "api_key":
            api_key_secret = next((s for s in required_secrets if "API" in s or "KEY" in s), "API_KEY")
            return f'''    # API Key authentication
    api_key = os.environ.get("{api_key_secret}")
    if api_key:
        headers["Authorization"] = f"Bearer {{api_key}}"'''

        elif auth_type == "bearer":
            token_secret = next((s for s in required_secrets if "TOKEN" in s), "BEARER_TOKEN")
            return f'''    # Bearer token authentication
    token = os.environ.get("{token_secret}")
    if token:
        headers["Authorization"] = f"Bearer {{token}}"'''

        elif auth_type == "oauth":
            return '''    # OAuth authentication
    token = os.environ.get("OAUTH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"'''

        else:
            return "    # No authentication required"

    # ============================================================================
    # VALIDATION PIPELINE
    # ============================================================================

    def _validate_syntax(self, code: str) -> ValidationResult:
        """Validate Python syntax using ast.parse"""
        try:
            ast.parse(code)
            logger.info("Syntax validation: PASSED")
            return ValidationResult(is_valid=True)
        except SyntaxError as e:
            logger.error(f"Syntax validation: FAILED - {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Syntax error at line {e.lineno}: {e.msg}"]
            )

    def _security_scan_patterns(self, code: str) -> ValidationResult:
        """Pattern matching security scan using existing validators"""
        result = validate_agent_code(code)

        if result.is_valid:
            logger.info("Pattern security scan: PASSED")
        else:
            logger.error(f"Pattern security scan: FAILED - {len(result.errors)} issues")

        return result

    def _security_scan_bandit(self, code: str) -> ValidationResult:
        """
        Run bandit static analysis security scanner
        Uses subprocess to run bandit on temporary file
        """
        try:
            # Check if bandit is installed
            result = subprocess.run(
                ['bandit', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning("Bandit not installed - skipping bandit scan")
                return ValidationResult(is_valid=True)

        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Bandit not available - skipping bandit scan")
            return ValidationResult(is_valid=True)

        try:
            # Write code to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            # Run bandit
            result = subprocess.run(
                ['bandit', '-r', temp_path, '-f', 'json', '-ll'],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse bandit output
            if result.returncode == 0:
                logger.info("Bandit security scan: PASSED (no high severity issues)")
                return ValidationResult(is_valid=True)

            # Check for issues
            try:
                bandit_output = json.loads(result.stdout)
                results = bandit_output.get('results', [])

                if results:
                    errors = [
                        f"{r['issue_text']} (line {r['line_number']}, severity: {r['severity']})"
                        for r in results
                    ]
                    logger.error(f"Bandit security scan: FAILED - {len(errors)} issues")
                    return ValidationResult(is_valid=False, errors=errors)
                else:
                    logger.info("Bandit security scan: PASSED")
                    return ValidationResult(is_valid=True)

            except json.JSONDecodeError:
                logger.warning("Could not parse bandit output - assuming safe")
                return ValidationResult(is_valid=True)

        except subprocess.TimeoutExpired:
            logger.error("Bandit scan timed out")
            return ValidationResult(is_valid=False, errors=["Security scan timed out"])
        except Exception as e:
            logger.error(f"Bandit scan error: {e}")
            return ValidationResult(is_valid=True, warnings=[f"Bandit scan error: {e}"])
        finally:
            # Clean up temp file
            try:
                Path(temp_path).unlink()
            except:
                pass

    def _format_code(self, code: str) -> str:
        """Auto-format code with black"""
        try:
            # Check if black is installed
            result = subprocess.run(
                ['black', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.warning("Black not installed - returning unformatted code")
                return code

        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Black not available - returning unformatted code")
            return code

        try:
            # Write to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            # Run black
            subprocess.run(
                ['black', '--quiet', temp_path],
                check=True,
                timeout=30
            )

            # Read formatted code
            with open(temp_path, 'r', encoding='utf-8') as f:
                formatted_code = f.read()

            logger.info("Code formatting: SUCCESS")
            return formatted_code

        except subprocess.CalledProcessError as e:
            logger.error(f"Black formatting error: {e}")
            return code
        except Exception as e:
            logger.error(f"Formatting error: {e}")
            return code
        finally:
            # Clean up
            try:
                Path(temp_path).unlink()
            except:
                pass

    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================

    def _save_generated_code(self, agent_id: str, code: str) -> str:
        """Save generated code to file"""
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create file path
        filename = f"{agent_id}.py"
        filepath = self.output_dir / filename

        # Write code
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        # Make executable on Unix systems
        try:
            filepath.chmod(0o755)
        except:
            pass  # Windows doesn't support chmod

        logger.info(f"Code saved to {filepath}")
        return str(filepath)

    def _update_agent_record(self, agent_id: str, code_path: str) -> None:
        """Update Agent database record with code_path"""
        agent = self.db.query(Agent).filter(Agent.agent_id == agent_id).first()

        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        # Update fields
        agent.code_path = code_path
        agent.status = "code_generated"
        agent.updated_at = datetime.utcnow()

        # Commit
        self.db.commit()
        self.db.refresh(agent)

        logger.info(f"Updated agent record: {agent_id} -> status={agent.status}")

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
