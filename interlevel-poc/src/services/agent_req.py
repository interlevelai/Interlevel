
"""
Agent Requirements Model
Converts clarification conversations into structured JSON specifications
"""
from typing import Dict, Any, List
import json
import uuid
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm.client import LLMClient
from src.models.database import SessionLocal, Session, Agent
from src.utils.logger import get_logger
from src.utils.validators import validate_requirements_json, validate_json_string
from config.settings import settings

logger = get_logger(__name__)


REQUIREMENTS_EXTRACTION_PROMPT = """You are an expert at extracting structured requirements from conversations.

Based on the following conversation between a user and an assistant, extract a complete requirements document in JSON format.

**OUTPUT ONLY VALID JSON** with this EXACT structure:

```json
{{
  "agent_id": "GENERATE_UUID_HERE",
  "version": "1.0",
  "metadata": {{
    "name": "Short descriptive agent name",
    "description": "Brief description of what the agent does",
    "created_at": "ISO8601_TIMESTAMP",
    "tags": ["tag1", "tag2"]
  }},
  "purpose": "Clear statement of the agent's primary objective",
  "inputs": [
    {{
      "name": "input_name",
      "type": "string|integer|boolean|object|array",
      "source": "user|api|file|database|environment",
      "required": true,
      "description": "What this input is for"
    }}
  ],
  "outputs": [
    {{
      "name": "output_name",
      "type": "string|integer|boolean|object|array",
      "destination": "console|api|file|database|user",
      "description": "What this output represents"
    }}
  ],
  "triggers": {{
    "type": "manual|schedule|event|continuous",
    "config": {{
      "schedule": "cron_expression (if schedule type)",
      "event_source": "api|webhook|file (if event type)",
      "interval_seconds": 300
    }}
  }},
  "platforms": [
    {{
      "name": "REST API|GraphQL|Database|etc",
      "base_url": "https://api.example.com",
      "authentication": "api_key|oauth|bearer|none",
      "endpoints": ["GET /endpoint1", "POST /endpoint2"]
    }}
  ],
  "constraints": {{
    "max_execution_time": 300,
    "token_budget": 5000,
    "rate_limits": {{
      "requests_per_minute": 60
    }},
    "timeout": 30
  }},
  "success_criteria": [
    "Specific measurable criterion 1",
    "Specific measurable criterion 2"
  ],
  "failure_handling": {{
    "retry_policy": {{
      "max_retries": 3,
      "backoff_seconds": 5
    }},
    "notification": {{
      "method": "log|email|webhook",
      "destination": "where to notify"
    }},
    "fallback_action": "what to do if all retries fail"
  }},
  "permissions": {{
    "allowed_actions": [
      "http_request",
      "read_file",
      "write_log"
    ],
    "disallowed_actions": [
      "system_command",
      "file_write",
      "database_write"
    ],
    "required_secrets": ["API_KEY", "DATABASE_URL"]
  }}
}}
```

**CONVERSATION:**
{conversation}

**CRITICAL RULES:**
1. Output ONLY the JSON, no explanations before or after
2. Use actual values from the conversation, not placeholders
3. Generate a real UUID for agent_id
4. Use current timestamp for created_at
5. Be specific - no generic descriptions
6. If information wasn't discussed, use sensible defaults
7. Validate that all required fields are present

Now output the JSON:
"""


