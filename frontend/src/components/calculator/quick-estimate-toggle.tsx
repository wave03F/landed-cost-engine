"use client";

/**
 * QuickEstimateToggle — Switch between full form and quick-estimate mode.
 *
 * In quick-estimate mode:
 * - Freight and insurance default to 0 (hidden)
 * - Origin defaults to CN (hidden)
 * - Import date defaults to today (hidden)
 * - Only HTS code + value shown
 *
 * Props:
 * - enabled: boolean
 * - onToggle: (enabled: boolean) => void
 */

interface QuickEstimateToggleProps {
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
}

export function QuickEstimateToggle({ enabled, onToggle }: QuickEstimateToggleProps) {
  return (
    <div>
      {/* TODO: Toggle switch with label "Quick Estimate" */}
    </div>
  );
}
