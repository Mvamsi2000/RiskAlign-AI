import { useMemo, useState } from "react";
import { Loader2, Sparkles, Table2, Target, Workflow } from "lucide-react";

import { Card } from "./components/Card";
import { useRiskData } from "./hooks/useRiskData";
import type { ControlMapping, OptimizePlanResponse, ScoredFinding } from "./lib/api";

const TABS = ["Plan", "Compliance", "Narratives", "Summary"] as const;

export default function App() {
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]>("Plan");
  const [maxHoursPerWave, setMaxHoursPerWave] = useState(16);
  const { findingsQuery, scoresQuery, wavesQuery, controlsQuery, impactQuery, summaryQuery, priorityCards } =
    useRiskData(maxHoursPerWave);

  const isLoading =
    findingsQuery.isLoading ||
    scoresQuery.isLoading ||
    wavesQuery.isLoading ||
    controlsQuery.isLoading ||
    impactQuery.isLoading ||
    summaryQuery.isLoading;

  const hasError =
    findingsQuery.isError ||
    scoresQuery.isError ||
    wavesQuery.isError ||
    controlsQuery.isError ||
    impactQuery.isError ||
    summaryQuery.isError;

  const totalFindings = findingsQuery.data?.length ?? 0;
  const criticalCount = priorityCards.find((card) => card.priority === "Critical")?.count ?? 0;
  const highCount = priorityCards.find((card) => card.priority === "High")?.count ?? 0;
  const highPriorityTotal = criticalCount + highCount;

  const intentHint = useMemo(() => {
    if (!scoresQuery.data) return "Ask the copilot for quick wins under 10 hours.";
    const highImpact = scoresQuery.data.results
      .filter((item) => item.priority === "Critical" || item.priority === "High")
      .slice(0, 1)
      .map((item) => item.title)
      .join(", ");
    return highImpact ? `Focus next on: ${highImpact}.` : "All findings are currently manageable.";
  }, [scoresQuery.data]);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-sm uppercase tracking-wide text-brand-dark">RiskAlign-AI</p>
            <h1 className="mt-1 text-3xl font-semibold text-slate-900">Cyber Risk Decision Intelligence</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-500">Explainable prioritisation, compliance coverage, and executive summaries in one workspace.</p>
          </div>
          <div className="hidden text-right md:block">
            <p className="text-sm font-medium text-slate-500">Wave capacity (hrs)</p>
            <input
              type="number"
              min={4}
              max={40}
              value={maxHoursPerWave}
              onChange={(event) => {
                const next = Number(event.target.value);
                setMaxHoursPerWave(Number.isNaN(next) ? 16 : Math.min(Math.max(next, 4), 40));
              }}
              className="mt-1 w-28 rounded-lg border border-slate-300 px-3 py-2 text-right text-sm font-medium text-slate-700 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
            />
            <p className="mt-1 text-xs text-slate-400">Used for plan optimisation.</p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-6 py-8">
        <section className="grid gap-4 md:grid-cols-4">
          <Card title={<span className="flex items-center gap-2"><Sparkles className="h-4 w-4 text-brand" />Findings scored</span>}>
            <p className="text-3xl font-semibold text-slate-900">{totalFindings}</p>
            <p className="text-xs text-slate-500">Auto ingested sample dataset.</p>
          </Card>
          <Card title={<span className="flex items-center gap-2"><Target className="h-4 w-4 text-brand" />High priority</span>}>
            <p className="text-3xl font-semibold text-slate-900">{highPriorityTotal}</p>
            <p className="text-xs text-slate-500">{criticalCount} critical • {highCount} high.</p>
          </Card>
          <Card title={<span className="flex items-center gap-2"><Workflow className="h-4 w-4 text-brand" />Plan readiness</span>}>
            <p className="text-3xl font-semibold text-slate-900">{wavesQuery.data?.waves.length ?? 0} waves</p>
            <p className="text-xs text-slate-500">Optimised for {maxHoursPerWave}h capacity.</p>
          </Card>
          <Card title={<span className="flex items-center gap-2"><Table2 className="h-4 w-4 text-brand" />Compliance boost</span>}>
            <p className="text-3xl font-semibold text-slate-900">
              {impactQuery.data ? impactQuery.data.compliance_gain.toFixed(1) : "0.0"}%
            </p>
            <p className="text-xs text-slate-500">Estimated coverage uplift.</p>
          </Card>
        </section>

        <section className="rounded-xl border border-dashed border-brand/40 bg-white p-5 text-sm text-slate-600">
          <p className="font-medium text-brand-dark">Analyst hint</p>
          <p className="mt-1 text-slate-500">{intentHint}</p>
        </section>

        <nav className="flex flex-wrap gap-2">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-full px-5 py-2 text-sm font-medium transition ${
                activeTab === tab ? "bg-brand text-white shadow" : "bg-white text-slate-600 hover:bg-slate-100"
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>

        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-slate-500">
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Loading decision intelligence…
          </div>
        ) : hasError ? (
          <Card title="Unable to load data">
            <p className="text-sm text-slate-500">Check that the FastAPI server is running on port 8000.</p>
          </Card>
        ) : (
          <section className="space-y-6">
{activeTab === "Plan" && wavesQuery.data ? <PlanView data={wavesQuery.data} /> : null}
{activeTab === "Compliance" && controlsQuery.data ? <ComplianceView data={controlsQuery.data.mappings} /> : null}
{activeTab === "Narratives" && scoresQuery.data ? <NarrativesView data={scoresQuery.data.results} /> : null}
            {activeTab === "Summary" && summaryQuery.data ? <SummaryView html={summaryQuery.data.html} /> : null}
          </section>
        )}
      </main>
    </div>
  );
}

