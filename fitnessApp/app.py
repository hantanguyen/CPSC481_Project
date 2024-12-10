from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

with open('/workspaces/codespaces-blank/fitnessApp/processed_data/processed_dataset.pkl', 'rb') as f:
    df = pickle.load(f)

with open('/workspaces/codespaces-blank/fitnessApp/models/rf_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)

with open('/workspaces/codespaces-blank/fitnessApp/models/level_encoder.pkl', 'rb') as f:
    level_encoder = pickle.load(f)

with open('/workspaces/codespaces-blank/fitnessApp/models/bodypart_encoder.pkl', 'rb') as f:
    bodypart_encoder = pickle.load(f)

def recommend_exercises(user_fitness_level, num_days, num_recommendations=5):
    user_fitness_level_code = level_encoder.transform([user_fitness_level.lower()])[0]
    filtered_df = df[df['Level_Code'] == user_fitness_level_code]

    if num_days == 3:
        day_to_body_parts = {
            1: ['chest'],
            2: ['rest'],
            3: ['biceps', 'shoulders'],
            4: ['rest'],
            5: ['quadriceps', 'abdominals'],
            6: ['rest'],
            7: ['rest']
        }
    elif num_days == 5:
        day_to_body_parts = {
            1: ['chest'],
            2: ['biceps', 'shoulders'],
            3: ['quadriceps', 'abdominals'],
            4: ['rest'],
            5: ['chest'],
            6: ['biceps', 'shoulders'],
            7: ['rest']
        }
    elif num_days == 6:
        day_to_body_parts = {
            1: ['chest'],
            2: ['biceps', 'shoulders'],
            3: ['quadriceps', 'abdominals'],
            4: ['rest'],
            5: ['chest'],
            6: ['biceps', 'shoulders'],
            7: ['quadriceps', 'abdominals']
        }

    workout_plan = {}

    for day in range(1, 8):
        workout_day_body_parts = day_to_body_parts.get(day)
        
        if workout_day_body_parts:
            if 'rest' in workout_day_body_parts:
                workout_plan[day] = {"type": "rest", "message": f"Day {day}: Rest Day"}
            else:
                day_plan = filtered_df[filtered_df['BodyPart'].isin(workout_day_body_parts)]
                if day_plan.empty:
                    workout_plan[day] = {"type": "rest", "message": f"Day {day}: No exercises available, rest day."}
                    continue
                day_plan = day_plan.sample(n=min(num_recommendations, len(day_plan)))
                workout_plan[day] = {
                    "type": "workout",
                    "message": f"Day {day}: Workout Plan",
                    "exercises": day_plan[['Title', 'BodyPart', 'Equipment', 'Rating']].to_dict(orient='records')
                }
        else:
            workout_plan[day] = {"type": "rest", "message": f"Day {day}: Rest Day"}

    return workout_plan

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_fitness_level = request.form['fitness_level']
        num_days = int(request.form['num_days'])
        
        recommended_plan = recommend_exercises(user_fitness_level, num_days)

        completed_exercises = []
        for key in request.form:
            if key.startswith('completed_'):
                if request.form[key] == '1':  
                    completed_exercises.append(key.replace('completed_', ''))

        print(f"Completed exercises: {completed_exercises}")
        
        return render_template('workout_plan.html', workout_plan=recommended_plan)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
