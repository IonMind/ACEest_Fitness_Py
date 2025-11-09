import html
import re
import pytest
from src.app import (
    app,
    workouts,
    CATEGORIES,
    WORKOUT_CHART_DATA,
    DIET_PLANS,
    user_info,
    MET_VALUES,
)

@pytest.fixture(autouse=True)
def client():
    """Provide a test client and clear global mutable state for isolation."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    # Clear workouts
    for entries in workouts.values():
        entries.clear()
    # Clear user profile
    user_info.clear()
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'ACEestFitness and Gym' in response.data
    assert '🏋️ Log Workouts'.encode() in response.data
    assert '💡 Workout Plan'.encode() in response.data
    assert '🥗 Diet Guide'.encode() in response.data
    assert '📈 Progress Tracker'.encode() in response.data
    for category in CATEGORIES:
        assert category.encode() in response.data
    assert b'name="category"' in response.data

def test_add_workout_valid(client):
    response = client.post('/add', data={
        'workout': 'Running',
        'duration': '30',
        'calories': '250',
        'category': 'Workout'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Running' in response.data
    assert b'30 min' in response.data
    assert b'250 cal' in response.data
    assert '✅ Added Running (30 min) to Workout.'.encode() in response.data
    assert len(workouts['Workout']) == 1

def test_add_workout_invalid(client):
    # Missing fields
    response = client.post('/add', data={
        'workout': '',
        'duration': '',
        'calories': '',
        'category': 'Workout'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please fill in all fields before submitting.' in response.data
    assert b'No workouts logged yet.' in response.data
    assert sum(len(entries) for entries in workouts.values()) == 0

def test_multiple_workouts(client):
    client.post('/add', data={'workout': 'Cycling', 'duration': '45', 'calories': '400', 'category': 'Warm-up'}, follow_redirects=True)
    client.post('/add', data={'workout': 'Yoga', 'duration': '60', 'calories': '180', 'category': 'Cool-down'}, follow_redirects=True)
    response = client.get('/')
    assert b'Cycling' in response.data
    assert b'Yoga' in response.data
    assert b'45 min' in response.data
    assert b'60 min' in response.data
    assert b'400 cal' in response.data
    assert b'180 cal' in response.data
    assert b'No sessions recorded for this category.' in response.data  # Workout category remains empty


def test_add_workout_boundary_and_invalid_values(client):
    # Boundary: minimum duration (1) and minimum calories (0)
    resp = client.post('/add', data={'workout': 'Walk', 'duration': '1', 'calories': '0', 'category': 'Workout'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Walk' in resp.data
    assert b'1 min' in resp.data
    assert b'0 cal' in resp.data

    # Zero duration should be rejected
    resp = client.post('/add', data={'workout': 'ZeroDur', 'duration': '0', 'calories': '10', 'category': 'Workout'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Duration must be a positive number.' in resp.data
    assert b'ZeroDur' not in resp.data

    # Negative duration
    resp = client.post('/add', data={'workout': 'NegDur', 'duration': '-5', 'calories': '20', 'category': 'Workout'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Duration must be a positive number.' in resp.data
    assert b'NegDur' not in resp.data

    # Negative calories
    resp = client.post('/add', data={'workout': 'NegCal', 'duration': '10', 'calories': '-20', 'category': 'Workout'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Calories cannot be negative.' in resp.data
    assert b'NegCal' not in resp.data

    # Decimal values should not be accepted by server-side int conversion (ignored)
    resp = client.post('/add', data={'workout': 'Decimal', 'duration': '30.5', 'calories': '250.2', 'category': 'Workout'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Duration and calories must be numeric values.' in resp.data
    assert b'Decimal' not in resp.data

    # Non-numeric values should be rejected by conversion and not added
    resp = client.post('/add', data={'workout': 'NonNumeric', 'duration': 'thirty', 'calories': 'twofifty', 'category': 'Workout'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Duration and calories must be numeric values.' in resp.data
    assert b'NonNumeric' not in resp.data

    # Very large integers should be accepted (Python handles big ints)
    resp = client.post('/add', data={'workout': 'Big', 'duration': '1000000', 'calories': '999999999', 'category': 'Workout'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Big' in resp.data
    assert b'1000000 min' in resp.data
    assert b'999999999 cal' in resp.data


def test_index_returns_html_and_contains_form(client):
    """GET / should return HTML and include the workout form fields."""
    resp = client.get('/')
    assert resp.status_code == 200
    # Flask test client exposes content_type
    assert 'text/html' in resp.content_type
    # Check presence of form inputs
    assert b'name="workout"' in resp.data
    assert b'name="duration"' in resp.data
    assert b'name="calories"' in resp.data
    assert b'name="category"' in resp.data
    assert b'Personalized Workout Plan Guide' in resp.data
    assert b'Nutritional Goal Setting Guide' in resp.data


def test_add_post_redirects_to_index(client):
    """A POST to /add without following redirects should return 302 and Location header."""
    resp = client.post('/add', data={'workout': 'RedirectTest', 'duration': '10', 'calories': '100', 'category': 'Workout'}, follow_redirects=False)
    assert resp.status_code == 302
    # Location header typically is absolute (http://localhost/) in Flask test client
    assert resp.headers.get('Location', '').endswith('/')


def test_add_get_method_not_allowed(client):
    """GET /add is not allowed (route only accepts POST) and should return 405."""
    resp = client.get('/add')
    assert resp.status_code == 405


def test_unknown_route_returns_404(client):
    resp = client.get('/this-route-does-not-exist')
    assert resp.status_code == 404


def test_summary_route_empty(client):
    resp = client.get('/summary')
    assert resp.status_code == 200
    assert b'Total Time Spent: 0 minutes' in resp.data
    assert b'Good start! Keep moving' in resp.data


def test_summary_route_with_sessions(client):
    client.post('/add', data={'workout': 'Sprint', 'duration': '20', 'calories': '200', 'category': 'Warm-up'}, follow_redirects=True)
    client.post('/add', data={'workout': 'Lift', 'duration': '45', 'calories': '350', 'category': 'Workout'}, follow_redirects=True)
    client.post('/add', data={'workout': 'Stretch', 'duration': '15', 'calories': '50', 'category': 'Cool-down'}, follow_redirects=True)

    resp = client.get('/summary')
    assert resp.status_code == 200
    assert b'Sprint' in resp.data
    assert b'Lift' in resp.data
    assert b'Stretch' in resp.data
    assert b'Total Time Spent: 80 minutes' in resp.data
    assert b'Excellent dedication! Keep up the great work' in resp.data


def test_progress_tab_initial_state(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'No workout data logged yet. Log a session to see your progress!' in resp.data
    assert b'id="progress-summary" style="display:none"' in resp.data
    assert b'LIFETIME TOTAL: 0 minutes logged across all categories.' in resp.data


def test_progress_tab_after_logging(client):
    client.post('/add', data={'workout': 'Intervals', 'duration': '30', 'calories': '320', 'category': 'Workout'}, follow_redirects=True)
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'LIFETIME TOTAL: 30 minutes logged across all categories.' in resp.data
    assert b'id="progress-empty" class="empty-progress" style="display:none"' in resp.data
    page = resp.get_data(as_text=True)
    assert '"Workout": 30' in page
    assert '"Warm-up": 0' in page


def test_reference_tabs_render_content(client):
    resp = client.get('/')
    assert resp.status_code == 200
    for exercises in WORKOUT_CHART_DATA.values():
        for exercise in exercises:
            assert html.escape(exercise).encode() in resp.data
    for foods in DIET_PLANS.values():
        for item in foods:
            assert html.escape(item).encode() in resp.data


# ---------------- New Feature Tests (Parity with Tkinter v1.3) ---------------- #

def test_user_info_save_valid(client):
    resp = client.post('/user/save', data={
        'name': 'Test User',
        'regn_id': 'R123',
        'age': '30',
        'gender': 'M',
        'height': '180',
        'weight': '80',
        'weekly_cal_goal': '2500',
    }, follow_redirects=True)
    assert resp.status_code == 200
    # Flash message present
    assert b'User info saved! BMI=' in resp.data
    # Derived values
    assert user_info['name'] == 'Test User'
    assert user_info['bmi'] == pytest.approx(80 / (1.8 * 1.8))
    # BMR (M): 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    assert user_info['bmr'] == pytest.approx(1780, rel=0.01)
    # Progress bar shows weekly calories (0 / goal initially)
    assert b'Weekly Calories:' in resp.data


def test_user_info_save_invalid_gender(client):
    resp = client.post('/user/save', data={
        'name': 'Bad',
        'regn_id': 'X1',
        'age': '25',
        'gender': 'X',
        'height': '170',
        'weight': '65',
        'weekly_cal_goal': '2000',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Invalid input:' in resp.data
    assert user_info == {}


def test_add_workout_auto_valid(client):
    # No user info saved: will default weight=70
    resp = client.post('/add-auto', data={
        'workout': 'QuickIntervals',
        'duration': '10',
        'category': 'Warm-up'
    }, follow_redirects=True)
    assert resp.status_code == 200
    # Calories estimate: MET=3, weight=70, duration=10 -> round((3*3.5*70/200)*10)=37
    assert b'QuickIntervals' in resp.data
    assert b'37 kcal' in resp.data or b'~37 kcal' in resp.data
    assert len(workouts['Warm-up']) == 1


def test_add_workout_auto_with_user_weight(client):
    client.post('/user/save', data={
        'name': 'WUser', 'regn_id': 'R9', 'age': '40', 'gender': 'F', 'height': '165', 'weight': '55', 'weekly_cal_goal': '2000'
    }, follow_redirects=True)
    resp = client.post('/add-auto', data={
        'workout': 'WarmFlow',
        'duration': '20',
        'category': 'Warm-up'
    }, follow_redirects=True)
    assert resp.status_code == 200
    # Calories: (3*3.5*55/200)*20 = (577.5/200)*20 = 2.8875*20=57.75 -> 58
    assert b'WarmFlow' in resp.data
    assert b'58 kcal' in resp.data or b'~58 kcal' in resp.data
    assert workouts['Warm-up'][0]['calories'] == 58


def test_export_pdf_requires_user_info(client):
    # Without user info should redirect and flash error
    resp = client.get('/export/pdf', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Please save user info first!' in resp.data


def test_export_pdf_success(client):
    client.post('/user/save', data={
        'name': 'PDFUser', 'regn_id': 'RID', 'age': '28', 'gender': 'M', 'height': '175', 'weight': '70', 'weekly_cal_goal': '2100'
    })
    client.post('/add', data={'workout': 'Run', 'duration': '30', 'calories': '300', 'category': 'Workout'})
    resp = client.get('/export/pdf')
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/pdf'
    pdf_bytes = resp.data[:10]
    assert pdf_bytes.startswith(b'%PDF')


def test_weekly_calories_progress_bar(client):
    client.post('/user/save', data={
        'name': 'CalUser', 'regn_id': 'C1', 'age': '26', 'gender': 'F', 'height': '160', 'weight': '60', 'weekly_cal_goal': '500'
    }, follow_redirects=True)
    # Add workouts so weekly calories accumulate
    client.post('/add', data={'workout': 'Lift', 'duration': '45', 'calories': '350', 'category': 'Workout'}, follow_redirects=True)
    client.post('/add', data={'workout': 'Stretch', 'duration': '15', 'calories': '50', 'category': 'Cool-down'}, follow_redirects=True)
    page = client.get('/').get_data(as_text=True)
    # Weekly Calories: 400 / 500 (350 + 50)
    assert 'Weekly Calories:' in page
    # Allow HTML tags between label and numeric values
    assert re.search(r'Weekly Calories:\s*(?:</?[^>]+>\s*)*400\s*/\s*500', page)
    # Progress percent should be 80%
    assert 'width: 80%' in page
