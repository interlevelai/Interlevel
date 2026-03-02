"""
Clarification Service
Gathers requirements from users through conversational AI
"""
from typing import List, Dict, Optional
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm.client import LLMClient
from src.utils.logger import get_logger
from src.models.database import Session, SessionLocal

logger = get_logger(__name__)


class ClarificationService:
    """Service for gathering agent requirements through conversation"""

    def __init__(self):
        """Initialize clarification service with LLM client"""
        self.llm = LLMClient()
        logger.info("Clarification service initialized")

    def start_session(self, user_id: str, initial_intent: str) -> Dict:
        """
        Start a new clarification session

        Args:
            user_id: ID of the user
            initial_intent: User's initial intent/description of what they want

        Returns:
            Dictionary with session_id and first question
        """
        db = SessionLocal()
        try:
            # Create new session
            session = Session(
                user_id=user_id,
                conversation_state=json.dumps([
                    {"role": "user", "content": initial_intent}
                ])
            )
            db.add(session)
            db.commit()
            db.refresh(session)

            logger.info(f"Started clarification session: {session.session_id}")

            # Generate first question
            first_question = self._generate_question(
                session.session_id,
                initial_intent,
                []
            )

            return {
                "session_id": session.session_id,
                "question": first_question,
                "conversation": [{"role": "user", "content": initial_intent}]
            }
        finally:
            db.close()

    def add_response(self, session_id: str, response: str) -> Dict:
        """
        Add user response to conversation and generate next question

        Args:
            session_id: ID of the clarification session
            response: User's response

        Returns:
            Dictionary with next question or completion status
        """
        db = SessionLocal()
        try:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()

            if not session:
                raise ValueError(f"Session {session_id} not found")

            # Load conversation
            conversation = json.loads(session.conversation_state)

            # Add user response
            conversation.append({"role": "user", "content": response})

            # Check if we have enough information
            if self._should_complete(conversation):
                logger.info(f"Clarification complete for session {session_id}")
                session.status = "complete"
                session.conversation_state = json.dumps(conversation)
                db.commit()

                return {
                    "session_id": session_id,
                    "status": "complete",
                    "summary": self._generate_summary(conversation)
                }

            # Generate next question
            next_question = self._generate_question(
                session_id,
                conversation[0]["content"],  # Original intent
                conversation[1:]  # Rest of conversation
            )

            # Add assistant response
            conversation.append({"role": "assistant", "content": next_question})

            # Save updated conversation
            session.conversation_state = json.dumps(conversation)
            db.commit()

            return {
                "session_id": session_id,
                "status": "active",
                "question": next_question,
                "conversation": conversation
            }
        finally:
            db.close()

    def _generate_question(
        self,
        session_id: str,
        user_intent: str,
        previous_exchanges: List[Dict]
    ) -> str:
        """Generate a clarifying question using LLM"""

        # Build conversation history for context
        history = ""
        if previous_exchanges:
            history = "Previous conversation:\n"
            for msg in previous_exchanges:
                role = msg["role"].capitalize()
                history += f"{role}: {msg['content']}\n"

        prompt = f"""You are an AI assistant helping users define agent requirements.
Your job is to ask ONE focused clarifying question to better understand what the user wants.

User's initial intent: {user_intent}

{history}

Based on the conversation so far, ask a specific, focused question to clarify requirements.
The question should:
1. Be specific and answerable
2. Help understand the agent's inputs, outputs, or functionality
3. Be numbered if asking multiple parts
4. Not ask for information already provided

Ask your next clarifying question:"""

        try:
            question = self.llm.generate(
                prompt,
                max_tokens=200,
                temperature=0.7
            )
            logger.debug(f"Generated question for session {session_id}")
            return question.strip()
        except Exception as e:
            logger.error(f"Failed to generate question: {e}")
            # Fallback question
            return "Could you provide more details about what this agent should do?"

    def _should_complete(self, conversation: List[Dict]) -> bool:
        """
        Determine if we have enough information to proceed

        Args:
            conversation: List of conversation messages

        Returns:
            True if clarification is complete
        """
        # Simple heuristic: if we have at least 3 exchanges, consider it complete
        # In production, this would use LLM to determine completeness
        user_messages = [msg for msg in conversation if msg["role"] == "user"]
        return len(user_messages) >= 3

    def _generate_summary(self, conversation: List[Dict]) -> str:
        """Generate a summary of gathered requirements"""

        # Build context for summary
        conv_text = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in conversation
        ])

        prompt = f"""Based on the following clarification conversation, create a structured summary of the agent requirements.

Conversation:
{conv_text}

Provide a structured summary including:
1. Agent Purpose: What the agent should do
2. Key Inputs: What data/parameters it receives
3. Key Outputs: What results it produces
4. Key Steps: Main operations/workflow
5. Success Criteria: How to know if it worked

Format as JSON."""

        try:
            summary = self.llm.generate(
                prompt,
                max_tokens=500,
                temperature=0.5
            )
            return summary.strip()
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return "Unable to generate summary"

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve a clarification session"""
        db = SessionLocal()
        try:
            session = db.query(Session).filter(
                Session.session_id == session_id
            ).first()

            if not session:
                return None

            return {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "status": session.status,
                "conversation": json.loads(session.conversation_state),
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat()
            }
        finally:
            db.close()
