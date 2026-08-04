"use client";

import type { CalculationResult } from "@/lib/types";

/**
 * ResultCard — Displays the calculation result with full tariff breakdown.
 *
 * Shows:
 * - Summary: invoice → customs value → total duty → landed cost
 * - Breakdown table: each tariff layer (type, rate, amount, applied/excluded)
 * - Exclusions applied (if any)
 * - FX rate used (if currency conversion happened)
 * - Audit ID for reference
 *
 * Props:
 * - result: CalculationResult | null
 */

interface ResultCardProps {
  result: CalculationResult | null;
}

export function ResultCard({ result }: ResultCardProps) {
  if (!result) return null;

  return (
    <div>
      {/* TODO: Cost summary (invoice → customs → duty → landed cost) */}
      {/* TODO: Tariff breakdown table */}
      {/* TODO: Exclusions section */}
      {/* TODO: FX rate info */}
      {/* TODO: Calculation ID (small, for audit reference) */}
    </div>
  );
}
