"""Exercise tool — free-exercise-db (public domain), no API key required.

Searches an open, public-domain dataset of ~800 exercises by name and returns
each match's target muscles, equipment, difficulty and short instructions.

Source: https://github.com/yuhonas/free-exercise-db (served as static JSON over a
CDN). We fetch the dataset and filter by name locally, since it has no query API.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from healthcare_assistant_lib.tools import _client
from healthcare_assistant_lib.tools._client import ServiceUnavailable, not_found, unavailable

_URL = "https://cdn.jsdelivr.net/gh/yuhonas/free-exercise-db@main/dist/exercises.json"
_SERVICE = "exercise database"
_MAX_RESULTS = 5


class ExercisesInput(BaseModel):
    """Pydantic input schema for the exercise tool."""

    query: str = Field(description="Exercise name or keyword, e.g. 'squat' or 'bench'")


@tool(args_schema=ExercisesInput)
def search_exercises(query: str) -> dict:
    """Search a public exercise database by name and return matching exercises with
    target muscles, equipment, difficulty level and short instructions. Returns a
    not_found result if nothing matches, or an 'unavailable' result if the dataset
    cannot be fetched.
    """
    try:
        data = _client.get_json(_URL)
    except ServiceUnavailable:
        return unavailable(_SERVICE)

    if not isinstance(data, list):
        return unavailable(_SERVICE)

    term = query.strip().lower()
    matches = [item for item in data if term in (item.get("name") or "").lower()]
    if not matches:
        return not_found(f"No exercises found for '{query}'.")

    exercises = [
        {
            "name": item.get("name"),
            "level": item.get("level"),
            "equipment": item.get("equipment"),
            "primary_muscles": item.get("primaryMuscles", []),
            "category": item.get("category"),
            "instructions": (item.get("instructions") or [])[:2],
        }
        for item in matches[:_MAX_RESULTS]
    ]
    return {
        "status": "ok",
        "query": query,
        "count": len(matches),
        "exercises": exercises,
        "source": "free-exercise-db",
    }
