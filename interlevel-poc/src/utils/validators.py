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
