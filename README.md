# Food Nutrition Analyzer

An AI-powered system that takes a photo of any food, identifies it using 
**BLIP-2** (a vision-language model), fetches real nutritional data from the 
**USDA FoodData Central database**, and generates a health assessment report 
in **English, French, and Arabic**.

## What it does

- Takes any food photo as input
- Uses BLIP-2 to identify the food item automatically
- Fetches real, government-verified nutritional data (calories, protein, 
  carbs, fat, fiber, sugar, sodium)
- Generates a plain-English health assessment based on nutritional values
- Translates the full report into French and Arabic automatically

## Why multilingual?

Food and nutrition information should be accessible to everyone regardless 
of language. This project supports English, French, and Arabic — including 
correct right-to-left rendering for Arabic.

## Tech stack

- Python, PyTorch, Hugging Face Transformers
- BLIP-2 (Salesforce/blip2-opt-2.7b) for food identification
- USDA FoodData Central API for nutritional data
- deep-translator for multilingual report generation
- NVIDIA GPU (CUDA) for inference

## Sample output

```
Food identified: a hamburger
Matched in USDA database as: HAMBURGER

Nutritional content (per 100g):
  Calories : 256 kcal
  Protein  : 9.3g
  Carbs    : 46.5g
  Fat      : 4.7g
  Fiber    : 2.3g
  Sugar    : 0g
  Sodium   : 488mg

Health assessment:
  - This food is moderate in calories, good for a balanced meal.
  - It has a low protein content — consider pairing with a protein source.
  - It is moderate fiber content.
  - It is low in sugar, good for blood sugar control.
  - It is low in fat.
  - It is moderate sodium content — consume as part of a balanced diet.
```

## Known limitations

- Nutritional values are based on USDA average data for that food type, 
  not the specific portion in the photo
- BLIP-2 works best with clear, single-item food photos
- Cooking method details (extra oil, salt added during cooking) are not 
  visible to the image model

## Setup

1. Clone this repository
2. Copy `config.example.py` to `config.py` and add your USDA API key
3. Get a free API key at https://fdc.nal.usda.gov/api-guide.html
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python food_analyzer.py`

## Built by

Guerrane Amina — Master's student, Computer Engineering, Jeju National University