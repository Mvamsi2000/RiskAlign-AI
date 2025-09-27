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
    queryKey: ["controls", findingsQuery.data?.map((item) => item.cve)],
    enabled: Boolean(findingsQuery.data?.some((item) => item.cve)),
    queryFn: () =>
      mapControls(
        (findingsQuery.data ?? [])
          .map((item) => item.cve)
          .filter((cve): cve is string => Boolean(cve))
      )
  });

  const impactQuery = useQuery({
    queryKey: ["impact", findingsQuery.data],
    enabled: Boolean(findingsQuery.data?.length),
    queryFn: () => estimateImpact(findingsQuery.data ?? [])
  });

  const summaryQuery = useQuery({
    queryKey: ["summary", findingsQuery.data],
    enabled: Boolean(findingsQuery.data?.length),
    queryFn: () => generateSummary(findingsQuery.data ?? [])
  });

  const priorityCards = useMemo(() => {
    const counts = scoresQuery.data?.summary.counts_by_priority ?? {};
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
