import { useState } from "react";

const initialNarratives = [
  {
    title: "Executive Summary",
    content:
      "RiskAlign-AI highlights a downward trend in residual risk driven by identity modernization.",
    author: "Risk Office"
  },
  {
    title: "Security Operations",
    content: "Analyst coverage increased 20% with automated playbooks.",
    author: "SOC Lead"
  }
];

function Narratives() {
  const [narratives] = useState(initialNarratives);

  return (
    <div>
      <h1>Narrative Workspace</h1>
      <p>Craft human-readable stories that align stakeholders and decision-makers.</p>
      {narratives.map((narrative) => (
        <article key={narrative.title}>
          <h2>{narrative.title}</h2>
          <p>{narrative.content}</p>
          <p>
            <strong>Author:</strong> {narrative.author}
          </p>
        </article>
      ))}
    </div>
  );
}

export default Narratives;
