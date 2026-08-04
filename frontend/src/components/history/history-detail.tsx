"use client";

import type { CalculationLog } from "@/lib/types";

/**
 * HistoryDetail — Expanded detail view of a single past calculation.
 *
 * Shows:
 * - Input data used
 * - Rules that matched
 * - Exclusions applied
 * - Full result data
 * - Timestamp
 *
 * Props:
 * - log: CalculationLog | null
 */

interface HistoryDetailProps {
  log: CalculationLog | null;
}

export function HistoryDetail({ log }: HistoryDetailProps) {
  if (!log) return null;

  return (
    <div>
      {/* TODO: Input summary */}
      {/* TODO: Matched rules list */}
      {/* TODO: Exclusions list */}
      {/* TODO: Result breakdown */}
      {/* TODO: Timestamp */}
    </div>
  );
}
