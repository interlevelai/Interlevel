from flask import Flask
from flask_cors import CORS


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)

    # Register blueprints here
    from src.api.routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "healthy"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
