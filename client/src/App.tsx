import { useState } from "react";
import { sampleFindings } from "./data/sampleFindings";
import { ScoreView } from "./components/ScoreView";
import { PlanView } from "./components/PlanView";
import { ComplianceView } from "./components/ComplianceView";
import { NarrativeView } from "./components/NarrativeView";

const tabs = ["Scores", "Plan", "Compliance", "Narratives"] as const;

export default function App() {
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>("Scores");

  return (
    <div className="app-shell">
      <header>
        <h1>RiskAlign-AI</h1>
        <p>Explainable, compliance-driven cyber risk decision intelligence.</p>
      </header>
      <nav>
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            className={`nav-button ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      {activeTab === "Scores" && <ScoreView findings={sampleFindings} />}
      {activeTab === "Plan" && <PlanView findings={sampleFindings} />}
      {activeTab === "Compliance" && <ComplianceView findings={sampleFindings} />}
      {activeTab === "Narratives" && <NarrativeView findings={sampleFindings} />}
    </div>
  );
}