function PlanView({ data }: { data?: OptimizePlanResponse }) {
  if (!data?.waves.length) {
    return <Card title="No remediation waves">All findings fall below the prioritisation threshold.</Card>;
  }

  return (
    <div className="space-y-4">
      {data.waves.map((wave) => (
        <Card key={wave.name} title={`${wave.name} — ${wave.expected_risk_reduction.toFixed(1)} risk pts saved`}>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <p className="text-sm text-slate-500">{wave.total_hours.toFixed(1)}h effort • {wave.items.length} findings</p>
          </div>
          <div className="mt-4 overflow-hidden rounded-lg border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Finding</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Score</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Effort (h)</th>
                  <th className="px-4 py-2 text-left font-medium text-slate-600">Risk reduction</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {wave.items.map((item) => (
                  <tr key={item.id}>
                    <td className="px-4 py-2 font-medium text-slate-800">{item.title}</td>
                    <td className="px-4 py-2 text-slate-600">{item.score.toFixed(2)}</td>
                    <td className="px-4 py-2 text-slate-600">{item.effort_hours.toFixed(1)}</td>
                    <td className="px-4 py-2 text-slate-600">{item.risk_reduction.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ))}
    </div>
  );
}

function ComplianceView({ data }: { data?: ControlMapping[] }) {
  if (!data?.length) {
    return <Card title="No mapped controls">Add CVE identifiers to see CIS / NIST coverage.</Card>;
  }

  return (
    <Card title="Mapped controls" description="Crosswalk of CVEs to CIS controls.">
      <div className="overflow-hidden rounded-lg border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Control</th>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Finding</th>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.map((item) => (
              <tr key={`${item.control}-${item.finding}`}>
                <td className="px-4 py-2 font-medium text-slate-800">{item.control}</td>
                <td className="px-4 py-2 text-slate-600">{item.finding}</td>
                <td className="px-4 py-2 text-slate-600">{item.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function NarrativesView({ data }: { data?: ScoredFinding[] }) {
  if (!data?.length) {
    return <Card title="No narratives">Scores will appear after findings are ingested.</Card>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {data.map((finding) => (
        <Card key={finding.id} title={`${finding.title} — ${finding.score} (${finding.priority})`}>
          <p className="text-sm text-slate-600">{finding.narrative}</p>
          <div className="mt-3 space-y-2 text-xs text-slate-500">
            {finding.contributions.map((contribution) => (
              <div key={contribution.name} className="flex items-center justify-between">
                <span>{contribution.name}</span>
                <span className="font-medium text-slate-700">{contribution.contribution.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}

function SummaryView({ html }: { html: string }) {
  return (
    <Card title="Executive summary" description="Copy this HTML into your executive report.">
      <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: html }} />
    </Card>
  );
}
