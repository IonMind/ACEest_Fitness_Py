
# Flask web app for ACEestFitness and Gym
import os
import io
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, redirect, url_for, flash, send_file

# PDF/report utilities (parity with Tkinter v1.3 export)
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors as rl_colors

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "aceest-dev-secret")

CATEGORIES = ("Warm-up", "Workout", "Cool-down")
workouts = {category: [] for category in CATEGORIES}

# MET values and user profile (from Tkinter v1.3)
MET_VALUES = {
    "Warm-up": 3,
    "Workout": 6,
    "Cool-down": 2.5,
}

# Simple in-memory user profile and daily aggregation
user_info = {}
daily_workouts = {}  # key: ISO date string -> {category: [entries]}

WORKOUT_CHART_DATA = {
    "Warm-up (5-10 min)": [
        "5 min light cardio (Jog/Cycle) to raise heart rate.",
        "Jumping Jacks (30 reps) for dynamic mobility.",
        "Arm Circles (15 Fwd/Bwd) to prepare shoulders.",
    ],
    "Strength & Cardio (45-60 min)": [
        "Push-ups (3 sets of 10-15) – Upper body strength.",
        "Squats (3 sets of 15-20) – Lower body foundation.",
        "Plank (3 sets of 60 seconds) – Core stabilization.",
        "Lunges (3 sets of 10 per leg) – Balance and leg development.",
        "Dumbbell Rows (3 sets of 12) – Posterior chain engagement.",
    ],
    "Cool-down (5 min)": [
        "Slow Walking to reduce intensity gradually.",
        "Static Stretching (Hold 30s each) for flexibility.",
        "Deep Breathing Exercises to promote recovery.",
    ],
}

