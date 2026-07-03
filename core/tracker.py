import json
import os
from datetime import date

def get_today_log_path():
    today = date.today().strftime("%Y-%m-%d")
    return f"data/log_{today}.json"

def load_today_log():
    path = get_today_log_path()
    if not os.path.exists(path):
        return {
            "date": date.today().strftime("%Y-%m-%d"),
            "meals": [],
            "totals": {
                "calories": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "fiber_g": 0,
                "sugar_g": 0,
                "sodium_mg": 0
            }
        }
    with open(path, "r") as f:
        return json.load(f)

def save_today_log(log):
    os.makedirs("data", exist_ok=True)
    with open(get_today_log_path(), "w") as f:
        json.dump(log, f, indent=2)

def add_meal_to_log(food_name, nutrition):
    log = load_today_log()

    meal = {
        "food": food_name,
        "nutrition": nutrition
    }
    log["meals"].append(meal)

    # Update running totals
    nutrient_keys = ["calories", "protein_g", "carbs_g",
                     "fat_g", "fiber_g", "sugar_g", "sodium_mg"]
    for key in nutrient_keys:
        log["totals"][key] = round(
            log["totals"][key] + nutrition.get(key, 0), 1
        )

    save_today_log(log)
    return log

def get_remaining(log, targets):
    remaining = {}
    for key, target in targets.items():
        consumed = log["totals"].get(key, 0)
        remaining[key] = round(target - consumed, 1)
    return remaining

def get_gaps(remaining):
    # Identify what nutrients are most lacking (below 30% of daily target remaining)
    gaps = []
    nutrient_names = {
        "protein_g": "protein",
        "fiber_g": "fiber",
        "calories": "calories",
        "carbs_g": "carbohydrates",
        "fat_g": "healthy fats"
    }
    for key, name in nutrient_names.items():
        if key in remaining and remaining[key] > 0:
            gaps.append(name)
    return gaps