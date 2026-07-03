def generate_recommendation(gaps, remaining, goal, restrictions):
    if not gaps:
        return "You've met all your nutritional targets for today. Great job!"

    # Build a recommendation based on what's missing
    gap_text = ", ".join(gaps[:3])  # top 3 gaps

    if goal == "lose_weight":
        base = f"You still need {gap_text} today. "
        if "calories" in gaps and remaining.get("calories", 0) < 300:
            suggestion = "You're close to your calorie limit — choose something light like a salad, soup, or fruit."
        elif "protein_g" in gaps:
            suggestion = "Focus on lean protein: grilled chicken, eggs, legumes, or tofu."
        elif "fiber_g" in gaps:
            suggestion = "Add vegetables or fruit to your next meal to boost fiber."
        else:
            suggestion = "Keep portions small and focus on whole foods."

    elif goal == "build_muscle":
        base = f"You still need {gap_text} today. "
        if "protein_g" in gaps:
            suggestion = "Prioritize protein: chicken breast, fish, eggs, Greek yogurt, or protein-rich legumes."
        elif "calories" in gaps and remaining.get("calories", 0) > 500:
            suggestion = "You still have significant calorie room — add a balanced meal with carbs and protein."
        else:
            suggestion = "Focus on complex carbs and protein for your next meal."

    else:  # maintain
        base = f"You still need {gap_text} today. "
        if "fiber_g" in gaps:
            suggestion = "Add more vegetables, whole grains, or legumes."
        elif "protein_g" in gaps:
            suggestion = "Include a protein source in your next meal."
        else:
            suggestion = "Aim for a balanced meal with a mix of protein, carbs, and vegetables."

    # Add restriction awareness
    restriction_note = ""
    if "halal" in restrictions:
        restriction_note = " Remember to choose halal-certified options."
    elif "vegetarian" in restrictions:
        restriction_note = " Stick to plant-based or vegetarian protein sources."
    elif "vegan" in restrictions:
        restriction_note = " Choose plant-based options only."

    return base + suggestion + restriction_note

def check_restrictions(food_name, nutrition_name, restrictions):
    warnings = []

    pork_keywords = ["pork", "bacon", "ham", "lard", "prosciutto",
                     "salami", "sausage", "pepperoni"]
    alcohol_keywords = ["wine", "beer", "alcohol", "liquor", "spirits"]
    meat_keywords = ["chicken", "beef", "pork", "lamb", "fish",
                     "seafood", "meat", "turkey"]
    dairy_keywords = ["milk", "cheese", "butter", "cream", "yogurt", "dairy"]
    gluten_keywords = ["wheat", "bread", "pasta", "flour", "gluten",
                       "barley", "rye"]

    food_lower = (food_name + " " + nutrition_name).lower()

    if "halal" in restrictions:
        if any(k in food_lower for k in pork_keywords):
            warnings.append("⚠ Contains pork — conflicts with halal restriction")
        if any(k in food_lower for k in alcohol_keywords):
            warnings.append("⚠ May contain alcohol — conflicts with halal restriction")

    if "vegetarian" in restrictions:
        if any(k in food_lower for k in meat_keywords):
            warnings.append("⚠ Contains meat — conflicts with vegetarian restriction")

    if "vegan" in restrictions:
        if any(k in food_lower for k in meat_keywords):
            warnings.append("⚠ Contains meat — conflicts with vegan restriction")
        if any(k in food_lower for k in dairy_keywords):
            warnings.append("⚠ Contains dairy — conflicts with vegan restriction")

    if "gluten_free" in restrictions:
        if any(k in food_lower for k in gluten_keywords):
            warnings.append("⚠ May contain gluten — conflicts with gluten-free restriction")

    if "dairy_free" in restrictions:
        if any(k in food_lower for k in dairy_keywords):
            warnings.append("⚠ Contains dairy — conflicts with dairy-free restriction")

    return warnings

