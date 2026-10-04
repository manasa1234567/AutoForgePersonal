from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_hello_endpoint():
    response = client.get('/hello')
    assert response.status_code == 200
    json_data = response.json()
    assert 'message' in json_data
    assert json_data['message'] == 'Hello World'
