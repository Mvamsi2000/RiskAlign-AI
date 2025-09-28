import { useMemo, useState } from "react";
import { Loader2, Sparkles, Table2, Target, Workflow } from "lucide-react";

import { Card } from "./components/Card";
import { useRiskData } from "./hooks/useRiskData";
import { submitFeedback } from "./lib/api";
import { ComplianceView } from "./views/Compliance";
import { CopilotView } from "./views/Copilot";
import { NarrativesView } from "./views/Narratives";
import { PlanView } from "./views/Plan";

const TABS = ["Plan", "Compliance", "Narratives", "Summary"] as const;

type Tab = (typeof TABS)[number];

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>("Plan");
  const [maxHoursPerWave, setMaxHoursPerWave] = useState(16);
  const [feedbackNotice, setFeedbackNotice] = useState<string | null>(null);

  const {
    findingsQuery,
    scoresQuery,
    wavesQuery,
    controlsQuery,
    impactQuery,
    summaryQuery,
    priorityCards
  } = useRiskData(maxHoursPerWave);

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
  const highPriorityTotal = priorityCards
    .filter((card) => card.priority === "Critical" || card.priority === "High")
    .reduce((acc, item) => acc + item.count, 0);
  const criticalCount = priorityCards.find((item) => item.priority === "Critical")?.count ?? 0;

  const intentHint = useMemo(() => {
    const highImpact = scoresQuery.data?.findings
      .filter((item) => item.priority === "Critical" || item.priority === "High")
      .slice(0, 1)
      .map((item) => item.title)
      .join(", ");
    return highImpact ? `Focus next on: ${highImpact}.` : "All findings are currently manageable.";
  }, [scoresQuery.data]);

  const readinessLabel = impactQuery.data ? `${impactQuery.data.readiness_percent.toFixed(1)}% ready` : "0% ready";
  const complianceLabel = impactQuery.data ? `${impactQuery.data.compliance_boost.toFixed(1)}%` : "0.0%";

  const handleFeedback = async (findingId: string, action: "agree" | "disagree") => {
    try {
      await submitFeedback({ finding_id: findingId, action });
      setFeedbackNotice(`Recorded ${action} for ${findingId}.`);
    } catch (error) {
      setFeedbackNotice("Unable to record feedback. Check the API server.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-sm uppercase tracking-wide text-brand-dark">RiskAlign-AI</p>
            <h1 className="mt-1 text-3xl font-semibold text-slate-900">Cyber Risk Decision Intelligence</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-500">
              Explainable prioritisation, compliance coverage, and executive summaries in one workspace.
            </p>
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
            <p className="text-xs text-slate-500">{criticalCount} critical • {highPriorityTotal - criticalCount} high.</p>
          </Card>
          <Card title={<span className="flex items-center gap-2"><Workflow className="h-4 w-4 text-brand" />Plan readiness</span>}>
            <p className="text-3xl font-semibold text-slate-900">{readinessLabel}</p>
            <p className="text-xs text-slate-500">Optimised for {maxHoursPerWave}h capacity.</p>
          </Card>
          <Card title={<span className="flex items-center gap-2"><Table2 className="h-4 w-4 text-brand" />Compliance boost</span>}>
            <p className="text-3xl font-semibold text-slate-900">{complianceLabel}</p>
            <p className="text-xs text-slate-500">Estimated coverage uplift.</p>
          </Card>
        </section>

        <section className="rounded-xl border border-dashed border-brand/40 bg-white p-5 text-sm text-slate-600">
          <p className="font-medium text-brand-dark">Analyst hint</p>
          <p className="mt-1 text-slate-500">{intentHint}</p>
        </section>

        {feedbackNotice ? (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-xs text-emerald-700">
            {feedbackNotice}
          </div>
        ) : null}

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
            {activeTab === "Plan" ? (
              <PlanView plan={wavesQuery.data} onFeedback={handleFeedback} />
            ) : null}
            {activeTab === "Compliance" ? <ComplianceView data={controlsQuery.data} /> : null}
            {activeTab === "Narratives" ? <NarrativesView scores={scoresQuery.data?.findings} /> : null}
            {activeTab === "Summary" ? (
              <SummaryView html={summaryQuery.data?.html ?? ""} path={summaryQuery.data?.path ?? ""} />
            ) : null}
          </section>
        )}

        <CopilotView />
      </main>
    </div>
  );
}

function SummaryView({ html, path }: { html: string; path: string }) {
  return (
    <Card title="Executive summary" description="Copy this HTML into your executive report.">
      {path ? (
        <p className="mb-3 text-xs text-slate-500">Saved to: {path}</p>
      ) : null}
      <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: html }} />
    </Card>
  );
}
