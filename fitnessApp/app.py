from flask import Flask, render_template, request
import pickle
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Load the processed dataset, model, and encoders
# Corrected file paths based on actual directory structure
with open('/workspaces/codespaces-blank/fitnessApp/processed_data/processed_dataset.pkl', 'rb') as f:
    df = pickle.load(f)

with open('/workspaces/codespaces-blank/fitnessApp/models/rf_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)

with open('/workspaces/codespaces-blank/fitnessApp/models/level_encoder.pkl', 'rb') as f:
    level_encoder = pickle.load(f)

with open('/workspaces/codespaces-blank/fitnessApp/models/bodypart_encoder.pkl', 'rb') as f:
    bodypart_encoder = pickle.load(f)


# Function to recommend exercises based on user input
def recommend_exercises(user_fitness_level, num_days, num_recommendations=5):
    user_fitness_level_code = level_encoder.transform([user_fitness_level.lower()])[0]
    filtered_df = df[df['Level_Code'] == user_fitness_level_code]

    target_body_parts = ['chest', 'biceps', 'shoulders', 'abdominals', 'quadriceps']
    relevant_exercises = filtered_df[filtered_df['BodyPart'].isin(target_body_parts)]

    max_days = 7
    if num_days > max_days:
        raise ValueError(f"Number of days cannot exceed {max_days}")

    rest_day_intervals = []
    if num_days == 3:
        rest_day_intervals = [2, 5]
    elif num_days == 4:
        rest_day_intervals = [2, 4]
    elif num_days == 5:
        rest_day_intervals = [3, 6]
    elif num_days == 6:
        rest_day_intervals = [5]

    workout_plan = {}
    workout_days = 0
    for day in range(1, 8):
        if day in rest_day_intervals:
            workout_plan[day] = f"Rest Day"
        elif workout_days < num_days:
            workout_days += 1
            if day == 2:
                day_plan = relevant_exercises[relevant_exercises['BodyPart'].isin(['quadriceps', 'abdominals'])].sample(
                    n=num_recommendations, random_state=42
                )
            else:
                day_plan = relevant_exercises[relevant_exercises['BodyPart'].isin(['chest', 'shoulders', 'biceps'])].sample(
                    n=num_recommendations, random_state=42
                )
            body_parts_predicted = rf_model.predict(day_plan[['Normalized_Rating', 'Level_Code']])
            day_plan['Predicted_BodyPart'] = bodypart_encoder.inverse_transform(body_parts_predicted)
            workout_plan[day] = day_plan[['Title', 'BodyPart', 'Equipment', 'Predicted_BodyPart', 'Rating']].to_dict(orient='records')
    return workout_plan

# Route to handle the form submission and display results
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_fitness_level = request.form['fitness_level']
        num_days = int(request.form['num_days'])
        
        # Generate the workout plan
        recommended_plan = recommend_exercises(user_fitness_level, num_days)
        return render_template('workout_plan.html', workout_plan=recommended_plan)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)