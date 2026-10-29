import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { getSuggestions, sendChatMessage } from "../api/assistant";
import Topbar from "../components/layout/Topbar";
import { useApiData } from "../hooks/useApiData";

const GREETING = {
  role: "assistant",
  text: "Hi! I'm the PAIMANA Sentinel assistant. Ask me about project risk, delays, cost escalation, alerts, or compare ministries, sectors and states.",
};

export default function Assistant() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const focusProject = searchParams.get("project");
  const initialQuestion = searchParams.get("q");

  const [messages, setMessages] = useState([GREETING]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const conversationId = useRef(null);
  const bottomRef = useRef(null);
  const autoSent = useRef(false);

  const suggestions = useApiData(getSuggestions, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, sending]);

  const send = useCallback(
    async (text) => {
      const message = text.trim();
      if (!message || sending) return;
      setMessages((m) => [...m, { role: "user", text: message }]);
      setInput("");
      setSending(true);
      try {
        const { data } = await sendChatMessage({
          message,
          conversationId: conversationId.current,
          projectId: focusProject,
        });
        conversationId.current = data.conversation_id;
        setMessages((m) => [
          ...m,
          { role: "assistant", text: data.answer, sources: data.sources, engine: data.engine },
        ]);
      } catch (err) {
        setMessages((m) => [...m, { role: "assistant", text: err.message, error: true }]);
      } finally {
        setSending(false);
      }
    },
    [sending, focusProject]
  );

  useEffect(() => {
    if (initialQuestion && !autoSent.current) {
      autoSent.current = true;
      send(initialQuestion);
    }
  }, [initialQuestion, send]);

  function newChat() {
    conversationId.current = null;
    setMessages([GREETING]);
    setInput("");
  }

  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <Topbar title="AI Assistant" subtitle="Ask questions about the monitored infrastructure projects" />

      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="text-xs text-text-muted">Answers are grounded in the monitored project database.</p>
        <button
          onClick={newChat}
          className="rounded-lg border border-border px-3 py-1.5 text-xs text-text-muted hover:bg-surface-hover"
        >
          New chat
        </button>
      </div>

      <div className="flex min-h-0 flex-1 flex-col rounded-xl border border-border bg-surface">
        <div className="min-h-[320px] flex-1 space-y-4 overflow-y-auto p-4">
          {messages.map((m, i) => (
            <Message key={i} message={m} onOpenProject={(id) => navigate(`/projects/${id}`)} />
          ))}
          {sending && (
            <div className="flex">
              <div className="flex items-center gap-1 rounded-2xl bg-surface-hover px-4 py-3">
                {[0, 1, 2].map((d) => (
                  <span
                    key={d}
                    className="h-2 w-2 animate-bounce rounded-full bg-text-muted"
                    style={{ animationDelay: `${d * 150}ms` }}
                  />
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-border p-3">
          {suggestions.data && (
            <div className="mb-3 flex flex-wrap gap-2">
              {suggestions.data.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  disabled={sending}
                  className="rounded-full border border-border bg-bg px-3 py-1 text-xs text-text-muted transition-colors hover:border-accent hover:text-accent disabled:opacity-50"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              rows={2}
              maxLength={1000}
              placeholder="Ask about a project, ministry, sector or state..."
              className="flex-1 resize-none rounded-lg border border-border bg-bg px-3 py-2 text-sm text-text placeholder:text-text-muted"
            />
            <button
              onClick={() => send(input)}
              disabled={sending || !input.trim()}
              className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              Send
            </button>
          </div>
          <p className="mt-1 text-[11px] text-text-muted">Enter to send · Shift+Enter for a new line</p>
        </div>
      </div>
    </div>
  );
}

function Message({ message, onOpenProject }) {
  const isUser = message.role === "user";
  const bubble = isUser
    ? "bg-accent text-white"
    : message.error
      ? "bg-critical-soft text-critical"
      : "bg-surface-hover text-text";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className="max-w-[85%]">
        <div className={`whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${bubble}`}>
          {message.text}
        </div>
        {message.sources?.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {message.sources.map((s) => (
              <button
                key={s.project_id}
                onClick={() => onOpenProject(s.project_id)}
                title={s.project_id}
                className="max-w-xs truncate rounded-full border border-border bg-bg px-2.5 py-0.5 text-xs text-accent hover:bg-surface-hover"
              >
                {s.project_name}
              </button>
            ))}
          </div>
        )}
        {message.engine && (
          <div className="mt-1">
            <span
              className="rounded bg-accent-soft px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-accent"
              title="Answers are grounded in the monitored project database"
            >
              {message.engine}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
