
# Flask web app for ACEestFitness and Gym
import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "aceest-dev-secret")

CATEGORIES = ("Warm-up", "Workout", "Cool-down")
workouts = {category: [] for category in CATEGORIES}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>ACEestFitness and Gym</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }
        .container { max-width: 600px; margin: 40px auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px #ccc; }
        h1 { color: #2c3e50; }
        form { margin-bottom: 24px; }
        label { display: block; margin-top: 12px; }
        input[type=text], input[type=number] { width: 100%; padding: 8px; margin-top: 4px; border: 1px solid #ccc; border-radius: 4px; }
        select { width: 100%; padding: 8px; margin-top: 4px; border: 1px solid #ccc; border-radius: 4px; }
        button { margin-top: 16px; padding: 10px 20px; background: #27ae60; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #219150; }
        .workout-list { margin-top: 32px; }
        .workout-item { background: #eafaf1; padding: 10px; border-radius: 4px; margin-bottom: 8px; }
        .messages { margin-top: 16px; }
        .messages .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; padding: 10px; border-radius: 4px; margin-bottom: 8px; }
        .messages .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px; margin-bottom: 8px; }
        .actions { margin-top: 16px; text-align: center; }
        .actions a { color: #007bff; text-decoration: none; }
        .actions a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ACEestFitness and Gym</h1>
        <form method="POST" action="{{ url_for('add_workout') }}">
            <label for="workout">Workout Name:</label>
            <input type="text" id="workout" name="workout" required>

            <label for="duration">Duration (minutes):</label>
            <input type="number" id="duration" name="duration" min="1" required>

            <label for="calories">Calories Burned:</label>
            <input type="number" id="calories" name="calories" min="0" required>

            <label for="category">Select Category:</label>
            <select id="category" name="category" required>
                {% for category in categories %}
                    <option value="{{ category }}" {% if category == default_category %}selected{% endif %}>{{ category }}</option>
                {% endfor %}
            </select>

            <button type="submit">Add Workout</button>
        </form>

        <div class="messages">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, msg in messages %}
                        <div class="{{ category }}">{{ msg }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>

        <div class="workout-list">
            <h2>Logged Workouts</h2>
            {% if total_sessions %}
                {% for category, sessions in workouts.items() %}
                    <h3>{{ category }}</h3>
                    {% if sessions %}
                        {% for entry in sessions %}
                            <div class="workout-item">
                                <strong>{{ entry.workout }}</strong> - {{ entry.duration }} min, {{ entry.calories }} cal<br>
                                <small>Logged at {{ entry.timestamp }}</small>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p>No sessions recorded for this category.</p>
                    {% endif %}
                {% endfor %}
            {% else %}
                <p>No workouts logged yet.</p>
            {% endif %}
        </div>
        <div class="actions">
            <a href="{{ url_for('summary') }}">View Summary</a>
        </div>
        <footer style="margin-top:24px; font-size:0.9em; color:#666; text-align:center;">
            Version: {{ version }}
        </footer>
    </div>
</body>
</html>
"""

SUMMARY_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>Workout Summary</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }
        .container { max-width: 600px; margin: 40px auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px #ccc; }
        h1 { color: #2c3e50; }
        h2 { color: #007bff; }
        .session { margin-bottom: 16px; padding-left: 12px; }
        .empty { color: #777; font-style: italic; }
        .total { margin-top: 24px; font-weight: bold; color: #28a745; }
        .note { margin-top: 12px; font-style: italic; color: #555; }
        a { display: inline-block; margin-top: 24px; color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Session Summary</h1>
        {% for category, sessions in workouts.items() %}
            <h2>{{ category }}</h2>
            {% if sessions %}
                {% for entry in sessions %}
                    <div class="session">{{ loop.index }}. {{ entry.workout }} - {{ entry.duration }} min ({{ entry.calories }} cal) at {{ entry.timestamp }}</div>
                {% endfor %}
            {% else %}
                <div class="session empty">No sessions recorded.</div>
            {% endif %}
        {% endfor %}
        <div class="total">Total Time Spent: {{ total_time }} minutes</div>
        <div class="note">{{ motivation }}</div>
        <a href="{{ url_for('index') }}">Back to Tracker</a>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    version = os.environ.get('APP_VERSION', 'unknown')
    total_sessions = sum(len(sessions) for sessions in workouts.values())
    return render_template_string(
        HTML_TEMPLATE,
        workouts=workouts,
        categories=CATEGORIES,
        default_category="Workout",
        total_sessions=total_sessions,
        version=version,
    )

@app.route('/add', methods=['POST'])
def add_workout():
    workout = request.form.get('workout')
    duration = request.form.get('duration')
    calories = request.form.get('calories')
    category = request.form.get('category', 'Workout')

    if not (workout and duration and calories and category):
        flash("Please fill in all fields before submitting.", "error")
        return redirect(url_for('index'))

    if category not in CATEGORIES:
        flash("Invalid category selected.", "error")
        return redirect(url_for('index'))

    try:
        duration = int(duration)
        calories = int(calories)
    except ValueError:
        flash("Duration and calories must be numeric values.", "error")
        return redirect(url_for('index'))

    if duration <= 0:
        flash("Duration must be a positive number.", "error")
        return redirect(url_for('index'))

    if calories < 0:
        flash("Calories cannot be negative.", "error")
        return redirect(url_for('index'))

    entry = {
        'workout': workout.strip(),
        'duration': duration,
        'calories': calories,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    workouts[category].append(entry)
    flash(f"Added {entry['workout']} ({duration} min) to {category}.", "info")
    return redirect(url_for('index'))

@app.route('/summary', methods=['GET'])
def summary():
    total_time = sum(entry['duration'] for sessions in workouts.values() for entry in sessions)
    if total_time < 30:
        motivation = "Good start! Keep moving 💪"
    elif total_time < 60:
        motivation = "Nice effort! You're building consistency 🔥"
    else:
        motivation = "Excellent dedication! Keep up the great work 🏆"

    return render_template_string(
        SUMMARY_TEMPLATE,
        workouts=workouts,
        total_time=total_time,
        motivation=motivation,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)