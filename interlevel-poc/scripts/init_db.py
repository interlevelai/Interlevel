"""
Database initialization script
Creates tables and optionally seeds test data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.database import init_db, SessionLocal
from src.models.database import User, Agent
from config.settings import settings


def seed_test_data():
    """Seed database with test data"""
    db = SessionLocal()

    try:
        # Create test user
        print("Creating test user...")
        test_user = User(
            email="test@interlevel.com",
            token_balance=100000
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Test user created: {test_user.user_id}")

        # Create sample agent
        print("Creating sample agent...")
        sample_agent = Agent(
            user_id=test_user.user_id,
            name="Weather Checker",
            description="Checks weather API and logs results",
            requirements_json={
                "purpose": "Check weather and alert if rain",
                "inputs": [{"name": "location", "type": "string"}],
                "outputs": [{"name": "alert", "type": "string"}],
                "triggers": {"type": "manual"}
            },
            status="draft"
        )
        db.add(sample_agent)
        db.commit()
        db.refresh(sample_agent)
        print(f"✅ Sample agent created: {sample_agent.agent_id}")

        print("\n✅ Test data seeded successfully")
        print(f"   User ID: {test_user.user_id}")
        print(f"   Email: {test_user.email}")
        print(f"   Token Balance: {test_user.token_balance}")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  Interlevel POC - Database Initialization")
    print("=" * 60)
    print()

    # Initialize database
    print("Creating database schema...")
    init_db()

    # Ask to seed test data
    response = input("\nSeed with test data? (y/n): ")
    if response.lower() == 'y':
        seed_test_data()

    print("\n✅ Database initialization complete!")
    print(f"   Database location: {settings.DATABASE_URL}")