class AgentRequirementModel:
    """Service for generating structured requirements from conversations"""

    def __init__(self):
        self.llm = LLMClient()
        self.db = SessionLocal()
        logger.info("Agent Requirement Model initialized")

    def generate_requirements(self, session_id: str) -> Dict[str, Any]:
        """
        Generate requirements JSON from a completed clarification session

        Args:
            session_id: Completed clarification session ID

        Returns:
            Structured requirements dictionary
        """
        logger.info("Generating requirements", session_id=session_id)

        # Load session
        session = self.db.query(Session).filter(Session.session_id == session_id).first()

        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.status != "complete":
            raise ValueError(f"Session is not complete. Status: {session.status}")

        # Format conversation
        conversation = session.conversation_state
        if isinstance(conversation, str):
            conversation = json.loads(conversation)

        conv_text = self._format_conversation(conversation)

        # Generate requirements
        prompt = REQUIREMENTS_EXTRACTION_PROMPT.format(conversation=conv_text)

        try:
            response = self.llm.generate(prompt, max_tokens=2000, temperature=0.3)

            # Extract JSON from response
            requirements = self._extract_json(response)

            # Validate requirements
            validation = validate_requirements_json(requirements)

            if not validation.is_valid:
                logger.error("Generated requirements invalid",
                           errors=validation.errors)
                raise ValueError(f"Invalid requirements: {', '.join(validation.errors)}")

            if validation.warnings:
                logger.warning("Requirements validation warnings",
                             warnings=validation.warnings)

            # Save to file
            filepath = self.save_requirements(requirements)

            logger.info("Requirements generated successfully",
                       session_id=session_id,
                       agent_id=requirements.get("agent_id"),
                       filepath=filepath)

            return {
                "requirements": requirements,
                "filepath": filepath,
                "session_id": session_id,
                "warnings": validation.warnings
            }

        except Exception as e:
            logger.error(f"Failed to generate requirements: {e}",
                        session_id=session_id)
            raise

    def _format_conversation(self, conversation: List[Dict]) -> str:
        """Format conversation for prompt"""
        formatted = []

        for msg in conversation:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Skip system messages
            if role == "system":
                continue

            formatted.append(f"{role.upper()}: {content}")

        return "\n\n".join(formatted)

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        # Try to find JSON in response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")

        json_str = response[json_start:json_end]

        # Validate JSON syntax
        validation = validate_json_string(json_str)
        if not validation.is_valid:
            raise ValueError(f"Invalid JSON: {validation.errors[0]}")

        try:
            requirements = json.loads(json_str)

            # Ensure agent_id and timestamp are set
            if "agent_id" not in requirements or requirements["agent_id"] == "GENERATE_UUID_HERE":
                requirements["agent_id"] = str(uuid.uuid4())

            if "metadata" not in requirements:
                requirements["metadata"] = {}

            requirements["metadata"]["created_at"] = datetime.utcnow().isoformat()

            return requirements

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError(f"Invalid JSON structure: {e}")

    def save_requirements(self, requirements: Dict[str, Any]) -> str:
        """
        Save requirements JSON to file

        Args:
            requirements: Requirements dictionary

        Returns:
            File path where requirements were saved
        """
        agent_id = requirements.get("agent_id")

        if not agent_id:
            raise ValueError("Requirements must have an agent_id")

        # Create filename
        requirements_dir = settings.get_absolute_path(settings.REQUIREMENTS_DIR)
        requirements_dir.mkdir(parents=True, exist_ok=True)



        filepath = requirements_dir / f"{agent_id}.json"

        # Write to file
        with open(filepath, 'w') as f:
            json.dump(requirements, f, indent=2)

        logger.info(f"Requirements saved to {filepath}")

        return str(filepath)

    def load_requirements(self, agent_id: str) -> Dict[str, Any]:
        """Load requirements from file"""
        requirements_dir = settings.get_absolute_path(settings.REQUIREMENTS_DIR)
        filepath = requirements_dir / f"{agent_id}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"Requirements file not found: {filepath}")

        with open(filepath, 'r') as f:
            return json.load(f)

    def create_agent_record(self, requirements: Dict[str, Any], user_id: str) -> Agent:
        """
        Create an agent database record from requirements

        Args:
            requirements: Requirements dictionary
            user_id: User ID

        Returns:
            Created Agent instance
        """
        agent_id = requirements.get("agent_id")
        metadata = requirements.get("metadata", {})

        agent = Agent(
            agent_id=agent_id,
            user_id=user_id,
            name=metadata.get("name", "Unnamed Agent"),
            description=metadata.get("description", ""),
            requirements_json=requirements,
            status="requirements_complete"
        )

        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)

        logger.info("Agent record created", agent_id=agent_id, user_id=user_id)

        return agent

    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
