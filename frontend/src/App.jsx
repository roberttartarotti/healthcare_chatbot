import { useEffect, useRef, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "/api/v1";

function getUserId() {
  let id = localStorage.getItem("hc_user_id");
  if (!id) {
    id = (crypto.randomUUID && crypto.randomUUID()) || `u-${Date.now()}`;
    localStorage.setItem("hc_user_id", id);
  }
  return id;
}

const SPECIALTY_LABELS = {
  medication: "💊 Medication",
  conditions: "🩺 Conditions",
  nutrition: "🥗 Nutrition",
  fitness: "🏃 Fitness",
  general: "🧭 General",
};

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const userId = useRef(getUserId());
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages, loading]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId.current, message: text }),
      });
      if (!res.ok) throw new Error(`Server error (${res.status})`);
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { role: "assistant", text: data.reply, specialty: data.specialty, blocked: data.blocked },
      ]);
    } catch (e) {
      setError(e.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  function resetConversation() {
    localStorage.removeItem("hc_user_id");
    userId.current = getUserId();
    setMessages([]);
    setError("");
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Healthcare Assistant</h1>
        <span className="tag">hobby project · not medical advice</span>
        <button className="reset" onClick={resetConversation}>
          New conversation
        </button>
      </header>

      <div className="banner">
        ⚠️ Homemade LangGraph demo with <strong>no medical value</strong>. Not a
        substitute for a doctor. In an emergency, call your local emergency number.
      </div>

      <main className="chat" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="empty">
            Ask about a medication, a condition or symptom, nutrition, or exercise.
            <div className="examples">
              <span>“What are the side effects of ibuprofen?”</span>
              <span>“What should I know about asthma?”</span>
              <span>“Is Nutella healthy?”</span>
              <span>“A beginner leg exercise?”</span>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.role === "assistant" && (
              <div className="meta">
                {SPECIALTY_LABELS[m.specialty] || "🤖 Assistant"}
                {m.blocked && <span className="blocked">guardrail</span>}
              </div>
            )}
            <div className="bubble">{m.text}</div>
          </div>
        ))}

        {loading && <div className="msg assistant"><div className="bubble typing">…thinking</div></div>}
        {error && <div className="error">{error}</div>}
      </main>

      <footer className="composer">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Type a health question…  (Enter to send, Shift+Enter for a new line)"
          rows={2}
        />
        <button onClick={send} disabled={loading || !input.trim()}>
          Send
        </button>
      </footer>
    </div>
  );
}
