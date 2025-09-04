import pytest
from src.app import app, workouts

@pytest.fixture(autouse=True)
def client():
    app.config['TESTING'] = True
    workouts.clear()  # Ensure test isolation
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'ACEestFitness and Gym' in response.data

def test_add_workout_valid(client):
    response = client.post('/add', data={
        'workout': 'Running',
        'duration': '30',
        'calories': '250'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Running' in response.data
    assert b'30 min' in response.data
    assert b'250 cal' in response.data

def test_add_workout_invalid(client):
    # Missing fields
    response = client.post('/add', data={
        'workout': '',
        'duration': '',
        'calories': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should not add anything
    assert b'No workouts logged yet.' in response.data

def test_multiple_workouts(client):
    client.post('/add', data={'workout': 'Cycling', 'duration': '45', 'calories': '400'})
    client.post('/add', data={'workout': 'Yoga', 'duration': '60', 'calories': '180'})
    response = client.get('/')
    assert b'Cycling' in response.data
    assert b'Yoga' in response.data
    assert b'45 min' in response.data
    assert b'60 min' in response.data
    assert b'400 cal' in response.data
    assert b'180 cal' in response.data
