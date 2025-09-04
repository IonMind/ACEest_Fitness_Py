
# Flask web app for ACEestFitness and Gym
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
workouts = []

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
        button { margin-top: 16px; padding: 10px 20px; background: #27ae60; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #219150; }
        .workout-list { margin-top: 32px; }
        .workout-item { background: #eafaf1; padding: 10px; border-radius: 4px; margin-bottom: 8px; }
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

            <button type="submit">Add Workout</button>
        </form>

        <div class="workout-list">
            <h2>Logged Workouts</h2>
            {% if workouts %}
                {% for entry in workouts %}
                    <div class="workout-item">
                        <strong>{{ entry.workout }}</strong> - {{ entry.duration }} min, {{ entry.calories }} cal
                    </div>
                {% endfor %}
            {% else %}
                <p>No workouts logged yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, workouts=workouts)

@app.route('/add', methods=['POST'])
def add_workout():
    workout = request.form.get('workout')
    duration = request.form.get('duration')
    calories = request.form.get('calories')
    if workout and duration and calories:
        try:
            duration = int(duration)
            calories = int(calories)
            workouts.append({
                'workout': workout,
                'duration': duration,
                'calories': calories
            })
        except ValueError:
            pass  # Ignore invalid input
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)