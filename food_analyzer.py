import requests
import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
from deep_translator import GoogleTranslator
from config import USDA_API_KEY

# =========================================================
# PART 1: Load BLIP-2
# =========================================================

print("Loading BLIP-2...")
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    torch_dtype=torch.float16
)
model.to("cuda")
print("BLIP-2 loaded.\n")

# =========================================================
# PART 2: Identify food from photo using BLIP-2
# =========================================================

def identify_food(image_path):
    image = Image.open(image_path).convert("RGB")
    prompt = "Question: what specific food or dish is in this photo? name only the main food item. Answer:"

    inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda", torch.float16)
    generated_ids = model.generate(**inputs, max_new_tokens=20)
    full_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    food_name = full_text.split("Answer:")[-1].strip()
    return food_name

# =========================================================
# PART 3: Clean the food name before searching
# =========================================================

def clean_food_query(food_description):
    filler_words = [
        "a", "an", "the", "fresh", "delicious", "beautiful",
        "colorful", "rainbow", "plate of", "bowl of", "some",
        "homemade", "tasty", "healthy", "grilled", "fried",
        "baked", "steamed", "cooked"
    ]
    words = food_description.lower().split()
    cleaned = [w for w in words if w not in filler_words]
    return " ".join(cleaned)

# =========================================================
# PART 4: Get nutrition data from USDA API
# =========================================================

def get_nutrition(food_name):
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": food_name,
        "api_key": USDA_API_KEY,
        "pageSize": 1
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    if not data.get("foods"):
        return None

    food = data["foods"][0]
    nutrients = food.get("foodNutrients", [])

    nutrition_info = {"name": food["description"]}

    nutrient_map = {
    "Energy": "calories",
    "Protein": "protein_g",
    "Carbohydrate, by difference": "carbs_g",
    "Total lipid (fat)": "fat_g",
    "Fiber, total dietary": "fiber_g",
    "Sugars, total including NLEA": "sugar_g",
    "Sodium, Na": "sodium_mg",    # ← add this
}

    for nutrient in nutrients:
        nutrient_name = nutrient.get("nutrientName", "")
        if nutrient_name in nutrient_map:
            key = nutrient_map[nutrient_name]
            nutrition_info[key] = round(nutrient.get("value", 0), 1)

    return nutrition_info

# =========================================================
# PART 5: Generate health assessment
# =========================================================

def generate_health_report(food_name, nutrition):
    calories = nutrition.get("calories", 0)
    protein = nutrition.get("protein_g", 0)
    carbs = nutrition.get("carbs_g", 0)
    fat = nutrition.get("fat_g", 0)
    fiber = nutrition.get("fiber_g", 0)
    sugar = nutrition.get("sugar_g", 0)
    sodium = nutrition.get("sodium_mg", 0)

    if sodium > 600:
        sodium_note = "high in sodium — may not be suitable for people with high blood pressure"
    elif sodium > 300:
        sodium_note = "moderate sodium content — consume as part of a balanced diet"
    else:
        sodium_note = "low in sodium, good for heart health"

    if calories < 200:
        calorie_note = "low in calories, suitable for weight management"
    elif calories < 500:
        calorie_note = "moderate in calories, good for a balanced meal"
    else:
        calorie_note = "high in calories, best consumed in moderation"

    if protein > 20:
        protein_note = "an excellent protein source, great for muscle recovery"
    elif protein > 10:
     protein_note = "a good protein content"
    else:
        protein_note = "a low protein content — consider pairing with a protein source"

    if fiber > 5:
        fiber_note = "high in fiber, great for digestion and gut health"
    elif fiber > 2:
        fiber_note = "moderate fiber content"
    else:
        fiber_note = "low in fiber — consider pairing with vegetables"

    if sugar > 20:
        sugar_note = "high in sugar — consume with caution"
    elif sugar > 10:
        sugar_note = "moderate sugar content"
    else:
        sugar_note = "low in sugar, good for blood sugar control"

    if fat > 20:
        fat_note = "high in fat — watch portion size"
    elif fat > 10:
        fat_note = "moderate fat content"
    else:
        fat_note = "low in fat"

    report = (
        f"Food identified: {food_name}\n"
        f"Matched in USDA database as: {nutrition['name']}\n\n"
        f"Nutritional content (per 100g):\n"
        f"  Calories : {calories} kcal\n"
        f"  Protein  : {protein}g\n"
        f"  Carbs    : {carbs}g\n"
        f"  Fat      : {fat}g\n"
        f"  Fiber    : {fiber}g\n"
        f"  Sugar    : {sugar}g\n"
        f"  Sodium   : {sodium}mg\n\n"
        f"Health assessment:\n"
        f"  - This food is {calorie_note}.\n"
        f"  - It has {protein_note}.\n"
        f"  - It is {fiber_note}.\n"
        f"  - It is {sugar_note}.\n"
        f"  - It is {fat_note}.\n"
        f"  - It is {sodium_note}.\n"
    )
    return report

# =========================================================
# PART 6: Translate to French and Arabic
# =========================================================

def translate_report(report, language):
    translator = GoogleTranslator(source="english", target=language)
    lines = report.split("\n")
    translated_lines = []
    for line in lines:
        if line.strip():
            translated_lines.append(translator.translate(line))
        else:
            translated_lines.append("")
    return "\n".join(translated_lines)

# =========================================================
# PART 7: Full pipeline
# =========================================================

def analyze_food(image_path):
    print(f"Analyzing: {image_path}\n")

    # Step 1: identify food from photo
    food_name = identify_food(image_path)
    print(f"BLIP-2 identified: {food_name}")

    # Step 2: clean the query before searching
    clean_query = clean_food_query(food_name)
    print(f"Searching USDA for: {clean_query}")

    # Step 3: get real nutrition data
    nutrition = get_nutrition(clean_query)
    if not nutrition:
        print(f"Could not find '{clean_query}' in USDA database. Try a clearer photo.")
        return

    # Step 4: generate English report
    report_en = generate_health_report(food_name, nutrition)

    # Step 5: translate
    print("Translating to French and Arabic...")
    report_fr = translate_report(report_en, "fr")
    report_ar = translate_report(report_en, "ar")

    # Step 6: print all three
    print("\n" + "="*50)
    print("ENGLISH")
    print("="*50)
    print(report_en)

    print("="*50)
    print("FRENCH")
    print("="*50)
    print(report_fr)

    print("="*50)
    print("ARABIC")
    print("="*50)
    print(report_ar)

    # Step 7: save to file
    with open("nutrition_report.txt", "w", encoding="utf-8") as f:
        f.write("ENGLISH\n" + "="*50 + "\n" + report_en + "\n\n")
        f.write("FRENCH\n" + "="*50 + "\n" + report_fr + "\n\n")
        f.write("ARABIC\n" + "="*50 + "\n" + report_ar + "\n")

    print("\nReport saved to nutrition_report.txt")

# =========================================================
# PART 8: Test it
# =========================================================

analyze_food("test_food.jpg")