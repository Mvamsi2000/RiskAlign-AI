import { Card } from "../components/Card";
import type { ScoreFinding } from "../lib/api";

interface NarrativesProps {
  scores?: ScoreFinding[];
}

export function NarrativesView({ scores }: NarrativesProps) {
  if (!scores || scores.length === 0) {
    return <Card title="No narratives">Scores will appear after findings are ingested.</Card>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {scores.map((finding) => (
        <Card
          key={finding.id ?? finding.title}
          title={`${finding.title ?? "Untitled"} — ${finding.score.toFixed(2)} (${finding.priority})`}
        >
          <p className="text-sm text-slate-500">
            Context multiplier {finding.context_multiplier.toFixed(2)} with {finding.effort_hours.toFixed(1)}h estimated effort.
          </p>
          <div className="mt-3 space-y-2 text-xs text-slate-500">
            <p className="font-medium text-slate-600">Component contributions</p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(finding.components).map(([name, value]) => (
                <div key={name} className="flex items-center justify-between rounded border border-slate-200 px-2 py-1">
                  <span className="capitalize">{name}</span>
                  <span className="font-medium text-slate-700">{value.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
