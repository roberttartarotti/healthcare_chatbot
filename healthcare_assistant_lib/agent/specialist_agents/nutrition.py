"""Nutrition specialist — food & nutrition via Open Food Facts."""

from healthcare_assistant_lib.agent.specialist_agents.base import Specialist
from healthcare_assistant_lib.tools.nutrition import lookup_food_nutrition

SPECIALIST = Specialist(
    name="nutrition",
    node="nutrition_agent",
    description="Questions about food, diet, nutrition, calories, or a food product.",
    prompt=(
        "You are the nutrition specialist. Use lookup_food_nutrition to get a "
        "product's Nutri-Score, processing (NOVA) group and per-100g nutrients "
        "from Open Food Facts. Explain what the numbers mean in plain language."
    ),
    tools=(lookup_food_nutrition,),
)
