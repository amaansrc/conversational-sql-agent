import React, { useState, useRef, useEffect, useCallback } from "react";
import Editor from "@monaco-editor/react";
import {
  Send,
  Database,
  Terminal,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle,
  Loader,
  RefreshCw,
  Copy,
  Check,
  Zap,
  BarChart2,
  Info,
  X,
  ArrowRight,
  Sparkles,
  Brain,
  RotateCcw,
  LineChart,
} from "lucide-react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ─── API helpers ──────────────────────────────────────────────────────────────
async function postQuery(query, endpoint = "/query/explain") {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  return res.json();
}

// ─── Hash Router ──────────────────────────────────────────────────────────────
function useHashRoute() {
  const [route, setRoute] = useState(window.location.hash || "#/");
  useEffect(() => {
    const handler = () => setRoute(window.location.hash || "#/");
    window.addEventListener("hashchange", handler);
    return () => window.removeEventListener("hashchange", handler);
  }, []);
  return route;
}

function navigate(hash) {
  window.location.hash = hash;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function TypingDots() {
  return (
    <span className="typing-dots">
      <span /><span /><span />
    </span>
  );
}

function RouteTag({ route }) {
  const map = {
    schema: { label: "Schema", color: "var(--tag-schema)" },
    memory: { label: "Memory", color: "var(--tag-memory)" },
    clarify: { label: "Clarify", color: "var(--tag-clarify)" },
  };
  const info = map[route] || { label: route, color: "var(--tag-default)" };
  return (
    <span className="route-tag" style={{ background: info.color }}>
      {info.label}
    </span>
  );
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <button className="copy-btn" onClick={handleCopy} title="Copy SQL">
      {copied ? <Check size={13} /> : <Copy size={13} />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

function SQLPanel({ sql, retryStrategy }) {
  const [open, setOpen] = useState(true);
  if (!sql) return null;
  return (
    <div className="panel sql-panel">
      <div className="panel-header" onClick={() => setOpen((o) => !o)}>
        <span className="panel-title">
          <Terminal size={14} /> Generated SQL
        </span>
        <div className="panel-header-right">
          {retryStrategy && (
            <span className="retry-badge">
              <RefreshCw size={11} /> {retryStrategy}
            </span>
          )}
          <CopyButton text={sql} />
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </div>
      {open && (
        <div className="monaco-wrap">
          <Editor
            height="160px"
            defaultLanguage="sql"
            value={sql}
            theme="vs-dark"
            options={{
              readOnly: true,
              minimap: { enabled: false },
              fontSize: 13,
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              lineNumbers: "on",
              scrollBeyondLastLine: false,
              wordWrap: "on",
              folding: false,
              renderLineHighlight: "none",
              scrollbar: { vertical: "hidden", horizontal: "auto" },
            }}
          />
        </div>
      )}
    </div>
  );
}

function ResultsTable({ results }) {
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState("asc");
  const [filter, setFilter] = useState("");
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 10;

  if (!results || results.length === 0) return null;

  const columns = Object.keys(results[0]);

  const filtered = filter
    ? results.filter((row) =>
        columns.some((col) =>
          String(row[col]).toLowerCase().includes(filter.toLowerCase())
        )
      )
    : results;

  const sorted = sortKey
    ? [...filtered].sort((a, b) => {
        const va = a[sortKey], vb = b[sortKey];
        if (va == null) return 1;
        if (vb == null) return -1;
        const cmp = typeof va === "number" ? va - vb : String(va).localeCompare(String(vb));
        return sortDir === "asc" ? cmp : -cmp;
      })
    : filtered;

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE);
  const pageData = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const handleSort = (col) => {
    if (sortKey === col) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(col); setSortDir("asc"); }
    setPage(0);
  };

  return (
    <div className="panel results-panel">
      <div className="panel-header">
        <span className="panel-title">
          <BarChart2 size={14} /> Results
          <span className="row-count">{results.length} row{results.length !== 1 ? "s" : ""}</span>
        </span>
        <input
          className="table-filter"
          placeholder="Filter…"
          value={filter}
          onChange={(e) => { setFilter(e.target.value); setPage(0); }}
        />
      </div>
      <div className="table-scroll">
        <table className="result-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col} onClick={() => handleSort(col)} className="sortable-th">
                  {col}
                  {sortKey === col && (
                    <span className="sort-arrow">{sortDir === "asc" ? " ↑" : " ↓"}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageData.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? "row-even" : "row-odd"}>
                {columns.map((col) => (
                  <td key={col} title={String(row[col] ?? "")}>
                    {row[col] == null ? <span className="null-val">NULL</span> : String(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="pagination">
          <button disabled={page === 0} onClick={() => setPage((p) => p - 1)}>←</button>
          <span>{page + 1} / {totalPages}</span>
          <button disabled={page === totalPages - 1} onClick={() => setPage((p) => p + 1)}>→</button>
        </div>
      )}
    </div>
  );
}

function InsightsPanel({ explanation, summary, insights }) {
  const [open, setOpen] = useState(true);
  if (!summary && !insights?.length) return null;
  return (
    <div className="panel insights-panel">
      <div className="panel-header" onClick={() => setOpen((o) => !o)}>
        <span className="panel-title"><Zap size={14} /> Insights</span>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </div>
      {open && (
        <div className="insights-body">
          {explanation && <p className="insight-explanation">{explanation}</p>}
          {summary && <p className="insight-summary">{summary}</p>}
          {insights && insights.length > 0 && (
            <ul className="insight-list">
              {insights.map((ins, i) => (
                <li key={i}><Zap size={11} className="insight-icon" />{ins}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

function ClarifyCard({ question, onAnswer }) {
  const [answer, setAnswer] = useState("");
  return (
    <div className="clarify-card">
      <div className="clarify-icon"><AlertCircle size={16} /></div>
      <div className="clarify-body">
        <p className="clarify-question">{question}</p>
        <div className="clarify-input-row">
          <input
            className="clarify-input"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && answer.trim() && onAnswer(answer.trim())}
            placeholder="Type your answer…"
          />
          <button
            className="clarify-send"
            disabled={!answer.trim()}
            onClick={() => onAnswer(answer.trim())}
          >
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}

function AssistantMessage({ msg, onClarify }) {
  const { data, loading, error } = msg;

  if (loading) {
    return (
      <div className="chat-bubble assistant loading-bubble">
        <TypingDots />
      </div>
    );
  }

  if (error) {
    return (
      <div className="chat-bubble assistant error-bubble">
        <X size={14} className="error-icon" /> {error}
      </div>
    );
  }

  if (!data) return null;

  const isClarify = data.route === "clarify" || !data.success;
  const needsClarify = isClarify && data.clarification;

  return (
    <div className="chat-bubble assistant">
      <div className="bubble-meta">
        <RouteTag route={data.route} />
        {data.reason && <span className="bubble-reason">{data.reason}</span>}
      </div>

      {needsClarify && (
        <ClarifyCard question={data.clarification} onAnswer={onClarify} />
      )}

      {!needsClarify && (
        <>
          <SQLPanel sql={data.sql} retryStrategy={data.retry_strategy} />
          <ResultsTable results={data.results} />
          <InsightsPanel
            explanation={data.query_explanation}
            summary={data.summary}
            insights={data.insights}
          />
          {!data.sql && !data.results && data.error && (
            <div className="error-inline"><AlertCircle size={13} /> {data.error}</div>
          )}
        </>
      )}
    </div>
  );
}

// ─── Suggested prompts ────────────────────────────────────────────────────────
const SUGGESTIONS = [
  "Show top 5 products by list price",
  "Top 10 customers by total sales",
  "List of orders placed in year 2008",
  "Customers with first letter 't' in their last name",
  "All details of the orders placed",
];

// ─── Feature cards data ───────────────────────────────────────────────────────
const FEATURES = [
  {
    icon: <MessageSquare size={24} />,
    iconClass: "icon-nlp",
    title: "Natural Language Queries",
    desc: "Ask questions about your database in plain English — no SQL knowledge required. The agent understands context and intent.",
  },
  {
    icon: <Brain size={24} />,
    iconClass: "icon-sql",
    title: "Intelligent SQL Generation",
    desc: "AI-powered query generation that understands your schema. Produces optimized, production-ready SQL automatically.",
  },
  {
    icon: <RotateCcw size={24} />,
    iconClass: "icon-retry",
    title: "Smart Retry Logic",
    desc: "Failed queries are automatically analyzed and corrected. Multiple retry strategies ensure you always get results.",
  },
  {
    icon: <LineChart size={24} />,
    iconClass: "icon-insights",
    title: "Instant Insights",
    desc: "Get rich summaries, key takeaways, and actionable insights alongside your query results — not just raw data.",
  },
];

// ─── Navbar ───────────────────────────────────────────────────────────────────
function Navbar({ currentRoute }) {
  const isHome = currentRoute === "#/" || currentRoute === "";
  const isChat = currentRoute === "#/chat";

  return (
    <nav className="navbar" id="main-nav">
      <div className="nav-brand" onClick={() => navigate("#/")}>
        <div className="nav-logo">
          <Database size={16} />
        </div>
        <span className="nav-title">SQL Agent</span>
      </div>
      <div className="nav-links">
        <button
          className={`nav-link ${isHome ? "active" : ""}`}
          onClick={() => navigate("#/")}
        >
          Home
        </button>
        <button
          className={`nav-link ${isChat ? "active" : ""}`}
          onClick={() => navigate("#/chat")}
        >
          Chatbot
        </button>
      </div>
      <button className="nav-cta" onClick={() => navigate("#/chat")}>
        <span>Start Chatting</span>
      </button>
    </nav>
  );
}

// ─── Homepage ─────────────────────────────────────────────────────────────────
function HomePage() {
  return (
    <div className="homepage" id="homepage">
      <section className="hero" id="hero-section">
        <div className="hero-badge">
          <span className="hero-badge-dot" />
          Powered by AI · AdventureWorksLT Database
        </div>

        <h1 className="hero-title">
          Talk to Your<br />
          <span className="accent-text">Data.</span>
        </h1>

        <p className="hero-subtitle">
          Ask questions about your database in plain English. Our AI agent generates SQL, 
          executes queries, and delivers insights — all through a simple conversation.
        </p>

        <div className="hero-actions">
          <button className="btn-primary" onClick={() => navigate("#/chat")}>
            Start Chatting <ArrowRight size={18} />
          </button>
          <button className="btn-secondary" onClick={() => {
            document.getElementById("features-section")?.scrollIntoView({ behavior: "smooth" });
          }}>
            <Sparkles size={16} /> Explore Features
          </button>
        </div>
      </section>

      <section className="features-section" id="features-section">
        <div className="features-header">
          <span className="features-label">Features</span>
          <h2 className="features-title">Everything you need to query smarter</h2>
          <p className="features-desc">
            From natural language understanding to intelligent error recovery — 
            built for effortless database exploration.
          </p>
        </div>

        <div className="features-grid" id="features-grid">
          {FEATURES.map((f, i) => (
            <div className="feature-card" key={i} id={`feature-card-${i}`}>
              <div className={`feature-icon ${f.iconClass}`}>
                {f.icon}
              </div>
              <h3 className="feature-card-title">{f.title}</h3>
              <p className="feature-card-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="homepage-footer">
        Conversational SQL Agent · Capstone Project
      </footer>
    </div>
  );
}

// ─── Chat Page ────────────────────────────────────────────────────────────────
function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingClarification, setPendingClarification] = useState(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendQuery = useCallback(async (query, originalQuery = null) => {
    if (!query.trim() || loading) return;
    setInput("");
    setLoading(true);

    const actualQuery = originalQuery ? `${originalQuery} ${query}` : query;
    const userMsg = { id: Date.now(), role: "user", text: actualQuery };
    const loadingMsg = { id: Date.now() + 1, role: "assistant", loading: true };
    setMessages((prev) => [...prev, userMsg, loadingMsg]);

    try {
      const data = await postQuery(actualQuery);
      setMessages((prev) =>
        prev.map((m) => (m.id === loadingMsg.id ? { ...m, loading: false, data } : m))
      );

      if (data.route === "clarify") {
        setPendingClarification(actualQuery);
      } else {
        setPendingClarification(null);
      }
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === loadingMsg.id
            ? { ...m, loading: false, error: err.message || "Request failed" }
            : m
        )
      );
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setPendingClarification(null);
    sendQuery(input);
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="chatbot-page" id="chatbot-page">
      <main className="chat-area">
        <div className="chat-container">
          {isEmpty ? (
            <div className="empty-state" id="chat-empty-state">
              <div className="empty-icon-wrap">
                <Database size={36} />
              </div>
              <h2>Ask anything about your database</h2>
              <p>Query the AdventureWorksLT database in plain English. The agent will generate SQL, run it, and explain the results.</p>
              <div className="suggestions">
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="suggestion-chip" onClick={() => sendQuery(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((msg) =>
                msg.role === "user" ? (
                  <div key={msg.id} className="chat-bubble user">
                    {msg.text}
                  </div>
                ) : (
                  <AssistantMessage
                    key={msg.id}
                    msg={msg}
                    onClarify={(answer) => sendQuery(answer, pendingClarification)}
                  />
                )
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </div>
      </main>

      <footer className="input-bar" id="chat-input-bar">
        <form onSubmit={handleSubmit} className="input-form">
          <input
            ref={inputRef}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your database…"
            disabled={loading}
            autoFocus
            id="chat-input"
          />
          <button
            type="submit"
            className="send-btn"
            disabled={!input.trim() || loading}
            id="send-button"
          >
            {loading ? <Loader size={16} className="spin" /> : <Send size={16} />}
          </button>
        </form>
        <p className="input-hint">
          <Info size={11} /> Queries run against AdventureWorksLT · Backend at {API_BASE}
        </p>
      </footer>
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const route = useHashRoute();

  return (
    <>
      {/* Background layers */}
      <div className="gradient-bg" />
      <div className="noise-overlay" />

      {/* Navigation */}
      <Navbar currentRoute={route} />

      {/* Page content */}
      {route === "#/chat" ? <ChatPage /> : <HomePage />}
    </>
  );
}