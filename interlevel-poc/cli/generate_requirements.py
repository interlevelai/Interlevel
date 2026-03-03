"""
CLI tool for generating requirements JSON from clarification session
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.agent_req import AgentRequirementModel
from src.models.database import init_db


def generate_requirements_cli():
    """Generate requirements from session ID"""
    print("="*70)
    print("  INTERLEVEL - Generate Agent Requirements")
    print("="*70)
    print()

    # Get session ID
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
    else:
        session_id = input("Enter session ID: ").strip()

    if not session_id:
        print("❌ Session ID required")
        return

    print(f"\nGenerating requirements for session: {session_id}")
    print("-"*70)

    # Generate requirements
    service = AgentRequirementModel()

    try:
        result = service.generate_requirements(session_id)

        requirements = result["requirements"]
        filepath = result["filepath"]

        print("\n✅ Requirements generated successfully!")
        print(f"\nFile saved: {filepath}")
        print(f"Agent ID: {requirements.get('agent_id')}")
        print(f"Agent Name: {requirements.get('metadata', {}).get('name')}")

        if result.get("warnings"):
            print("\n⚠️  Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")

        print("\n" + "="*70)
        print("  Requirements JSON")
        print("="*70)
        print(json.dumps(requirements, indent=2))
        print("="*70)

        print("\nNext step:")
        print(f"Generate agent code: python cli/generate_code.py {requirements.get('agent_id')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    init_db()

    try:
        generate_requirements_cli()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
