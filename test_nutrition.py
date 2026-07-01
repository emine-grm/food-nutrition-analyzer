import requests
from config import USDA_API_KEY

def get_nutrition(food_name):
    # Step 1: search for the food
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": food_name,
        "api_key": USDA_API_KEY,
        "pageSize": 1  # just get the top result
    }
    
    response = requests.get(search_url, params=params)
    data = response.json()
    
    if not data.get("foods"):
        return None
    
    food = data["foods"][0]
    food_name_found = food["description"]
    nutrients = food.get("foodNutrients", [])
    
    # Step 2: extract the key nutrients we care about
    nutrition_info = {"name": food_name_found}
    
    nutrient_map = {
        "Energy": "calories",
        "Protein": "protein_g",
        "Carbohydrate, by difference": "carbs_g",
        "Total lipid (fat)": "fat_g",
        "Fiber, total dietary": "fiber_g",
        "Sugars, total including NLEA": "sugar_g",
    }
    
    for nutrient in nutrients:
        nutrient_name = nutrient.get("nutrientName", "")
        if nutrient_name in nutrient_map:
            key = nutrient_map[nutrient_name]
            nutrition_info[key] = round(nutrient.get("value", 0), 1)
    
    return nutrition_info

# Test it
result = get_nutrition("grilled chicken")
if result:
    print("Food found:", result["name"])
    print("Calories:", result.get("calories", "N/A"), "kcal")
    print("Protein:", result.get("protein_g", "N/A"), "g")
    print("Carbs:", result.get("carbs_g", "N/A"), "g")
    print("Fat:", result.get("fat_g", "N/A"), "g")
    print("Fiber:", result.get("fiber_g", "N/A"), "g")
else:
    print("Food not found")