import { useState } from "react";

import { Card } from "../components/Card";
import type { Finding, IngestResponse } from "../lib/api";
import { uploadArtifact } from "../lib/api";

interface ImportViewProps {
  sampleFindings?: Finding[];
}

export function ImportView({ sampleFindings }: ImportViewProps) {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState<IngestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const response = await uploadArtifact(file);
      setPreview(response);
    } catch (err) {
      setError("Unable to ingest the file. Ensure the backend is running.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card
        title="Upload artifact"
        description="Drop a Nessus XML, CSV, or log file to see how the pipeline normalises it into MCP envelopes."
      >
        <label className="mt-2 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center text-sm text-slate-500 hover:bg-slate-100">
          <input type="file" className="hidden" onChange={handleUpload} accept=".csv,.nessus,.xml,.txt,.log" />
          <span className="font-medium text-slate-700">{uploading ? "Uploading…" : "Select artifact"}</span>
          <span className="text-xs text-slate-400">Formats: Nessus XML, vulnerability CSV, or security logs.</span>
        </label>
        {error ? <p className="mt-3 text-xs text-rose-500">{error}</p> : null}
      </Card>

      {preview ? (
        <Card title="Ingestion preview" description={`Detected ${preview.count} findings.`}>
          <pre className="overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-900/90 p-4 text-xs text-slate-100">
            {JSON.stringify(preview.sample, null, 2)}
          </pre>
        </Card>
      ) : null}

      <Card
        title="Demo dataset"
        description="Loaded automatically on every page so you can explore the experience instantly."
      >
        <p className="text-sm text-slate-500">
          {sampleFindings?.length ?? 0} findings loaded from <code>server/data/samples/sample_findings.json</code>.
        </p>
        <ul className="mt-3 space-y-1 text-xs text-slate-500">
          {sampleFindings?.slice(0, 4).map((finding) => (
            <li key={finding.id} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
              <span className="font-medium text-slate-700">{finding.title}</span>
              <span className="ml-2 text-slate-400">CVSS {finding.cvss.toFixed(1)}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
