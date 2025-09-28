import { useState } from "react";

import { Card } from "../components/Card";
import { queryIntent } from "../lib/api";

export function CopilotView() {
  const [query, setQuery] = useState("Suggest the next remediation wave");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Awaited<ReturnType<typeof queryIntent>> | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await queryIntent(query);
      setResult(response);
    } catch (error) {
      setResult({ intent: "error", response: "Unable to reach the API", details: { matched_keywords: [], confidence: 0, endpoint: null } });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title="Copilot router"
      description="Ask natural-language questions. The router suggests the best backend endpoint."
    >
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
          {loading ? "Routing…" : "Ask"}
        </button>
      </form>

      {result ? (
        <div className="mt-4 space-y-2 text-sm text-slate-600">
          <p>
            <span className="font-medium text-slate-800">Intent:</span> {result.intent}
          </p>
          <p>{result.response}</p>
          <div className="text-xs text-slate-500">
            <p>Matched keywords: {result.details.matched_keywords.join(", ") || "None"}</p>
            <p>Confidence: {(result.details.confidence * 100).toFixed(0)}%</p>
            <p>Endpoint: {result.details.endpoint ?? "Not sure"}</p>
          </div>
        </div>
      ) : null}
    </Card>
  );
}
