
# Flask web app for ACEestFitness and Gym
import os
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "aceest-dev-secret")

CATEGORIES = ("Warm-up", "Workout", "Cool-down")
workouts = {category: [] for category in CATEGORIES}

WORKOUT_CHART_DATA = {
    "Warm-up (5-10 min)": [
        "5 min light cardio (Jog/Cycle)",
        "Jumping Jacks (30 reps)",
        "Arm Circles (15 forward/backward)",
        "Leg Swings (10 per leg)",
    ],
    "Strength Workout (45-60 min)": [
        "Push-ups (3 x 10-15)",
        "Squats (3 x 15-20)",
        "Plank (3 x 60 seconds)",
        "Lunges (3 x 10 per leg)",
        "Dumbbell Rows (3 x 12)",
    ],
    "Cool-down (5 min)": [
        "Slow Walking",
        "Static Stretching (hold 30s each)",
        "Deep Breathing Exercises",
        "Short Yoga Flow",
    ],
}

DIET_PLANS = {
    "🎯 Weight Loss": [
        "Breakfast: Oatmeal with berries",
        "Lunch: Grilled chicken/tofu salad",
        "Snack: Handful of nuts",
        "Dinner: Vegetable soup with lentils",
    ],
    "💪 Muscle Gain": [
        "Breakfast: 3-egg omelet with spinach",
        "Lunch: Chicken breast, quinoa, steamed veggies",
        "Snack: Protein shake and Greek yogurt",
        "Dinner: Salmon with roasted sweet potatoes",
    ],
    "🏃 Endurance Focus": [
        "Pre-workout: Banana with peanut butter",
        "Lunch: Whole grain pasta with lean protein",
        "Snack: Trail mix with dried fruits",
        "Dinner: Salmon & avocado salad",
    ],
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>ACEestFitness and Gym</title>
    <style>
        body { font-family: Arial, sans-serif; background: #eef1f4; margin: 0; padding: 0; }
        .container { max-width: 820px; margin: 40px auto; background: #fff; padding: 28px; border-radius: 10px; box-shadow: 0 8px 22px rgba(44, 62, 80, 0.15); }
        h1 { color: #2c3e50; margin-bottom: 8px; font-size: 2em; }
        .subtitle { color: #555; margin-top: 0; font-size: 1.05em; }
        form { margin-bottom: 24px; }
        label { display: block; margin-top: 12px; font-weight: bold; color: #2c3e50; }
        input[type=text], input[type=number], select { width: 100%; padding: 10px; margin-top: 6px; border: 1px solid #ced4da; border-radius: 6px; background: #f8f9fa; }
        input[type=text]:focus, input[type=number]:focus, select:focus { outline: none; border-color: #007bff; background: #fff; }
        button { margin-top: 18px; padding: 12px 20px; background: #28a745; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; letter-spacing: 0.4px; }
        button:hover { background: #219150; }
        .messages { margin-top: 16px; }
        .messages .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; padding: 10px; border-radius: 6px; margin-bottom: 8px; }
        .messages .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; padding: 10px; border-radius: 6px; margin-bottom: 8px; }
        .workout-list { margin-top: 32px; }
        .workout-item { background: #eafaf1; padding: 12px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid #28a745; }
        .actions { margin-top: 16px; text-align: center; }
        .actions a { color: #007bff; text-decoration: none; font-weight: bold; }
        .actions a:hover { text-decoration: underline; }
        .tabs { margin-top: 24px; }
        .tab-nav { display: flex; gap: 8px; flex-wrap: wrap; }
        .tab-btn { background: #dde5f2; border: none; padding: 10px 18px; border-radius: 20px; cursor: pointer; color: #2c3e50; font-weight: 600; transition: background 0.3s, transform 0.2s; }
        .tab-btn:hover { background: #d0d9e4; transform: translateY(-1px); }
        .tab-btn.active { background: #007bff; color: #fff; box-shadow: 0 4px 10px rgba(0, 123, 255, 0.25); }
        .tab-panel { display: none; margin-top: 24px; }
        .tab-panel.active { display: block; }
        .input-card { background: #eef4fb; padding: 20px; border-radius: 10px; border: 1px solid #dce4f0; }
        .chart-group, .diet-group { background: #f8f9fa; border-radius: 8px; padding: 18px; margin-bottom: 18px; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.04); }
        .chart-group h3, .diet-group h3 { margin-top: 0; }
        ul { padding-left: 18px; }
        .chart-wrapper { background: #fff; border-radius: 8px; padding: 18px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
        .progress-note { color: #555; margin-bottom: 8px; font-weight: bold; }
        .progress-summary { color: #dc3545; font-weight: bold; margin-top: 12px; }
        .empty-progress { color: #777; font-style: italic; }
        .section-title { font-size: 1.4em; color: #343a40; margin-bottom: 12px; }
        .summary-header { margin-bottom: 16px; text-align: center; }
        .summary-category { color: #007bff; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
        .summary-entry { margin-left: 16px; margin-bottom: 6px; }
        .summary-total { margin-top: 24px; font-weight: bold; color: #dc3545; font-size: 1.1em; }
        .summary-note { margin-top: 8px; color: #555; font-style: italic; }
        footer { margin-top: 24px; font-size: 0.9em; color: #666; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ACEestFitness and Gym</h1>
        <p class="subtitle">Log your training, follow curated workout flows, and keep nutrition aligned.</p>
        <div class="tabs">
            <div class="tab-nav">
                <button type="button" class="tab-btn active" data-target="log-tab">🏋️ Log Workouts</button>
                <button type="button" class="tab-btn" data-target="chart-tab">💡 Workout Plan</button>
                <button type="button" class="tab-btn" data-target="diet-tab">🥗 Diet Guide</button>
                <button type="button" class="tab-btn" data-target="progress-tab">📈 Progress Tracker</button>
            </div>
            <div id="log-tab" class="tab-panel active">
                <div class="input-card">
                    <h2 class="section-title">ACEest Fitness &amp; Gym Tracker</h2>
                    <form method="POST" action="{{ url_for('add_workout') }}">
                        <label for="category">Select Category</label>
                        <select id="category" name="category" required>
                            {% for category in categories %}
                                <option value="{{ category }}" {% if category == default_category %}selected{% endif %}>{{ category }}</option>
                            {% endfor %}
                        </select>

                        <label for="workout">Exercise</label>
                        <input type="text" id="workout" name="workout" placeholder="e.g. Interval Sprints" required>

                        <label for="duration">Duration (minutes)</label>
                        <input type="number" id="duration" name="duration" min="1" placeholder="e.g. 30" required>

                        <label for="calories">Calories Burned</label>
                        <input type="number" id="calories" name="calories" min="0" placeholder="e.g. 250" required>

                        <button type="submit">✅ Add Session</button>
                    </form>
                </div>

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
                <h2 class="section-title">💡 Personalized Workout Plan</h2>
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
                <h2 class="section-title">🥗 Best Diet Guide for Fitness Goals</h2>
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
            <div id="progress-tab" class="tab-panel">
                <h2 class="section-title">📈 Personal Progress Tracker (Minutes Logged)</h2>
                <p class="progress-note">Track how your sessions build momentum.</p>
                <p id="progress-empty" class="empty-progress" {% if total_minutes %}style="display:none"{% endif %}>Log workouts to unlock your progress insights.</p>
                <div class="chart-wrapper">
                    <canvas id="durationBarChart" width="400" height="240"></canvas>
                </div>
                <div class="chart-wrapper">
                    <canvas id="distributionPieChart" width="400" height="240"></canvas>
                </div>
                <p class="progress-summary" id="progress-summary" {% if not total_minutes %}style="display:none"{% endif %}>Total Training Time Logged: {{ total_minutes }} minutes</p>
            </div>
        </div>
        <footer>
            Version: {{ version }}
        </footer>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
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

        var totals = {{ progress_totals | tojson }};
        var labels = Object.keys(totals);
        var values = labels.map(function (key) { return totals[key]; });
        var totalMinutes = values.reduce(function (acc, value) { return acc + value; }, 0);

        var emptyMessage = document.getElementById('progress-empty');
        var barCanvas = document.getElementById('durationBarChart');
        var pieCanvas = document.getElementById('distributionPieChart');
        var barWrapper = barCanvas ? barCanvas.parentElement : null;
        var pieWrapper = pieCanvas ? pieCanvas.parentElement : null;
        var summaryText = document.getElementById('progress-summary');

        if (totalMinutes > 0 && window.Chart && barCanvas && pieCanvas) {
            if (emptyMessage) {
                emptyMessage.style.display = 'none';
            }
            if (barWrapper) {
                barWrapper.style.display = 'block';
            }
            if (pieWrapper) {
                pieWrapper.style.display = 'block';
            }
            if (summaryText) {
                summaryText.style.display = 'block';
                summaryText.textContent = 'Total Training Time Logged: ' + totalMinutes + ' minutes';
            }

            var palette = ['#007bff', '#28a745', '#ffc107'];

            var barContext = barCanvas.getContext('2d');
            new Chart(barContext, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Minutes Logged',
                        data: values,
                        backgroundColor: palette,
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Minutes'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });

            var pieContext = pieCanvas.getContext('2d');
            new Chart(pieContext, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: palette,
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        } else {
            if (barCanvas) {
                barCanvas.style.display = 'none';
            }
            if (pieCanvas) {
                pieCanvas.style.display = 'none';
            }
            if (barWrapper) {
                barWrapper.style.display = 'none';
            }
            if (pieWrapper) {
                pieWrapper.style.display = 'none';
            }
            if (summaryText) {
                summaryText.style.display = 'none';
            }
        }
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
        body { font-family: Arial, sans-serif; background: #eef1f4; margin: 0; padding: 0; }
        .container { max-width: 700px; margin: 40px auto; background: #fff; padding: 32px; border-radius: 10px; box-shadow: 0 8px 22px rgba(44, 62, 80, 0.15); }
        .summary-header { text-align: center; margin-bottom: 24px; }
        .summary-header h1 { color: #2c3e50; margin-bottom: 8px; }
        .summary-header p { color: #6c757d; margin: 0; }
        .summary-category { color: #007bff; margin-top: 18px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.6px; font-weight: bold; }
        .session { margin-bottom: 10px; padding-left: 18px; }
        .session span { color: #6c757d; font-size: 0.9em; }
        .empty { color: #777; font-style: italic; padding-left: 18px; }
        .total { margin-top: 28px; font-weight: bold; color: #dc3545; font-size: 1.1em; }
        .note { margin-top: 12px; font-style: italic; color: #555; }
        a { display: inline-block; margin-top: 30px; color: #007bff; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="summary-header">
            <h1>📊 Weekly Session Summary</h1>
            <p>Review your logged workouts by category.</p>
        </div>
        {% for category, sessions in workouts.items() %}
            <div class="summary-category">{{ category }}</div>
            {% if sessions %}
                {% for entry in sessions %}
                    <div class="session">{{ loop.index }}. {{ entry.workout }} - {{ entry.duration }} min ({{ entry.calories }} cal)
                        <span>• Logged: {{ entry.timestamp.split(' ')[0] }}</span>
                    </div>
                {% endfor %}
            {% else %}
                <div class="empty">No sessions recorded.</div>
            {% endif %}
        {% endfor %}
        <div class="total">Total Time Spent: {{ total_time }} minutes</div>
        <div class="note">{{ motivation }}</div>
        <a href="{{ url_for('index') }}">⬅️ Back to Tracker</a>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    version = os.environ.get('APP_VERSION', 'unknown')
    total_sessions = sum(len(sessions) for sessions in workouts.values())
    progress_totals = {category: sum(entry['duration'] for entry in sessions) for category, sessions in workouts.items()}
    total_minutes = sum(progress_totals.values())
    return render_template_string(
        HTML_TEMPLATE,
        workouts=workouts,
        categories=CATEGORIES,
        default_category="Workout",
        total_sessions=total_sessions,
        version=version,
        workout_chart=WORKOUT_CHART_DATA,
        diet_plans=DIET_PLANS,
        progress_totals=progress_totals,
        total_minutes=total_minutes,
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
    flash(f"✅ Added {entry['workout']} ({duration} min) to {category}.", "info")
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