import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ClipboardList,
  CloudUpload,
  Moon,
  ShieldCheck,
  Sparkles,
  Sun,
  Workflow
} from "lucide-react";

import { Card } from "./components/Card";
import { useRiskData } from "./hooks/useRiskData";
import {
  AIProviderId,
  listAIProviders,
  onAIProviderError,
  submitFeedback
} from "./lib/api";
import { ComplianceView } from "./views/Compliance";
import { CopilotView } from "./views/Copilot";
import { ImportView } from "./views/Import";
import { NarrativesView } from "./views/Narratives";
import { PlanView } from "./views/Plan";
import { ReportsView } from "./views/Reports";

type ViewKey = "import" | "plan" | "compliance" | "reports" | "copilot";

const NAV_ITEMS: { key: ViewKey; label: string; icon: ReactNode }[] = [
  { key: "import", label: "Import", icon: <CloudUpload className="h-4 w-4" /> },
  { key: "plan", label: "Plan", icon: <Workflow className="h-4 w-4" /> },
  { key: "compliance", label: "Compliance", icon: <ShieldCheck className="h-4 w-4" /> },
  { key: "reports", label: "Reports", icon: <ClipboardList className="h-4 w-4" /> },
  { key: "copilot", label: "Copilot", icon: <Sparkles className="h-4 w-4" /> }
];

const DEFAULT_AI_PROVIDERS: { id: AIProviderId; label: string }[] = [
  { id: "local", label: "Local (Ollama)" },
  { id: "online", label: "Online (OpenAI)" }
];

