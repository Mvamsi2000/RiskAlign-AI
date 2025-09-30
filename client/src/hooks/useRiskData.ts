import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import {
  AIProviderId,
  ImpactEstimateResponse,
  MapControlsResponse,
  computeScores,
  estimateImpact,
  fetchSampleFindings,
  generateSummary,
  mapControls,
  optimizePlan
} from "../lib/api";

export function useRiskData(maxHoursPerWave: number, aiProvider: AIProviderId) {
  const findingsQuery = useQuery({
    queryKey: ["findings", aiProvider],
    queryFn: fetchSampleFindings
  });

  const scoresQuery = useQuery({
    queryKey: ["scores", findingsQuery.data, aiProvider],
    enabled: Boolean(findingsQuery.data?.length),
    queryFn: () => computeScores(findingsQuery.data ?? [])
  });

  const wavesQuery = useQuery({
    queryKey: ["waves", scoresQuery.data, maxHoursPerWave, aiProvider],
    enabled: Boolean(scoresQuery.data?.findings.length),
    queryFn: () => optimizePlan(scoresQuery.data?.findings ?? [], maxHoursPerWave)
  });

  const controlsQuery = useQuery({
    queryKey: ["controls", findingsQuery.data, aiProvider],
    enabled: Boolean(findingsQuery.data?.length),
    queryFn: () => mapControls(findingsQuery.data ?? [])
  });

  const impactQuery = useQuery({
    queryKey: ["impact", scoresQuery.data, wavesQuery.data, aiProvider],
    enabled: Boolean(scoresQuery.data?.findings.length && wavesQuery.data?.waves.length),
    queryFn: () => estimateImpact(scoresQuery.data?.findings ?? [], wavesQuery.data?.waves ?? [])
  });

  const summaryQuery = useQuery({
    queryKey: ["summary", scoresQuery.data, wavesQuery.data, impactQuery.data, controlsQuery.data, aiProvider],
    enabled: Boolean(scoresQuery.data?.findings.length && wavesQuery.data?.waves.length && impactQuery.data),
    queryFn: () =>
      generateSummary({
        findings: scoresQuery.data?.findings ?? [],
        waves: wavesQuery.data?.waves ?? [],
        impact: impactQuery.data as ImpactEstimateResponse,
        mapping: controlsQuery.data as MapControlsResponse
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
    scoresQuery,
    wavesQuery,
    controlsQuery,
    impactQuery,
    summaryQuery,
    priorityCards
  };
}
