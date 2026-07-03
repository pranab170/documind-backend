import { useState, useRef, useEffect } from "react";

const API_URL = "https://pranabpaul102-documind-api.hf.space";

const QUICK_QUESTIONS = [
  "Attendance requirement for exams?",
  "EOD fee kitna hai?",
  "Pass grade for theory?",
  "Malpractice consequences?"
];

// Modern Icons
function BotIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
      <circle cx="9" cy="14" r="1" fill="currentColor" stroke="none"/>
      <circle cx="15" cy="14" r="1" fill="currentColor" stroke="none"/>
    </svg>
  );
}

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13"/>
      <polygon points="22 2 15 22 11 13 2 9 22 2"/>
    </svg>
  );
}

function TypingDots() {
  return (
    <div style={{ display: "flex", gap: 5, alignItems: "center", padding: "4px 2px" }}>
      {[0, 1, 2].map((i) => (
        <div key={i} style={{
          width: 8, height: 8, borderRadius: "50%",
          background: "linear-gradient(135deg, #60a5fa, #a78bfa)",
          animation: "bounce 1.4s infinite ease-in-out",
          animationDelay: `${i * 0.16}s`
        }} />
      ))}
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className="message-animate" style={{
      display: "flex", gap: 12, alignItems: "flex-end",
      flexDirection: isUser ? "row-reverse" : "row",
      marginBottom: 20,
    }}>
      <div style={{
        width: 36, height: 36, borderRadius: "12px", flexShrink: 0,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: isUser ? "#334155" : "linear-gradient(135deg, #2563eb, #6366f1)",
        color: "#f8fafc",
        boxShadow: "0 4px 10px rgba(0,0,0,0.3)",
        fontSize: 14, fontWeight: 600,
      }}>
        {isUser ? "U" : <BotIcon />}
      </div>

      <div style={{ maxWidth: "78%", display: "flex", flexDirection: "column", gap: 6, alignItems: isUser ? "flex-end" : "flex-start" }}>
        <div style={{
          padding: "12px 18px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          background: isUser ? "#334155" : "#1e293b",
          color: "#f8fafc",
          boxShadow: isUser ? "0 4px 15px rgba(0, 0, 0, 0.2)" : "0 4px 15px rgba(0,0,0,0.3)",
          border: isUser ? "none" : "1px solid #334155",
          fontSize: 14.5, lineHeight: 1.6,
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
        }}>
          {msg.typing ? <TypingDots /> : msg.content}
        </div>

        {msg.sources && msg.sources.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, justifyContent: isUser ? "flex-end" : "flex-start" }}>
            {msg.sources.map((s, i) => (
              <span key={i} className="source-pill">
                📄 {s}
              </span>
            ))}
          </div>
        )}

        {msg.latency && (
          <span style={{ fontSize: 11, color: "#94a3b8", fontWeight: 500 }}>
            ⚡ {(msg.latency / 1000).toFixed(2)}s · {msg.model}
          </span>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 0, role: "assistant",
      content: "Hi! I'm DocuMind — an AI assistant powered by CUTM's official academic regulations.\n\nAsk me anything about attendance rules, grading, backlogs, EOD, or malpractice.",
      sources: ["BTech_Academic_Regulations_CBCS_2017", "CUTM_Examination_Handbook_2026"],
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then(r => r.json())
      .then(d => setHealth(d))
      .catch(() => setHealth(null));
  }, []);

  const sendMessage = async (q) => {
    const query = q || input.trim();
    if (!query || loading) return;
    
    setInput("");
    const userMsg = { id: Date.now(), role: "user", content: query };
    const typingMsg = { id: Date.now() + 1, role: "assistant", typing: true, content: "" };
    setMessages(prev => [...prev, userMsg, typingMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 5 }),
      });
      const data = await res.json();
      
      setMessages(prev => [
        ...prev.filter(m => !m.typing),
        {
          id: Date.now() + 2,
          role: "assistant",
          content: data.answer || data.detail || "Something went wrong.",
          sources: data.sources || [],
          latency: data.latency_ms,
          model: data.model,
        }
      ]);
    } catch (e) {
      setMessages(prev => [
        ...prev.filter(m => !m.typing),
        {
          id: Date.now() + 2,
          role: "assistant",
          content: "Could not connect to DocuMind API. Ensure FastAPI is running on port 8000.",
          sources: [],
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ height: "100vh", background: "#0f172a", display: "flex", flexDirection: "column", fontFamily: "'Inter', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Kalam:wght@400;700&display=swap');
        
        @keyframes bounce { 
          0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 
          40% { transform: scale(1); opacity: 1; } 
        }
        
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .message-animate {
          animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .source-pill {
          font-size: 11px; padding: 4px 10px; border-radius: 12px;
          background: #334155; border: 1px solid #475569;
          color: #cbd5e1; display: flex; align-items: center; gap: 4px;
          transition: all 0.2s; font-weight: 500;
        }

        /* --- STICKY NOTE CSS (Dark Tech Theme) --- */
        .sticky-note {
          font-family: 'Kalam', cursive;
          font-size: 14px;
          padding: 12px 16px;
          width: 140px;
          background: #1e293b;
          color: #e2e8f0;
          border-radius: 2px 15px 2px 15px;
          border: 1px solid #334155;
          box-shadow: 2px 4px 6px rgba(0,0,0,0.3);
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
          position: relative;
          text-align: center;
          line-height: 1.3;
        }
        .sticky-note:hover {
          transform: translateY(-5px) scale(1.05) rotate(0deg) !important;
          box-shadow: 4px 8px 12px rgba(0,0,0,0.5);
          border-color: #60a5fa;
          z-index: 10;
        }
        .sticky-note::before {
          content: '';
          position: absolute;
          top: -10px; left: 50%;
          transform: translateX(-50%);
          width: 30px; height: 12px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 50%;
          box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }
        
        .sticky-note:nth-child(odd) { transform: rotate(-3deg); }
        .sticky-note:nth-child(even) { transform: rotate(2deg); }
        .sticky-note:nth-child(3n) { transform: rotate(-1deg); }

        * { box-sizing: border-box; }
        body { margin: 0; }
        textarea:focus { outline: none; border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 10px; }
      `}</style>

      {/* Header */}
      <div style={{
        background: "rgba(15, 23, 42, 0.9)", backdropFilter: "blur(12px)",
        borderBottom: "1px solid rgba(51, 65, 85, 0.8)",
        padding: "16px 32px", display: "flex", alignItems: "center",
        justifyContent: "space-between", position: "sticky", top: 0, zIndex: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 40, height: 40, borderRadius: "12px",
            background: "linear-gradient(135deg, #2563eb, #6366f1)", 
            display: "flex", alignItems: "center", justifyContent: "center", 
            color: "#fff", boxShadow: "0 4px 12px rgba(37, 99, 235, 0.3)"
          }}>
            <BotIcon />
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 18, color: "#f8fafc", letterSpacing: "-0.5px" }}>DocuMind</div>
            <div style={{ fontSize: 12, color: "#94a3b8", fontWeight: 500 }}>Interactive Portfolio Edition</div>
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, maxWidth: 900, width: "100%", margin: "0 auto", padding: "30px 20px 0", display: "flex", flexDirection: "column", overflowY: "auto" }}>
        <div style={{ flex: 1, paddingBottom: 20 }}>
          {messages.map(msg => <Message key={msg.id} msg={msg} />)}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input area & Sticky Notes */}
      <div style={{
        background: "linear-gradient(to top, #0f172a 85%, rgba(15,23,42,0))",
        padding: "10px 20px 24px",
      }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          
          {/* STICKY NOTES CONTAINER */}
          <div style={{ display: "flex", gap: 15, flexWrap: "wrap", marginBottom: 25, justifyContent: "center", padding: "10px" }}>
            {QUICK_QUESTIONS.map(q => (
              <div key={q} className="sticky-note" onClick={() => sendMessage(q)}>
                {q}
              </div>
            ))}
          </div>

          {/* Text input */}
          <div style={{ 
            display: "flex", gap: 12, alignItems: "flex-end",
            background: "#1e293b", padding: "8px", borderRadius: "20px",
            boxShadow: "0 8px 30px rgba(0,0,0,0.3)", border: "1px solid #334155"
          }}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Type your question here..."
              rows={1}
              style={{
                flex: 1, border: "none", padding: "12px 16px", 
                fontSize: 15, fontFamily: "inherit", background: "transparent", 
                color: "#f8fafc", resize: "none", lineHeight: 1.5, 
                maxHeight: 120, overflowY: "auto",
              }}
            />
            <button onClick={() => sendMessage()} disabled={loading || !input.trim()}
              style={{
                width: 44, height: 44, borderRadius: "14px", border: "none",
                background: loading || !input.trim() ? "#334155" : "linear-gradient(135deg, #2563eb, #6366f1)",
                color: loading || !input.trim() ? "#64748b" : "#fff", 
                cursor: loading || !input.trim() ? "not-allowed" : "pointer",
                display: "flex", alignItems: "center", justifyContent: "center",
                transition: "all 0.2s", flexShrink: 0,
                boxShadow: loading || !input.trim() ? "none" : "0 4px 12px rgba(37, 99, 235, 0.4)",
              }}>
              <SendIcon />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}