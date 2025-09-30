import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import {
  AIProviderId,
  computeScores,
  estimateImpact,
  fetchCanonicalFindings,
  generateSummary,
  mapControls,
  optimizePlan
} from "../lib/api";

export function useRiskData(
  maxHoursPerWave: number,
  aiProvider: AIProviderId,
  batchId?: string
) {
  const findingsQuery = useQuery({
    queryKey: ["canonical-findings", batchId, aiProvider],
    queryFn: () => fetchCanonicalFindings(batchId)
  });

  const canonical = findingsQuery.data;
  const findings = canonical?.findings ?? [];

  const scoresQuery = useQuery({
    queryKey: ["scores", findings, aiProvider],
    enabled: Boolean(findings.length),
    queryFn: () => computeScores(findings)
  });

  const wavesQuery = useQuery({
    queryKey: ["waves", findings, maxHoursPerWave, aiProvider],
    enabled: Boolean(findings.length),
    queryFn: () => optimizePlan(findings, maxHoursPerWave)
  });

  const controlsQuery = useQuery({
    queryKey: ["controls", findings, aiProvider],
    enabled: Boolean(findings.some((item) => item.cve)),
    queryFn: () => mapControls(findings)
  });

  const impactQuery = useQuery({
    queryKey: ["impact", findings, wavesQuery.data, aiProvider],
    enabled: Boolean(findings.length && wavesQuery.data?.waves.length),
    queryFn: () => estimateImpact(findings, wavesQuery.data?.waves ?? [])
  });

  const summaryQuery = useQuery({
    queryKey: ["summary", findings, maxHoursPerWave, aiProvider],
    enabled: Boolean(findings.length),
    queryFn: () =>
      generateSummary({
        findings,
        max_hours_per_wave: maxHoursPerWave
      })
  });

  const priorityCards = useMemo(() => {
    const counts = scoresQuery.data?.totals.by_priority ?? {};
    return Object.entries(counts).map(([priority, count]) => ({
      priority,
      count
    }));
  }, [scoresQuery.data]);

  return {
    findingsQuery,
    canonical,
    scoresQuery,
    wavesQuery,
    controlsQuery,
    impactQuery,
    summaryQuery,
    priorityCards
  };
}
