import { useMemo } from "react";

const initiatives = [
  "Harden identity perimeter with conditional access",
  "Automate asset discovery across cloud environments",
  "Implement continuous vulnerability scanning"
];

function Plan() {
  const roadmap = useMemo(() => initiatives, []);

  return (
    <div>
      <h1>Strategic Plan</h1>
      <p>
        This workspace captures prioritized initiatives that align investments to
        measurable risk reduction outcomes.
      </p>
      <ol>
        {roadmap.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ol>
    </div>
  );
}

export default Plan;
