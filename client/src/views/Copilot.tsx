import { useMemo, useState } from "react";

import { Card } from "../components/Card";
import { AIProviderId, ChatMessage, chatWithAI } from "../lib/api";

interface CopilotViewProps {
  providerId: AIProviderId;
  providerLabel: string;
  namespace?: string;
}

const SYSTEM_PROMPT =
  "You are RiskAlign Copilot, a cybersecurity assistant helping prioritise remediation. Provide clear, concise responses.";

export function CopilotView({ providerId, providerLabel, namespace }: CopilotViewProps) {
  const [query, setQuery] = useState("Suggest the next remediation wave");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<ChatMessage[]>([{ role: "system", content: SYSTEM_PROMPT }]);
  const [error, setError] = useState<string | null>(null);

  const providerBadge = providerId.toUpperCase();
  const conversation = useMemo(
    () => history.filter((message) => message.role !== "system"),
    [history]
  );

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const messages = [...history, { role: "user", content: query.trim() }];
      const response = await chatWithAI(messages);
      setHistory(response.messages);
      setQuery("");
    } catch (error) {
      setError("Unable to reach the AI provider. Try switching AI mode or retry later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title={
        <div className="flex items-center justify-between">
          <span>Copilot router</span>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
            AI: {providerBadge}
          </span>
        </div>
      }
      description="Ask natural-language questions. Responses come from the configured AI provider."
    >
      <p className="mb-3 text-xs text-slate-400">
        Namespace: {namespace ?? "default"} • Provider: {providerLabel}
      </p>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3 md:flex-row">
        <input
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="e.g. Map controls for the latest CVEs"
        />
        <button
          type="submit"
          className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white shadow hover:bg-brand-dark disabled:bg-slate-300"
          disabled={loading}
        >
          {loading ? "Thinking…" : "Ask"}
        </button>
      </form>

      {error ? <p className="mt-3 text-xs text-rose-500">{error}</p> : null}

      {conversation.length ? (
        <div className="mt-4 space-y-4 text-sm text-slate-600">
          {conversation.map((message, index) => (
            <div key={`${message.role}-${index}`} className="space-y-1">
              <p className="text-xs uppercase tracking-wide text-slate-400">{message.role === "assistant" ? "Copilot" : "You"}</p>
              <p className="rounded-lg bg-slate-100 px-3 py-2 text-slate-700">{message.content}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-4 text-sm text-slate-500">Ask a question to start a conversation with the Copilot.</p>
      )}
    </Card>
  );
}
