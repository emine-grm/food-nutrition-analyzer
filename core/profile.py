import json
import os

PROFILE_PATH = "data/profile.json"

def calculate_daily_calories(age, weight_kg, height_cm, gender, goal):
    # Mifflin-St Jeor equation — the most accurate formula for daily calorie needs
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Multiply by activity factor (assuming sedentary/light activity for now)
    tdee = bmr * 1.375

    # Adjust based on goal
    if goal == "lose_weight":
        return round(tdee - 500)   # 500 kcal deficit = ~0.5kg/week loss
    elif goal == "build_muscle":
        return round(tdee + 300)   # slight surplus for muscle gain
    else:
        return round(tdee)         # maintain

def calculate_daily_targets(calories, goal):
    # Calculate recommended daily nutrient targets based on calories and goal
    if goal == "build_muscle":
        protein_g = round(calories * 0.30 / 4)   # 30% of calories from protein
        carbs_g = round(calories * 0.45 / 4)     # 45% from carbs
        fat_g = round(calories * 0.25 / 9)       # 25% from fat
    elif goal == "lose_weight":
        protein_g = round(calories * 0.35 / 4)   # higher protein to preserve muscle
        carbs_g = round(calories * 0.35 / 4)     # lower carbs
        fat_g = round(calories * 0.30 / 9)
    else:
        protein_g = round(calories * 0.25 / 4)
        carbs_g = round(calories * 0.50 / 4)
        fat_g = round(calories * 0.25 / 9)

    return {
        "calories": calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "fiber_g": 30,       # standard recommendation
        "sugar_g": 50,       # WHO recommendation
        "sodium_mg": 2300    # standard recommendation
    }

def create_profile(name, age, weight_kg, height_cm, gender, goal,
                   restrictions, language):
    daily_calories = calculate_daily_calories(age, weight_kg, height_cm,
                                              gender, goal)
    daily_targets = calculate_daily_targets(daily_calories, goal)

    profile = {
        "name": name,
        "age": age,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "gender": gender,
        "goal": goal,
        "restrictions": restrictions,
        "language": language,
        "daily_targets": daily_targets
    }

    os.makedirs("data", exist_ok=True)
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)

    return profile

def load_profile():
    if not os.path.exists(PROFILE_PATH):
        return None
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

def profile_exists():
    return os.path.exists(PROFILE_PATH)