"""Tests for the knowledge-base tool and the fallback routing (mocked store)."""

from langchain_core.messages import AIMessage

from healthcare_assistant_lib import send_message
from healthcare_assistant_lib.agent import fallback
from healthcare_assistant_lib.rag import store
from healthcare_assistant_lib.tools.knowledge_base import search_knowledge_base
from tests.conftest import FakeLLM


class TestKnowledgeBaseTool:
    """Tests for knowledge base tool."""

    def test_ok(self, monkeypatch):
        """Test ok."""
        monkeypatch.setattr(
            store,
            "search",
            lambda q, k=4: [{"text": "chunk", "source": "a.md", "similarity": 0.93}],
        )
        result = search_knowledge_base.invoke({"query": "x"})
        assert result["status"] == "ok"
        assert result["chunks"][0]["source"] == "a.md"

    def test_not_found_when_nothing_clears_threshold(self, monkeypatch):
        """Test not found when nothing clears threshold."""
        monkeypatch.setattr(store, "search", lambda q, k=4: [])
        result = search_knowledge_base.invoke({"query": "x"})
        assert result["status"] == "not_found"

    def test_unavailable_on_store_error(self, monkeypatch):
        """Test unavailable on store error."""

        def boom(q, k=4):
            """Test helper: boom."""
            raise RuntimeError("chromadb missing")

        monkeypatch.setattr(store, "search", boom)
        result = search_knowledge_base.invoke({"query": "x"})
        assert result["status"] == "unavailable"


class TestFallbackRouting:
    """Tests for fallback routing."""

    def test_falls_back_to_kb_when_specialist_cannot_answer(self, patch_agent_llm, monkeypatch):
        """Test falls back to kb when specialist cannot answer."""
        monkeypatch.setattr(fallback.store, "count", lambda: 5)
        patch_agent_llm(
            FakeLLM(
                route="conditions",
                script=[
                    AIMessage(content="I'm sorry, I couldn't find reliable information on that."),
                    AIMessage(content="According to your uploaded documents, the answer is 42."),
                ],
            )
        )
        result = send_message("kb-fallback", "what is our internal onboarding policy?")
        assert result["specialty"] == "knowledge_base"
        assert "42" in result["reply"]

    def test_no_fallback_when_kb_empty(self, patch_agent_llm, monkeypatch):
        """Test no fallback when kb empty."""
        monkeypatch.setattr(fallback.store, "count", lambda: 0)
        patch_agent_llm(
            FakeLLM(route="conditions", script=[AIMessage(content="I couldn't find that.")])
        )
        result = send_message("kb-empty", "obscure question")
        assert result["specialty"] == "conditions"
        assert "couldn't find" in result["reply"].lower()

    def test_no_fallback_when_answer_is_adequate(self, patch_agent_llm, monkeypatch):
        """Test no fallback when answer is adequate."""
        monkeypatch.setattr(fallback.store, "count", lambda: 5)
        patch_agent_llm(
            FakeLLM(route="fitness", script=[AIMessage(content="Here is a good squat routine.")])
        )
        result = send_message("kb-adequate", "leg exercise please")
        assert result["specialty"] == "fitness"
        assert "squat" in result["reply"].lower()
