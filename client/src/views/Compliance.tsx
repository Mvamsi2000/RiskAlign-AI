import { Card } from "../components/Card";
import type { MapControlsResponse } from "../lib/api";

interface ComplianceProps {
  data?: MapControlsResponse;
}

export function ComplianceView({ data }: ComplianceProps) {
  if (!data || data.mappings.length === 0) {
    return <Card title="No mapped controls">Add CVE identifiers to see CIS coverage.</Card>;
  }

  return (
    <Card
      title="Mapped controls"
      description={`Coverage ${data.coverage.toFixed(1)}% across ${data.unique_controls.length} controls.`}
    >
      <div className="overflow-hidden rounded-lg border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Control</th>
              <th className="px-4 py-2 text-left font-medium text-slate-600">CVE</th>
              <th className="px-4 py-2 text-left font-medium text-slate-600">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.mappings.map((item) => (
              <tr key={`${item.control}-${item.cve}`}>
                <td className="px-4 py-2 font-medium text-slate-800">{item.control}</td>
                <td className="px-4 py-2 text-slate-600">{item.cve}</td>
                <td className="px-4 py-2 text-slate-600">{item.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.unmapped.length ? (
        <p className="mt-3 text-xs text-slate-500">Unmapped CVEs: {data.unmapped.join(", ")}</p>
      ) : null}
    </Card>
  );
}
