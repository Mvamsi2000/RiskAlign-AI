import { useQuery } from "@tanstack/react-query";
import { fetchScores, ScoredFinding } from "../api/client";
import { Finding } from "../data/sampleFindings";

interface Props {
  findings: Finding[];
}

export function ScoreView({ findings }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["scores", findings],
    queryFn: () => fetchScores(findings)
  });

  if (isLoading) {
    return <p>Calculating risk scores…</p>;
  }

  if (error) {
    return <p>Unable to load scores. Please ensure the backend is running.</p>;
  }

  return (
    <div className="card-grid">
      {data?.findings.map((item: ScoredFinding) => (
        <div key={item.finding.id} className="card">
          <h3>{item.finding.title}</h3>
          <p>{item.finding.description}</p>
          <p>
            <span className="badge">Score: {item.score}</span>
          </p>
          <p>Priority: {item.priority.toUpperCase()}</p>
          <p>{item.recommended_action}</p>
          <h4>Top signals</h4>
          <ul>
            {item.contributions.slice(0, 3).map((contribution) => (
              <li key={contribution.signal}>
                {contribution.signal} · {contribution.impact.toFixed(2)} ({contribution.rationale})
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
