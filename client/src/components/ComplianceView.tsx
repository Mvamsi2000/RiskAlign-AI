import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchCompliance, ControlMapping } from "../api/client";
import { Finding } from "../data/sampleFindings";

interface Props {
  findings: Finding[];
}

export function ComplianceView({ findings }: Props) {
  const cves = useMemo(() => findings.map((finding) => finding.cve).filter(Boolean) as string[], [findings]);

  const { data, isLoading, error } = useQuery({
    queryKey: ["compliance", cves],
    queryFn: () => fetchCompliance(cves),
    enabled: cves.length > 0
  });

  if (cves.length === 0) {
    return <p>No CVEs present in the dataset to map against controls.</p>;
  }

  if (isLoading) {
    return <p>Loading control mappings…</p>;
  }

  if (error) {
    return <p>Unable to load control mappings. Please ensure the backend is running.</p>;
  }

  return (
    <div className="card">
      <h3>Control coverage</h3>
      {Object.entries(data?.mappings ?? {}).map(([cve, controls]) => (
        <div key={cve}>
          <h4>{cve}</h4>
          <ul>
            {(controls as ControlMapping[]).map((control) => (
              <li key={control.control}>
                <strong>{control.control}</strong> — {control.title}
                <br />
                <small>{control.description}</small>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
