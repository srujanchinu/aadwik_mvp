from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get('/health').status_code == 200

def test_movie_lifecycle():
    payload = {"prompt":"A child finds a magical forest", "style":"3D Animation", "language":"English", "duration_minutes":5, "aspect_ratio":"16:9"}
    r = client.post('/movies', json=payload)
    assert r.status_code == 200
    movie_id = r.json()['movie_id']
    assert client.get(f'/movies/{movie_id}').status_code == 200
    assert client.post(f'/movies/{movie_id}/cancel').json()['status'] == 'cancelled'
    assert client.post(f'/movies/{movie_id}/resume').status_code == 200
