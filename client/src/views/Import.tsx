import { useCallback, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Card } from "../components/Card";
import { IngestUploadResponse, uploadIngest } from "../lib/api";

function formatNumber(value: number) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
}

export function ImportView() {
  const queryClient = useQueryClient();
  const [result, setResult] = useState<IngestUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: uploadIngest,
    onSuccess: (data) => {
      setResult(data);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ["canonical-batches"] });
      queryClient.invalidateQueries({ queryKey: ["canonical-findings"] });
    },
    onError: (cause: unknown) => {
      setError(cause instanceof Error ? cause.message : "Upload failed");
    }
  });

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files?.length) return;
      const file = files[0];
      mutation.mutate(file);
    },
    [mutation]
  );

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      handleFiles(event.dataTransfer.files);
    },
    [handleFiles]
  );

  const onBrowse = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(event.target.files);
  }, [handleFiles]);

  return (
    <Card
      title="Import findings"
      description="Drag and drop Nessus, CSV, or log files to populate canonical datasets."
    >
      <div
        onDrop={onDrop}
        onDragOver={(event) => event.preventDefault()}
        className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-100/60 px-6 py-10 text-center"
      >
        <p className="text-sm font-medium text-slate-700">Drop files here or browse</p>
        <p className="mt-2 text-xs text-slate-500">Supported: .nessus, .csv, .log</p>
        <label className="mt-4 cursor-pointer rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white shadow hover:bg-brand-dark">
          <input
            type="file"
            accept=".nessus,.xml,.csv,.log,.txt"
            onChange={onBrowse}
            className="hidden"
          />
          Browse files
        </label>
        {mutation.status === "pending" ? (
          <p className="mt-3 flex items-center gap-2 text-xs text-slate-500">
            <span className="h-2 w-2 animate-ping rounded-full bg-brand" /> Uploading…
          </p>
        ) : null}
      </div>

      {error ? <p className="mt-4 text-xs text-rose-500">{error}</p> : null}

      {result ? (
        <div className="mt-6 space-y-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-700">
            <p className="font-medium text-slate-900">Detected adapter</p>
            <p className="text-xs text-slate-500">{result.adapter_label} ({result.detected})</p>
            <div className="mt-3 grid grid-cols-3 gap-3 text-center text-xs uppercase tracking-wide text-slate-500">
              <div>
                <p className="text-lg font-semibold text-slate-900">{formatNumber(result.count)}</p>
                <p>Total items</p>
              </div>
              <div>
                <p className="text-lg font-semibold text-emerald-600">{formatNumber(result.accepted)}</p>
                <p>Accepted</p>
              </div>
              <div>
                <p className="text-lg font-semibold text-amber-600">{formatNumber(result.rejected)}</p>
                <p>Rejected</p>
              </div>
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-slate-700">Sample findings</p>
            <table className="mt-2 w-full table-fixed rounded-lg border border-slate-200 text-left text-xs text-slate-600">
              <thead className="bg-slate-100 text-slate-500">
                <tr>
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">Title</th>
                  <th className="px-3 py-2">CVE</th>
                  <th className="px-3 py-2">CVSS</th>
                  <th className="px-3 py-2">Severity</th>
                  <th className="px-3 py-2">EPSS</th>
                  <th className="px-3 py-2">KEV</th>
                </tr>
              </thead>
              <tbody>
                {result.sample.slice(0, 5).map((item) => (
                  <tr key={item.id ?? item.title} className="border-t border-slate-200">
                    <td className="truncate px-3 py-2 font-mono text-[11px]">{item.id}</td>
                    <td className="truncate px-3 py-2">{item.title}</td>
                    <td className="px-3 py-2">{item.cve ?? "—"}</td>
                    <td className="px-3 py-2">{typeof item.cvss === "number" ? item.cvss.toFixed(1) : "—"}</td>
                    <td className="px-3 py-2 capitalize">{item.severity ?? "unknown"}</td>
                    <td className="px-3 py-2">{item.epss !== undefined ? item.epss.toFixed(2) : "—"}</td>
                    <td className="px-3 py-2">{item.kev ? "Yes" : "No"}</td>
                  </tr>
                ))}
                {result.sample.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-3 py-4 text-center text-slate-400">
                      No sample findings returned from the adapter.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </Card>
  );
}