export default function App() {
  const [activeView, setActiveView] = useState<ViewKey>("plan");
  const [maxHoursPerWave, setMaxHoursPerWave] = useState(16);
  const [feedbackNotice, setFeedbackNotice] = useState<string | null>(null);
  const [aiNotice, setAINotice] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  });
  const queryClient = useQueryClient();
  const [aiProvider, setAIProvider] = useState<AIProviderId>(() => {
    if (typeof window === "undefined") {
      return "local";
    }
    const stored = window.localStorage.getItem("aiProvider");
    return stored === "online" ? "online" : "local";
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const aiProvidersQuery = useQuery({
    queryKey: ["ai-providers"],
    queryFn: listAIProviders,
    staleTime: 60_000
  });

  useEffect(() => {
    const unsubscribe = onAIProviderError((message) => {
      setAINotice(`AI provider issue: ${message}. Try switching AI mode.`);
    });
    return unsubscribe;
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem("aiProvider", aiProvider);
    }
    queryClient.invalidateQueries();
    setAINotice(null);
  }, [aiProvider, queryClient]);

  useEffect(() => {
    const options = aiProvidersQuery.data ?? DEFAULT_AI_PROVIDERS;
    if (!options.some((option) => option.id === aiProvider)) {
      setAIProvider(options[0]?.id ?? "local");
    }
  }, [aiProvidersQuery.data, aiProvider]);

  const {
    findingsQuery,
    scoresQuery,
    wavesQuery,
    controlsQuery,
    impactQuery,
    summaryQuery,
    priorityCards
  } = useRiskData(maxHoursPerWave, aiProvider);

  const providerOptions = aiProvidersQuery.data ?? DEFAULT_AI_PROVIDERS;
  const activeProviderLabel =
    providerOptions.find((option) => option.id === aiProvider)?.label ?? "Local (Ollama)";

  const isLoading =
    findingsQuery.isLoading ||
    scoresQuery.isLoading ||
    wavesQuery.isLoading ||
    controlsQuery.isLoading ||
    impactQuery.isLoading;

  const hasError =
    findingsQuery.isError ||
    scoresQuery.isError ||
    wavesQuery.isError ||
    controlsQuery.isError ||
    impactQuery.isError;

  const totalFindings = findingsQuery.data?.length ?? 0;
  const highPriorityTotal = priorityCards
    .filter((card) => card.priority === "Critical" || card.priority === "High")
    .reduce((acc, item) => acc + item.count, 0);
  const criticalCount = priorityCards.find((item) => item.priority === "Critical")?.count ?? 0;

  const readinessLabel = impactQuery.data
    ? `${impactQuery.data.readiness_percent.toFixed(1)}%`
    : "0%";
  const complianceLabel = controlsQuery.data ? `${controlsQuery.data.coverage.toFixed(1)}%` : "0.0%";

  const intentHint = useMemo(() => {
    const highImpact = scoresQuery.data?.findings
      .filter((item) => item.priority === "Critical" || item.priority === "High")
      .slice(0, 1)
      .map((item) => item.title)
      .join(", ");
    return highImpact ? `Focus next on: ${highImpact}.` : "All findings are currently manageable.";
  }, [scoresQuery.data]);

  const handleFeedback = async (findingId: string, action: "agree" | "disagree") => {
    try {
      await submitFeedback({ finding_id: findingId, action });
      setFeedbackNotice(`Recorded ${action} for ${findingId}.`);
    } catch (error) {
      setFeedbackNotice("Unable to record feedback. Check the API server.");
    }
  };

  return (
    <div className={`flex min-h-screen ${darkMode ? "bg-slate-900 text-slate-100" : "bg-slate-50 text-slate-900"}`}>
      <aside className="hidden w-60 flex-col border-r border-slate-200 bg-white/80 p-6 dark:bg-slate-800/80 md:flex">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-wide text-slate-400">RiskAlign-AI</p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">
            Decision workspace
          </h1>
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-300">
            Import, prioritise, map to controls, and brief executives from one hub.
          </p>
        </div>
        <nav className="space-y-2">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.key}
              onClick={() => setActiveView(item.key)}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                activeView === item.key
                  ? "bg-brand text-white shadow"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
              }`}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="flex-1 space-y-6 p-6 md:p-10">
        <header className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800/80 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-3xl font-semibold text-slate-900 dark:text-white">Cyber risk intelligence</h2>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">
              Explainable prioritisation, compliance coverage, and executive narratives.
            </p>
          </div>
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-400" htmlFor="ai-mode-select">
                AI mode
              </label>
              <select
                id="ai-mode-select"
                aria-label="Select AI provider"
                value={aiProvider}
                disabled={aiProvidersQuery.isLoading}
                onChange={(event) => setAIProvider(event.target.value as AIProviderId)}
                className="mt-1 w-48 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
              >
                {providerOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-400" htmlFor="wave-capacity">
                Wave capacity (hrs)
              </label>
              <input
                id="wave-capacity"
                type="number"
                min={4}
                max={40}
                value={maxHoursPerWave}
                onChange={(event) => {
                  const next = Number(event.target.value);
                  setMaxHoursPerWave(Number.isNaN(next) ? 16 : Math.min(Math.max(next, 4), 40));
                }}
                className="mt-1 w-32 rounded-lg border border-slate-300 px-3 py-2 text-right text-sm font-medium text-slate-700 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30"
              />
            </div>
            <button
              type="button"
              onClick={() => setDarkMode((previous) => !previous)}
              className="flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-600 dark:text-slate-200 dark:hover:bg-slate-700"
            >
              {darkMode ? (
                <>
                  <Sun className="h-4 w-4" /> Light
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4" /> Dark
                </>
              )}
            </button>
          </div>
        </header>

        {aiNotice ? (
          <div className="flex items-start justify-between rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-700">
            <span>{aiNotice}</span>
            <button
              type="button"
              onClick={() => setAINotice(null)}
              className="ml-4 rounded bg-amber-200/40 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-amber-700"
            >
              Dismiss
            </button>
          </div>
        ) : null}

        <section className="grid gap-4 md:grid-cols-4">
          <Card title="Findings scored">
            <p className="text-3xl font-semibold text-slate-900 dark:text-white">{totalFindings}</p>
            <p className="text-xs text-slate-500 dark:text-slate-300">Demo dataset auto-loaded.</p>
          </Card>
          <Card title="High priority">
            <p className="text-3xl font-semibold text-slate-900 dark:text-white">{highPriorityTotal}</p>
            <p className="text-xs text-slate-500 dark:text-slate-300">
              {criticalCount} critical • {highPriorityTotal - criticalCount} high
            </p>
          </Card>
          <Card title="Plan readiness">
            <p className="text-3xl font-semibold text-slate-900 dark:text-white">{readinessLabel}</p>
            <p className="text-xs text-slate-500 dark:text-slate-300">Optimised for {maxHoursPerWave}h capacity.</p>
          </Card>
          <Card title="Compliance boost">
            <p className="text-3xl font-semibold text-slate-900 dark:text-white">{complianceLabel}</p>
            <p className="text-xs text-slate-500 dark:text-slate-300">Estimated CIS coverage uplift.</p>
          </Card>
        </section>

        <section className="rounded-2xl border border-dashed border-brand/40 bg-white/80 p-5 text-sm text-slate-600 dark:border-brand/60 dark:bg-slate-800/60 dark:text-slate-200">
          <p className="font-medium text-brand-dark dark:text-brand">Analyst hint</p>
          <p className="mt-1 text-slate-500 dark:text-slate-300">{intentHint}</p>
        </section>

        {feedbackNotice ? (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-xs text-emerald-700">
            {feedbackNotice}
          </div>
        ) : null}

        {isLoading ? (
          <Card title="Loading intelligence">
            <p className="h-48 text-sm text-slate-500">Fetching analytics from the API…</p>
          </Card>
        ) : hasError ? (
          <Card title="Unable to load data">
            <p className="text-sm text-slate-500">Check that the FastAPI server is running on port 8000.</p>
          </Card>
        ) : (
          <section className="space-y-6">
            {activeView === "import" ? <ImportView sampleFindings={findingsQuery.data} /> : null}
            {activeView === "plan" ? (
              <>
                <PlanView plan={wavesQuery.data} onFeedback={handleFeedback} />
                <NarrativesView scores={scoresQuery.data?.findings} />
              </>
            ) : null}
            {activeView === "compliance" ? <ComplianceView data={controlsQuery.data} /> : null}
            {activeView === "reports" ? <ReportsView summary={summaryQuery.data ?? undefined} /> : null}
            {activeView === "copilot" ? (
              <CopilotView providerId={aiProvider} providerLabel={activeProviderLabel} />
            ) : null}
          </section>
        )}
      </main>
    </div>
  );
}
