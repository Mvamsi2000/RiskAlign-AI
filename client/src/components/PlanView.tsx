import { useQuery } from "@tanstack/react-query";
import { fetchPlan, PlanItem } from "../api/client";
import { Finding } from "../data/sampleFindings";

interface Props {
  findings: Finding[];
}

export function PlanView({ findings }: Props) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["plan", findings],
    queryFn: () => fetchPlan(findings)
  });

  if (isLoading) {
    return <p>Building optimization plan…</p>;
  }

  if (error) {
    return <p>Unable to build plan. Please ensure the backend is running.</p>;
  }

  return (
    <div>
      <div className="summary-box">
        <h2>Remediation roadmap</h2>
        <p>{data?.summary}</p>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>Wave</th>
            <th>Finding</th>
            <th>Hours</th>
            <th>Score</th>
            <th>Risk Δ</th>
          </tr>
        </thead>
        <tbody>
          {data?.plan.map((item: PlanItem) => (
            <tr key={item.finding_id}>
              <td>{item.wave}</td>
              <td>{item.title}</td>
              <td>{item.estimated_hours}</td>
              <td>{item.score.toFixed(2)}</td>
              <td>{item.expected_risk_reduction.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
