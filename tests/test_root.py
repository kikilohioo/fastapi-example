from app.main import app


def test_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json().get('message') == 'Hello World'
