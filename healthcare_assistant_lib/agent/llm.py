"""LLM factory for the agents.

Lives with the agents (not the API) so the lib has no dependency on FastAPI.
Reads the model name from the environment and lets the Anthropic SDK pick up
ANTHROPIC_API_KEY from the environment too.
"""

import os

from langchain_anthropic import ChatAnthropic


def get_llm() -> ChatAnthropic:
    """Return the chat model used by the agents.

    ANTHROPIC_API_KEY must be set in the environment.
    (Newer Claude models manage sampling internally, so we don't set temperature.)
    """
    return ChatAnthropic(
        model=os.getenv("LLM_MODEL", "claude-sonnet-5"),
    )
