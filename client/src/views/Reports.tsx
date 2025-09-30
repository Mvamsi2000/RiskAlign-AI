import { Card } from "../components/Card";
import type { SummaryGenerateResponse } from "../lib/api";

interface ReportsViewProps {
  summary?: SummaryGenerateResponse;
}

export function ReportsView({ summary }: ReportsViewProps) {
  if (!summary) {
    return <Card title="No report yet">Run the optimiser to generate a summary.</Card>;
  }

  return (
    <Card title="Executive summary" description="Copy this HTML into a board-ready briefing.">
      <p className="mb-3 text-xs text-slate-500">Saved to: {summary.path}</p>
      <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: summary.html }} />
    </Card>
  );
}
