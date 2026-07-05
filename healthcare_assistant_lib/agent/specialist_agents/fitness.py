"""Fitness specialist — exercises via free-exercise-db."""

from healthcare_assistant_lib.agent.specialist_agents.base import Specialist
from healthcare_assistant_lib.tools.exercises import search_exercises

SPECIALIST = Specialist(
    name="fitness",
    node="fitness_agent",
    description="Questions about exercise, physical activity, workouts, or training.",
    prompt=(
        "You are the fitness specialist. Use search_exercises to find exercises "
        "with their target muscles, equipment, difficulty and instructions. "
        "Give general, sensible activity guidance and remind users to progress "
        "gradually and consider their own limits."
    ),
    tools=(search_exercises,),
)