DIET_PLANS = {
    "🎯 Weight Loss Focus (Calorie Deficit)": [
        "Breakfast: Oatmeal with Berries (High Fiber).",
        "Lunch: Grilled Chicken/Tofu Salad (Lean Protein).",
        "Dinner: Vegetable Soup with Lentils (Low Calorie, High Volume).",
    ],
    "💪 Muscle Gain Focus (High Protein)": [
        "Breakfast: 3 Egg Omelet, Spinach, Whole-wheat Toast (Protein/Carb combo).",
        "Lunch: Chicken Breast, Quinoa, and Steamed Veggies (Balanced Meal).",
        "Post-Workout: Protein Shake & Greek Yogurt (Immediate Recovery).",
    ],
    "🏃 Endurance Focus (Complex Carbs)": [
        "Pre-Workout: Banana & Peanut Butter (Quick Energy).",
        "Lunch: Whole Grain Pasta with Light Sauce (Sustainable Carbs).",
        "Dinner: Salmon & Avocado Salad (Omega-3s and Healthy Fats).",
    ],
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>ACEestFitness and Gym</title>
    <style>
        :root {
            --color-primary: #4caf50;
            --color-primary-dark: #388e3c;
            --color-secondary: #2196f3;
            --color-secondary-dark: #1976d2;
            --color-background: #f8f9fa;
            --color-card: #ffffff;
            --color-text: #343a40;
        }
        body { font-family: Arial, sans-serif; background: var(--color-background); margin: 0; padding: 0; color: var(--color-text); }
        .container { max-width: 860px; margin: 40px auto; background: var(--color-card); padding: 32px; border-radius: 12px; box-shadow: 0 12px 28px rgba(44, 62, 80, 0.15); }
        h1 { color: var(--color-text); margin-bottom: 8px; font-size: 2.1em; }
        .subtitle { color: #6c757d; margin-top: 0; font-size: 1.05em; }
        form { margin-bottom: 24px; }
        label { display: block; margin-top: 12px; font-weight: bold; color: var(--color-text); }
        input[type=text], input[type=number], select { width: 100%; padding: 12px; margin-top: 6px; border: 1px solid #ced4da; border-radius: 8px; background: #f1f3f5; transition: border-color 0.2s, background 0.2s; }
        input[type=text]:focus, input[type=number]:focus, select:focus { outline: none; border-color: var(--color-secondary); background: var(--color-card); }
        button { margin-top: 20px; padding: 13px 22px; background: var(--color-primary); color: #fff; border: none; border-radius: 24px; cursor: pointer; font-weight: bold; letter-spacing: 0.6px; text-transform: uppercase; box-shadow: 0 4px 12px rgba(76, 175, 80, 0.25); }
        button:hover { background: var(--color-primary-dark); }
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
    .tab-btn { background: #e4ecf6; border: none; padding: 10px 20px; border-radius: 24px; cursor: pointer; color: var(--color-text); font-weight: 600; transition: background 0.3s, transform 0.2s; }
    .tab-btn:hover { background: #d0d9e4; transform: translateY(-1px); }
    .tab-btn.active { background: var(--color-secondary); color: #fff; box-shadow: 0 6px 14px rgba(33, 150, 243, 0.25); }
        .tab-panel { display: none; margin-top: 24px; }
        .tab-panel.active { display: block; }
    .input-card { background: #eef4fb; padding: 26px; border-radius: 12px; border: 1px solid #dce4f0; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.02); }
        .chart-group, .diet-group { background: #f8f9fa; border-radius: 8px; padding: 18px; margin-bottom: 18px; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.04); }
        .chart-group h3, .diet-group h3 { margin-top: 0; }
        ul { padding-left: 18px; }
    .chart-wrapper { background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 16px; box-shadow: 0 8px 18px rgba(0,0,0,0.05); }
    .progress-note { color: #6c757d; margin-bottom: 8px; font-weight: bold; }
    .progress-summary { color: #dc3545; font-weight: bold; margin-top: 16px; }
    .empty-progress { color: #777; font-style: italic; }
    .section-title { font-size: 1.4em; color: #343a40; margin-bottom: 12px; }
    .section-subtitle { color: #6c757d; margin-top: 0; margin-bottom: 16px; font-size: 0.95em; }
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
        <!-- User Info -->
        <div class="input-card" style="margin-bottom: 18px;">
            <h2 class="section-title">📝 User Info</h2>
            <form method="POST" action="{{ url_for('save_user_info') }}">
                <label for="name">Name</label>
                <input type="text" id="name" name="name" value="{{ user_info.get('name','') }}" placeholder="Your full name" required>

                <label for="regn_id">Regn-ID</label>
                <input type="text" id="regn_id" name="regn_id" value="{{ user_info.get('regn_id','') }}" placeholder="Membership / Registration ID" required>

                <label for="age">Age</label>
                <input type="number" id="age" name="age" min="1" value="{{ user_info.get('age','') }}" required>

                <label for="gender">Gender (M/F)</label>
                <select id="gender" name="gender" required>
                    <option value="" {% if not user_info %}selected{% endif %} disabled>Select</option>
                    <option value="M" {% if user_info.get('gender')=='M' %}selected{% endif %}>M</option>
                    <option value="F" {% if user_info.get('gender')=='F' %}selected{% endif %}>F</option>
                </select>

                <label for="height">Height (cm)</label>
                <input type="number" step="0.1" id="height" name="height" min="50" value="{{ user_info.get('height','') }}" required>

                <label for="weight">Weight (kg)</label>
                <input type="number" step="0.1" id="weight" name="weight" min="10" value="{{ user_info.get('weight','') }}" required>

                <label for="weekly_cal_goal">Weekly Calorie Goal (kcal)</label>
                <input type="number" id="weekly_cal_goal" name="weekly_cal_goal" min="0" value="{{ user_info.get('weekly_cal_goal', 2000) }}" required>

                <button type="submit">Save Info</button>
            </form>
            {% if user_info %}
                <div style="margin-top: 10px;">
                    <div class="messages info">Saved. BMI={{ '%.1f'|format(user_info['bmi']) }}, BMR={{ '%.0f'|format(user_info['bmr']) }} kcal/day</div>
                    <div style="margin-top: 8px;">
                        <strong>Weekly Calories:</strong> {{ weekly_calories }} / {{ user_info.get('weekly_cal_goal', 2000) }} kcal
                        <div style="height: 10px; background:#e9ecef; border-radius:6px; margin-top:6px;">
                            <div style="height:10px; width: {{ weekly_progress_percent }}%; background: var(--color-secondary); border-radius:6px;"></div>
                        </div>
                    </div>
                </div>
            {% endif %}
        </div>

        <div class="tabs">
            <div class="tab-nav">
                <button type="button" class="tab-btn active" data-target="log-tab">🏋️ Log Workouts</button>
                <button type="button" class="tab-btn" data-target="chart-tab">💡 Workout Plan</button>
                <button type="button" class="tab-btn" data-target="diet-tab">🥗 Diet Guide</button>
                <button type="button" class="tab-btn" data-target="progress-tab">📈 Progress Tracker</button>
            </div>
            <div id="log-tab" class="tab-panel active">
                <div class="input-card">
                    <h2 class="section-title">ACEest Session Logger</h2>
                    <p class="section-subtitle">Track your progress with precision.</p>
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
                    <div style="margin-top:16px;">
                        <form method="POST" action="{{ url_for('add_workout_auto') }}">
                            <label for="category_auto">Quick Add (Auto Calories via MET)</label>
                            <select id="category_auto" name="category" required>
                                {% for category in categories %}
                                    <option value="{{ category }}" {% if category == default_category %}selected{% endif %}>{{ category }}</option>
                                {% endfor %}
                            </select>
                            <label for="workout_auto">Exercise</label>
                            <input type="text" id="workout_auto" name="workout" placeholder="e.g. Intervals" required>
                            <label for="duration_auto">Duration (minutes)</label>
                            <input type="number" id="duration_auto" name="duration" min="1" placeholder="e.g. 30" required>
                            <button type="submit" style="background: var(--color-secondary);">⚡ Add with Auto Calories</button>
                            <div class="summary-note">Uses your saved weight (or 70kg) and category MET to estimate calories.</div>
                        </form>
                    </div>
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
                    &nbsp;|&nbsp;
                    <a href="{{ url_for('export_weekly_pdf') }}">📄 Export Weekly PDF Report</a>
                </div>
            </div>
            <div id="chart-tab" class="tab-panel">
                <h2 class="section-title">💡 Personalized Workout Plan Guide</h2>
                <p class="section-subtitle">Structured flows to keep your sessions purposeful.</p>
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
                <h2 class="section-title">🥗 Nutritional Goal Setting Guide</h2>
                <p class="section-subtitle">Align your meals with the outcomes you’re chasing.</p>
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
                <h2 class="section-title">📈 Personal Progress Tracker</h2>
                <p class="progress-note">Visualization of your logged workout time distribution.</p>
                <p id="progress-empty" class="empty-progress" {% if total_minutes %}style="display:none"{% endif %}>No workout data logged yet. Log a session to see your progress!</p>
                <div class="chart-wrapper">
                    <canvas id="durationBarChart" width="400" height="240"></canvas>
                </div>
                <div class="chart-wrapper">
                    <canvas id="distributionPieChart" width="400" height="240"></canvas>
                </div>
                <p class="progress-summary" id="progress-summary" {% if not total_minutes %}style="display:none"{% endif %}>LIFETIME TOTAL: {{ total_minutes }} minutes logged across all categories.</p>
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
                summaryText.textContent = 'LIFETIME TOTAL: ' + totalMinutes + ' minutes logged across all categories.';
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
    # Weekly calories progress (last 7 days including today)
    weekly_calories = 0
    try:
        today = datetime.now().date()
        week_start = today - timedelta(days=6)
        for cat, sessions in workouts.items():
            for entry in sessions:
                try:
                    d = datetime.strptime(entry['timestamp'], "%Y-%m-%d %H:%M:%S").date()
                except Exception:
                    # Fallback: ignore malformed timestamps
                    continue
                if d >= week_start:
                    weekly_calories += int(entry.get('calories', 0))
    except Exception:
        weekly_calories = 0
    goal = user_info.get('weekly_cal_goal', 2000) if user_info else 2000
    weekly_progress_percent = min(100, int((weekly_calories / goal) * 100)) if goal else 0
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
        user_info=user_info,
        weekly_calories=weekly_calories,
        weekly_progress_percent=weekly_progress_percent,
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
    # Track daily workouts (parity with Tkinter)
    today_iso = datetime.now().date().isoformat()
    if today_iso not in daily_workouts:
        daily_workouts[today_iso] = {c: [] for c in CATEGORIES}
    daily_workouts[today_iso][category].append(entry)
    flash(f"✅ Added {entry['workout']} ({duration} min) to {category}.", "info")
    return redirect(url_for('index'))

@app.route('/add-auto', methods=['POST'])
def add_workout_auto():
    """Add a workout with calories auto-calculated from MET and user weight."""
    workout = request.form.get('workout')
    duration = request.form.get('duration')
    category = request.form.get('category', 'Workout')

    if not (workout and duration and category):
        flash("Please fill in all fields before submitting.", "error")
        return redirect(url_for('index'))

    if category not in CATEGORIES:
        flash("Invalid category selected.", "error")
        return redirect(url_for('index'))

    try:
        duration = int(duration)
    except ValueError:
        flash("Duration must be a numeric value.", "error")
        return redirect(url_for('index'))

    if duration <= 0:
        flash("Duration must be a positive number.", "error")
        return redirect(url_for('index'))

    # Compute calories via MET formula
    weight = (user_info or {}).get('weight', 70)
    met = MET_VALUES.get(category, 5)
    calories = int(round((met * 3.5 * float(weight) / 200.0) * duration))

    entry = {
        'workout': workout.strip(),
        'duration': duration,
        'calories': calories,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    workouts[category].append(entry)
    today_iso = datetime.now().date().isoformat()
    if today_iso not in daily_workouts:
        daily_workouts[today_iso] = {c: [] for c in CATEGORIES}
    daily_workouts[today_iso][category].append(entry)
    flash(f"✅ Added {entry['workout']} ({duration} min, ~{calories} kcal) to {category}.", "info")
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


@app.route('/user/save', methods=['POST'])
def save_user_info():
    """Save user info and compute BMI/BMR (mimics Tkinter behavior)."""
    try:
        name = (request.form.get('name') or '').strip()
        regn_id = (request.form.get('regn_id') or '').strip()
        age = int(request.form.get('age'))
        gender = (request.form.get('gender') or '').strip().upper()
        height_cm = float(request.form.get('height'))
        weight_kg = float(request.form.get('weight'))
        weekly_cal_goal = int(request.form.get('weekly_cal_goal') or 2000)
        if not name or not regn_id or gender not in {"M", "F"}:
            raise ValueError("Please provide valid name, regn-id and gender.")
        bmi = weight_kg / ((height_cm / 100.0) ** 2)
        if gender == "M":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        user_info.clear()
        user_info.update({
            "name": name,
            "regn_id": regn_id,
            "age": age,
            "gender": gender,
            "height": height_cm,
            "weight": weight_kg,
            "bmi": bmi,
            "bmr": bmr,
            "weekly_cal_goal": weekly_cal_goal,
        })
        flash(f"User info saved! BMI={bmi:.1f}, BMR={bmr:.0f} kcal/day", "info")
    except Exception as e:
        flash(f"Invalid input: {e}", "error")
    return redirect(url_for('index'))


@app.route('/export/pdf', methods=['GET'])
def export_weekly_pdf():
    """Export a simple PDF report of all logged workouts and user info."""
    if not user_info:
        flash("Please save user info first!", "error")
        return redirect(url_for('index'))

    buffer = io.BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Weekly Fitness Report - {user_info['name']}")

    # User info block
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 80, f"Regn-ID: {user_info['regn_id']} | Age: {user_info['age']} | Gender: {user_info['gender']}")
    c.drawString(50, height - 100, f"Height: {user_info['height']} cm | Weight: {user_info['weight']} kg | BMI: {user_info['bmi']:.1f} | BMR: {user_info['bmr']:.0f} kcal/day")

    # Table of workouts
    y = height - 140
    table_data = [["Category", "Exercise", "Duration(min)", "Calories(kcal)", "Date"]]
    for cat, sessions in workouts.items():
        for e in sessions:
            date_str = (e.get('timestamp') or '').split(' ')[0]
            table_data.append([cat, e.get('workout', ''), str(e.get('duration', '')), str(e.get('calories', '')), date_str])
    table = Table(table_data, colWidths=[80, 150, 100, 100, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.black),
    ]))
    table.wrapOn(c, width - 100, y)
    table.drawOn(c, 50, max(40, y - 20 - 18 * len(table_data)))

    c.showPage()
    c.save()
    buffer.seek(0)

    filename = f"{user_info['name'].replace(' ', '_')}_weekly_report.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)