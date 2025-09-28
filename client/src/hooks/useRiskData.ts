import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import {
  computeScores,
  estimateImpact,
  fetchSampleFindings,
  generateSummary,
  mapControls,
  optimizePlan
} from "../lib/api";

export function useRiskData(maxHoursPerWave: number) {
  const findingsQuery = useQuery({
    queryKey: ["findings"],
    queryFn: fetchSampleFindings
  });

  const scoresQuery = useQuery({
    queryKey: ["scores", findingsQuery.data],
    enabled: Boolean(findingsQuery.data?.length),
    queryFn: () => computeScores(findingsQuery.data ?? [])
  });

  const wavesQuery = useQuery({
    queryKey: ["waves", findingsQuery.data, maxHoursPerWave],
    enabled: Boolean(findingsQuery.data?.length),
    queryFn: () => optimizePlan(findingsQuery.data ?? [], maxHoursPerWave)
  });

  const controlsQuery = useQuery({
    queryKey: ["controls", findingsQuery.data],
    enabled: Boolean(findingsQuery.data?.some((item) => item.cve)),
    queryFn: () => mapControls(findingsQuery.data ?? [])
  });

  const impactQuery = useQuery({
    queryKey: ["impact", findingsQuery.data, wavesQuery.data],
    enabled: Boolean(findingsQuery.data?.length && wavesQuery.data?.waves.length),
    queryFn: () => estimateImpact(findingsQuery.data ?? [], wavesQuery.data?.waves ?? [])
  });

  const summaryQuery = useQuery({
    queryKey: ["summary", findingsQuery.data, maxHoursPerWave],
    enabled: Boolean(findingsQuery.data?.length),
    queryFn: () =>
      generateSummary({
        findings: findingsQuery.data ?? [],
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
    scoresQuery,
    wavesQuery,
    controlsQuery,
    impactQuery,
    summaryQuery,
    priorityCards
  };
}
