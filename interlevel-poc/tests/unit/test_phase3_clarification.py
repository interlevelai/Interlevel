"""
Phase 3: Clarification Service - Unit Tests
Tests for clarification service and API endpoints
"""
import pytest
import json


@pytest.fixture
def db_cleanup():
    """Clean up test database before and after tests"""
    from src.models.database import SessionLocal, Base, engine

    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=engine)


# Clarification Service Tests
def test_clarification_service_initialization(db_cleanup):
    """Test clarification service initializes"""
    from src.services.clarification import ClarificationService

    try:
        service = ClarificationService()
        assert service is not None
        assert service.llm is not None
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_clarification_start_session(db_cleanup):
    """Test starting a clarification session"""
    from src.services.clarification import ClarificationService

    try:
        service = ClarificationService()
        result = service.start_session(
            "test_user",
            "I want an agent that fetches weather"
        )

        assert "session_id" in result
        assert "question" in result
        assert result["question"] is not None
        assert len(result["question"]) > 0
        assert "conversation" in result
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_clarification_get_session(db_cleanup):
    """Test retrieving a session"""
    from src.services.clarification import ClarificationService

    try:
        service = ClarificationService()
        session = service.start_session("test_user", "I want an agent")
        session_id = session["session_id"]

        retrieved = service.get_session(session_id)

        assert retrieved is not None
        assert retrieved["session_id"] == session_id
        assert retrieved["user_id"] == "test_user"
        assert retrieved["status"] == "active"
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_clarification_add_response(db_cleanup):
    """Test adding response to session"""
    from src.services.clarification import ClarificationService

    try:
        service = ClarificationService()
        session = service.start_session("test_user", "I want a weather agent")
        session_id = session["session_id"]

        result = service.add_response(session_id, "It should fetch data for any city")

        assert "session_id" in result
        assert result["session_id"] == session_id
        assert result["status"] in ["active", "complete"]
    except ConnectionError:
        pytest.skip("Ollama server not running")


def test_clarification_session_expiration(db_cleanup):
    """Test session expiration property"""
    from src.services.clarification import ClarificationService
    from src.models.database import SessionLocal, Session
    import json

    service = ClarificationService()
    session = service.start_session("test_user", "I want an agent")
    session_id = session["session_id"]

    db = SessionLocal()
    db_session = db.query(Session).filter(
        Session.session_id == session_id
    ).first()

    assert db_session is not None
    assert not db_session.is_expired
    db.close()


# API Endpoint Tests
@pytest.fixture
def client():
    """Create Flask test client"""
    from src.api.app import create_app

    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_api_health_endpoint(client):
    """Test /health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'


def test_api_status_endpoint(client):
    """Test /api/status endpoint"""
    response = client.get('/api/status')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'


def test_api_start_session_endpoint(client):
    """Test POST /api/clarification/session endpoint"""
    response = client.post(
        '/api/clarification/session',
        json={
            'user_id': 'test_user',
            'intent': 'I want a weather agent'
        }
    )

    assert response.status_code == 201
    data = response.json
    assert 'session_id' in data
    assert 'question' in data
    assert 'conversation' in data


def test_api_start_session_missing_fields(client):
    """Test POST /api/clarification/session with missing fields"""
    response = client.post(
        '/api/clarification/session',
        json={'user_id': 'test_user'}  # Missing 'intent'
    )

    assert response.status_code == 400
    assert 'error' in response.json


def test_api_get_session_endpoint(client):
    """Test GET /api/clarification/session/<id> endpoint"""
    # First, create a session
    create_response = client.post(
        '/api/clarification/session',
        json={
            'user_id': 'test_user',
            'intent': 'I want an agent'
        }
    )
    session_id = create_response.json['session_id']

    # Then retrieve it
    response = client.get(f'/api/clarification/session/{session_id}')

    assert response.status_code == 200
    data = response.json
    assert data['session_id'] == session_id
    assert data['status'] == 'active'


def test_api_get_session_not_found(client):
    """Test GET /api/clarification/session with non-existent ID"""
    response = client.get('/api/clarification/session/non-existent-id')

    assert response.status_code == 404
    assert 'error' in response.json


def test_api_add_response_endpoint(client):
    """Test POST /api/clarification/session/<id>/response endpoint"""
    # Create session
    create_response = client.post(
        '/api/clarification/session',
        json={
            'user_id': 'test_user',
            'intent': 'I want a weather agent'
        }
    )
    session_id = create_response.json['session_id']

    # Add response
    response = client.post(
        f'/api/clarification/session/{session_id}/response',
        json={'response': 'It should fetch weather for any city'}
    )

    assert response.status_code == 200
    data = response.json
    assert data['session_id'] == session_id
    assert data['status'] in ['active', 'complete']


def test_api_add_response_missing_fields(client):
    """Test POST response with missing fields"""
    response = client.post(
        '/api/clarification/session/some-id/response',
        json={}  # Missing 'response' field
    )

    assert response.status_code == 400
    assert 'error' in response.json


def test_api_workflow_complete_conversation(client):
    """Test complete conversation workflow"""
    # 1. Start session
    session_response = client.post(
        '/api/clarification/session',
        json={
            'user_id': 'workflow_test',
            'intent': 'I need an agent that monitors server uptime'
        }
    )
    assert session_response.status_code == 201
    session_id = session_response.json['session_id']

    # 2. Get session
    get_response = client.get(f'/api/clarification/session/{session_id}')
    assert get_response.status_code == 200
    assert len(get_response.json['conversation']) == 1

    # 3. Add multiple responses
    responses = [
        "It should ping the server every minute",
        "It should send an email if server is down",
        "It should log all results to a file"
    ]

    for response_text in responses:
        response = client.post(
            f'/api/clarification/session/{session_id}/response',
            json={'response': response_text}
        )
        assert response.status_code == 200

    # 4. Check final session state
    final_response = client.get(f'/api/clarification/session/{session_id}')
    assert final_response.status_code == 200
    final_data = final_response.json
    assert final_data['status'] in ['active', 'complete']
