
# Flask web app for ACEestFitness and Gym
import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "aceest-dev-secret")

CATEGORIES = ("Warm-up", "Workout", "Cool-down")
workouts = {category: [] for category in CATEGORIES}

WORKOUT_CHART_DATA = {
    "Warm-up": [
        "5 min Jog",
        "Jumping Jacks",
        "Arm Circles",
        "Leg Swings",
        "Dynamic Stretching",
    ],
    "Workout": [
        "Push-ups",
        "Squats",
        "Plank",
        "Lunges",
        "Burpees",
        "Crunches",
    ],
    "Cool-down": [
        "Slow Walking",
        "Static Stretching",
        "Deep Breathing",
        "Yoga Poses",
    ],
}

DIET_PLANS = {
    "Weight Loss": [
        "Oatmeal with Fruits",
        "Grilled Chicken Salad",
        "Vegetable Soup",
        "Brown Rice & Stir-fry Veggies",
    ],
    "Muscle Gain": [
        "Egg Omelet",
        "Chicken Breast",
        "Quinoa & Beans",
        "Protein Shake",
        "Greek Yogurt with Nuts",
    ],
    "Endurance": [
        "Banana & Peanut Butter",
        "Whole Grain Pasta",
        "Sweet Potatoes",
        "Salmon & Avocado",
        "Trail Mix",
    ],
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>ACEestFitness and Gym</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }
        .container { max-width: 760px; margin: 40px auto; background: #fff; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px #ccc; }
        h1 { color: #2c3e50; margin-bottom: 8px; }
        .subtitle { color: #555; margin-top: 0; }
        form { margin-bottom: 24px; }
        label { display: block; margin-top: 12px; }
        input[type=text], input[type=number] { width: 100%; padding: 8px; margin-top: 4px; border: 1px solid #ccc; border-radius: 4px; }
        select { width: 100%; padding: 8px; margin-top: 4px; border: 1px solid #ccc; border-radius: 4px; }
        button { margin-top: 16px; padding: 10px 20px; background: #27ae60; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #219150; }
        .messages { margin-top: 16px; }
        .messages .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; padding: 10px; border-radius: 4px; margin-bottom: 8px; }
        .messages .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px; margin-bottom: 8px; }
        .workout-list { margin-top: 32px; }
        .workout-item { background: #eafaf1; padding: 10px; border-radius: 4px; margin-bottom: 8px; }
        .actions { margin-top: 16px; text-align: center; }
        .actions a { color: #007bff; text-decoration: none; }
        .actions a:hover { text-decoration: underline; }
        .tabs { margin-top: 24px; }
        .tab-nav { display: flex; gap: 8px; flex-wrap: wrap; }
        .tab-btn { background: #e0e7ef; border: none; padding: 10px 16px; border-radius: 4px; cursor: pointer; color: #2c3e50; transition: background 0.3s; }
        .tab-btn:hover { background: #d0d9e4; }
        .tab-btn.active { background: #007bff; color: #fff; }
        .tab-panel { display: none; margin-top: 24px; }
        .tab-panel.active { display: block; }
        .chart-group, .diet-group { background: #f8f9fa; border-radius: 6px; padding: 16px; margin-bottom: 16px; }
        .chart-group h3, .diet-group h3 { margin-top: 0; }
        ul { padding-left: 18px; }
        footer { margin-top: 24px; font-size: 0.9em; color: #666; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ACEestFitness and Gym</h1>
        <p class="subtitle">Log your training, follow curated workout flows, and keep nutrition aligned.</p>
        <div class="tabs">
            <div class="tab-nav">
                <button type="button" class="tab-btn active" data-target="log-tab">Log Workouts</button>
                <button type="button" class="tab-btn" data-target="chart-tab">Workout Chart</button>
                <button type="button" class="tab-btn" data-target="diet-tab">Diet Chart</button>
            </div>
            <div id="log-tab" class="tab-panel active">
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
            </div>
            <div id="chart-tab" class="tab-panel">
                <h2>Personalized Workout Chart</h2>
                {% for category, exercises in workout_chart.items() %}
                    <div class="chart-group">
                        <h3>{{ category }}</h3>
                        <ul>
                            {% for exercise in exercises %}
                                <li>{{ exercise }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                {% endfor %}
            </div>
            <div id="diet-tab" class="tab-panel">
                <h2>Best Diet Chart for Fitness Goals</h2>
                {% for goal, foods in diet_plans.items() %}
                    <div class="diet-group">
                        <h3>{{ goal }}</h3>
                        <ul>
                            {% for item in foods %}
                                <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                {% endfor %}
            </div>
        </div>
        <footer>
            Version: {{ version }}
        </footer>
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', function () {
        var buttons = document.querySelectorAll('.tab-btn');
        var panels = document.querySelectorAll('.tab-panel');
        buttons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                buttons.forEach(function (item) { item.classList.remove('active'); });
                panels.forEach(function (panel) { panel.classList.remove('active'); });
                btn.classList.add('active');
                var target = document.getElementById(btn.dataset.target);
                if (target) {
                    target.classList.add('active');
                }
            });
        });
    });
    </script>
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
        workout_chart=WORKOUT_CHART_DATA,
        diet_plans=DIET_PLANS,
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