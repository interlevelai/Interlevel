"""
Database models and setup for Interlevel POC
Uses SQLAlchemy ORM with SQLite
"""
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings
import uuid

Base = declarative_base()


class User(Base):
    """User model"""

    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    token_balance = Column(Integer, default=100000)

    # Relationships
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    executions = relationship("Execution", back_populates="user")

    def __repr__(self):
        return f"<User(user_id='{self.user_id}', email='{self.email}')>"


class Agent(Base):
    """Agent model"""

    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    requirements_json = Column(JSON)  # Stored as JSON
    code_path = Column(String)
    status = Column(
        String, default="draft"
    )  # draft, deployed, active, failed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="agents")
    executions = relationship("Execution", back_populates="agent")

    def __repr__(self):
        return f"<Agent(agent_id='{self.agent_id}', name='{self.name}', status='{self.status}')>"


class Execution(Base):
    """Agent execution model"""

    __tablename__ = "executions"

    execution_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.agent_id"), nullable=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    status = Column(
        String, default="pending"
    )  # pending, running, success, failed, timeout
    tokens_used = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    output = Column(Text)

    # Relationships
    agent = relationship("Agent", back_populates="executions")
    user = relationship("User", back_populates="executions")

    def __repr__(self):
        return (
            f"<Execution(execution_id='{self.execution_id}', status='{self.status}')>"
        )

    @property
    def duration(self):
        """Calculate execution duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class Session(Base):
    """Clarification session model"""

    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    conversation_state = Column(JSON)  # Stored as JSON array of messages
    status = Column(String, default="active")  # active, complete, abandoned
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(
        DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24)
    )

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(session_id='{self.session_id}', status='{self.status}')>"

    @property
    def is_expired(self):
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at


# Database engine and session
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    connect_args={"check_same_thread": False},  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_test_user(email: str = "test@interlevel.com") -> User:
    """Create a test user for development"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return existing_user

        user = User(email=email, token_balance=100000)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
    print("Database schema created successfully")
