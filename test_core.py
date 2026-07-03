from core.profile import create_profile, load_profile
from core.tracker import add_meal_to_log, get_remaining, get_gaps, load_today_log
from core.recommender import generate_recommendation, check_restrictions

# Test 1: create a profile
print("Creating profile...")
profile = create_profile(
    name="Amina",
    age=24,
    weight_kg=58,
    height_cm=165,
    gender="female",
    goal="lose_weight",
    restrictions=["halal"],
    language="english"
)
print(f"Daily calorie target: {profile['daily_targets']['calories']} kcal")
print(f"Daily protein target: {profile['daily_targets']['protein_g']}g")

# Test 2: log a meal
print("\nLogging breakfast (grilled chicken)...")
nutrition = {
    "calories": 165,
    "protein_g": 31.0,
    "carbs_g": 0.0,
    "fat_g": 3.6,
    "fiber_g": 0.0,
    "sugar_g": 0.0,
    "sodium_mg": 74.0
}
log = add_meal_to_log("grilled chicken", nutrition)
print(f"Total calories so far: {log['totals']['calories']} kcal")

# Test 3: get remaining and recommendation
remaining = get_remaining(log, profile["daily_targets"])
gaps = get_gaps(remaining)
recommendation = generate_recommendation(
    gaps, remaining, profile["goal"], profile["restrictions"]
)
print(f"\nCalories remaining: {remaining['calories']} kcal")
print(f"Gaps identified: {gaps}")
print(f"\nRecommendation: {recommendation}")

# Test 4: restriction check
print("\nChecking restrictions on 'pork fried rice'...")
warnings = check_restrictions("pork fried rice", "PORK FRIED RICE", ["halal"])
for w in warnings:
    print(w)

# Test 5: meal verdict
from core.recommender import meal_verdict

print("\n--- MEAL VERDICT ---")
verdict = meal_verdict("grilled chicken", nutrition, profile)
print(f"Score: {verdict['score']}/100")
print(f"Verdict: {verdict['verdict']}")
if verdict['positives']:
    print("Positives:")
    for p in verdict['positives']:
        print(f"  + {p}")
if verdict['concerns']:
    print("Concerns:")
    for c in verdict['concerns']:
        print(f"  - {c}")