def meal_verdict(food_name, nutrition, profile):
    goal = profile["goal"]
    targets = profile["daily_targets"]
    restrictions = profile["restrictions"]
    age = profile["age"]

    calories = nutrition.get("calories", 0)
    protein = nutrition.get("protein_g", 0)
    fat = nutrition.get("fat_g", 0)
    sugar = nutrition.get("sugar_g", 0)
    sodium = nutrition.get("sodium_mg", 0)
    fiber = nutrition.get("fiber_g", 0)

    score = 100  # start at 100 and deduct based on how bad it is for this person
    feedback = []
    positives = []

    # ── Goal-specific judgment ──────────────────────────────────────────

    if goal == "lose_weight":
        if calories > 500:
            score -= 25
            feedback.append(
                f"High in calories ({calories} kcal) — "
                f"this is {round(calories/targets['calories']*100)}% "
                f"of your daily target in one meal"
            )
        elif calories < 300:
            positives.append(f"Low in calories ({calories} kcal) — good for weight loss")

        if fat > 20:
            score -= 15
            feedback.append(f"High in fat ({fat}g) — limit fatty meals while losing weight")

        if sugar > 20:
            score -= 15
            feedback.append(
                f"High in sugar ({sugar}g) — "
                f"sugar spikes insulin and slows fat loss"
            )

        if protein > 15:
            positives.append(
                f"Good protein content ({protein}g) — "
                f"helps preserve muscle while losing weight"
            )

    elif goal == "build_muscle":
        if protein < 15:
            score -= 25
            feedback.append(
                f"Low in protein ({protein}g) — "
                f"aim for at least 25-30g per meal to support muscle growth"
            )
        elif protein >= 25:
            positives.append(
                f"Excellent protein ({protein}g) — "
                f"great for muscle recovery and growth"
            )

        if calories < 200:
            score -= 10
            feedback.append(
                f"Low in calories ({calories} kcal) — "
                f"you need a calorie surplus to build muscle"
            )

    elif goal == "maintain":
        if calories > 600:
            score -= 10
            feedback.append(
                f"Fairly high in calories ({calories} kcal) for one meal — "
                f"balance with lighter meals today"
            )

    # ── Age-specific judgment ───────────────────────────────────────────

    if age > 50:
        if sodium > 400:
            score -= 15
            feedback.append(
                f"High sodium ({sodium}mg) — "
                f"especially important to watch after 50 for heart and blood pressure health"
            )
        if calcium_present := nutrition.get("calcium_mg", 0):
            if calcium_present > 100:
                positives.append(
                    f"Good calcium content — "
                    f"important for bone health after 50"
                )

    if age < 18:
        if sugar > 15:
            score -= 10
            feedback.append(
                f"High in sugar ({sugar}g) — "
                f"limit sugar intake for children and teenagers"
            )
        if protein > 10:
            positives.append(
                f"Good protein ({protein}g) — "
                f"important for growth and development"
            )

    # ── General health flags (apply to everyone) ─────────────────────────

    if sodium > 800:
        score -= 20
        feedback.append(
            f"Very high sodium ({sodium}mg) — "
            f"that's {round(sodium/2300*100)}% of the daily recommended limit in one meal"
        )
    elif sodium > 500:
        score -= 10
        feedback.append(f"Moderately high sodium ({sodium}mg) — watch your intake today")

    if fiber > 5:
        positives.append(f"High in fiber ({fiber}g) — great for digestion and gut health")
    elif fiber < 1:
        feedback.append(f"Very low in fiber — pair with vegetables or whole grains")

    # ── Restriction warnings ─────────────────────────────────────────────

    warnings = check_restrictions(food_name, food_name, restrictions)
    if warnings:
        score -= 30
        feedback.extend(warnings)

    # ── Final verdict ────────────────────────────────────────────────────

    score = max(0, min(100, score))  # keep between 0-100

    if score >= 80:
        verdict = "✅ GREAT CHOICE for your profile"
    elif score >= 60:
        verdict = "⚠ ACCEPTABLE — some concerns for your profile"
    elif score >= 40:
        verdict = "⚠ NOT IDEAL for your profile"
    else:
        verdict = "❌ POOR CHOICE for your profile"

    return {
        "score": score,
        "verdict": verdict,
        "positives": positives,
        "concerns": feedback,
    }