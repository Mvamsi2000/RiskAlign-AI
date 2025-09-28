import { useState } from "react";

import { Card } from "../components/Card";
import type { OptimizePlanResponse } from "../lib/api";

interface PlanProps {
  plan?: OptimizePlanResponse;
  onFeedback?: (findingId: string, action: "agree" | "disagree") => Promise<void>;
}

export function PlanView({ plan, onFeedback }: PlanProps) {
  const [submitting, setSubmitting] = useState<string | null>(null);

  if (!plan || plan.waves.length === 0) {
    return <Card title="No remediation waves">All findings fall below the prioritisation threshold.</Card>;
  }

  const handleFeedback = async (findingId: string, action: "agree" | "disagree") => {
    if (!onFeedback) return;
    setSubmitting(findingId + action);
    try {
      await onFeedback(findingId, action);
    } finally {
      setSubmitting(null);
    }
  };

  return (
    <div className="space-y-4">
      <Card
        title="Wave overview"
        description="Risk saved per wave and total effort under the selected capacity."
      >
        <div className="grid gap-4 md:grid-cols-3">
          <Metric label="Total waves" value={plan.totals.waves.toString()} />
          <Metric label="Total hours" value={plan.totals.total_hours.toFixed(1)} />
          <Metric label="Risk saved" value={plan.totals.total_risk_saved.toFixed(1)} />
        </div>
      </Card>

      {plan.waves.map((wave) => (
        <Card key={wave.name} title={`${wave.name} — ${wave.risk_saved.toFixed(1)} risk saved`}>
          <p className="text-sm text-slate-500">{wave.total_hours.toFixed(1)}h effort • {wave.items.length} findings</p>
          <div className="mt-4 overflow-hidden rounded-lg border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Finding</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Priority</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Effort (h)</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Score</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Risk saved</th>
                  {onFeedback ? <th className="px-4 py-2 text-right font-medium text-slate-600">Feedback</th> : null}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {wave.items.map((item) => {
                  const key = item.id ?? item.title ?? "unknown";
                  const findingId = item.id ?? key;
                  const isSubmittingAgree = submitting === findingId + "agree";
                  const isSubmittingDisagree = submitting === findingId + "disagree";
                  return (
                    <tr key={key}>
                      <td className="px-4 py-2 font-medium text-slate-800">{item.title ?? "Untitled"}</td>
                      <td className="px-4 py-2 text-slate-600">{item.priority}</td>
                      <td className="px-4 py-2 text-slate-600">{item.effort_hours.toFixed(1)}</td>
                      <td className="px-4 py-2 text-slate-600">{item.score.toFixed(2)}</td>
                      <td className="px-4 py-2 text-slate-600">{item.risk_saved.toFixed(2)}</td>
                      {onFeedback ? (
                        <td className="px-4 py-2 text-right">
                          <div className="inline-flex gap-2">
                            <button
                              className="rounded-full border border-emerald-500 px-3 py-1 text-xs font-medium text-emerald-600 transition hover:bg-emerald-50"
                              disabled={isSubmittingAgree}
                              onClick={() => handleFeedback(findingId, "agree")}
                            >
                              {isSubmittingAgree ? "Sending…" : "Agree"}
                            </button>
                            <button
                              className="rounded-full border border-rose-500 px-3 py-1 text-xs font-medium text-rose-600 transition hover:bg-rose-50"
                              disabled={isSubmittingDisagree}
                              onClick={() => handleFeedback(findingId, "disagree")}
                            >
                              {isSubmittingDisagree ? "Sending…" : "Disagree"}
                            </button>
                          </div>
                        </td>
                      ) : null}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      ))}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
