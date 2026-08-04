"use client";

import type { CalculationLog } from "@/lib/types";

/**
 * HistoryList — List of past calculations.
 *
 * Each item shows: date, HTS code, origin, landed cost result.
 * Click to expand/navigate to full detail.
 *
 * Props:
 * - items: CalculationLog[]
 * - onSelect: (id: string) => void
 */

interface HistoryListProps {
  items: CalculationLog[];
  onSelect: (id: string) => void;
}

export function HistoryList({ items, onSelect }: HistoryListProps) {
  return (
    <div>
      {/* TODO: Table or card list of calculation history */}
    </div>
  );
}
