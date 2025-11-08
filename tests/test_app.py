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


def test_add_workout_boundary_and_invalid_values(client):
    # Boundary: minimum duration (1) and minimum calories (0)
    resp = client.post('/add', data={'workout': 'Walk', 'duration': '1', 'calories': '0'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Walk' in resp.data
    assert b'1 min' in resp.data
    assert b'0 cal' in resp.data

    # Zero duration (HTML min=1 prevents it in browser, but server currently accepts it)
    resp = client.post('/add', data={'workout': 'ZeroDur', 'duration': '0', 'calories': '10'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'ZeroDur' in resp.data
    assert b'0 min' in resp.data

    # Negative values are converted to int and currently stored by the server
    resp = client.post('/add', data={'workout': 'Neg', 'duration': '-5', 'calories': '-20'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Neg' in resp.data
    assert b'-5 min' in resp.data
    assert b'-20 cal' in resp.data

    # Decimal values should not be accepted by server-side int conversion (ignored)
    resp = client.post('/add', data={'workout': 'Decimal', 'duration': '30.5', 'calories': '250.2'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Decimal' not in resp.data

    # Non-numeric values should be rejected by conversion and not added
    resp = client.post('/add', data={'workout': 'NonNumeric', 'duration': 'thirty', 'calories': 'twofifty'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'NonNumeric' not in resp.data

    # Very large integers should be accepted (Python handles big ints)
    resp = client.post('/add', data={'workout': 'Big', 'duration': '1000000', 'calories': '999999999'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Big' in resp.data
    assert b'1000000 min' in resp.data
    assert b'999999999 cal' in resp.data
