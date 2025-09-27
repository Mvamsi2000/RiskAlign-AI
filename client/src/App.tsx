import { useState } from "react";
import Plan from "./pages/Plan";
import Compliance from "./pages/Compliance";
import Narratives from "./pages/Narratives";
import Copilot from "./pages/Copilot";
import "./App.css";

type TabKey = "plan" | "compliance" | "narratives" | "copilot";

type Tab = {
  key: TabKey;
  label: string;
  component: JSX.Element;
};

const tabs: Tab[] = [
  { key: "plan", label: "Plan", component: <Plan /> },
  { key: "compliance", label: "Compliance", component: <Compliance /> },
  { key: "narratives", label: "Narratives", component: <Narratives /> },
  { key: "copilot", label: "Copilot", component: <Copilot /> }
];

function App() {
  const [activeTab, setActiveTab] = useState<TabKey>("plan");

  return (
    <div className="app-container">
      <nav className="tab-nav" aria-label="Primary">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            className={`tab-button${tab.key === activeTab ? " active" : ""}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </nav>
      <section className="tab-panel" role="tabpanel">
        {tabs.find((tab) => tab.key === activeTab)?.component}
      </section>
    </div>
  );
}

export default App;
