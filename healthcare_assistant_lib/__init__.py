"""Healthcare assistant library.

A LangGraph multi-agent healthcare assistant (hobby project, no medical value).
A supervisor orchestrator routes each turn to a specialist agent (medication,
conditions, nutrition, fitness, or general), which answers using open-data tools.
Input/output guardrails and a mandatory disclaimer keep it safe; see
``constants.py``.

Public surface: ``send_message(user_id, message)``.
"""

from healthcare_assistant_lib.service import send_message

__all__ = ["send_message"]
