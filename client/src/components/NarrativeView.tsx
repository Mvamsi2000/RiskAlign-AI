import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { fetchNaturalLanguage } from "../api/client";
import { Finding } from "../data/sampleFindings";

interface Props {
  findings: Finding[];
}

export function NarrativeView({ findings }: Props) {
  const [query, setQuery] = useState("Which quick wins should we start with?");

  const mutation = useMutation({
    mutationFn: () => fetchNaturalLanguage(query, findings)
  });

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    mutation.mutate();
  };

  return (
    <div className="card">
      <h3>Natural-language copilots</h3>
      <p>Ask RiskAlign-AI a question and receive an intent-routed response.</p>
      <form onSubmit={handleSubmit}>
        <textarea value={query} onChange={(event) => setQuery(event.target.value)} />
        <button className="nav-button" type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Thinking…" : "Ask"}
        </button>
      </form>
      {mutation.data && (
        <div style={{ marginTop: "1rem" }}>
          <h4>{mutation.data.intent}</h4>
          <pre>{mutation.data.result.items}</pre>
        </div>
      )}
      {mutation.error && <p>Unable to process the question. Please ensure the backend is running.</p>}
    </div>
  );
}
