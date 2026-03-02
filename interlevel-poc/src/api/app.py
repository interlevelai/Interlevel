from flask import Flask
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.database import init_db, create_test_user
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Create test user for development
    test_user = create_test_user()
    logger.info(f"Test user created/retrieved: {test_user.email}")

    # Register blueprints here
    from src.api.routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "healthy"}, 200

    logger.info("Flask application created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
