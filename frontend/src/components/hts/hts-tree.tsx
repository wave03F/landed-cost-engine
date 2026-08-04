"use client";

import type { HTSCode } from "@/lib/types";

/**
 * HTSTree — Hierarchical display of HTS codes.
 *
 * Shows chapter → heading → subheading tree structure.
 * Expandable/collapsible nodes.
 *
 * Props:
 * - codes: HTSCode[]
 * - onSelect: (code: HTSCode) => void
 */

interface HTSTreeProps {
  codes: HTSCode[];
  onSelect: (code: HTSCode) => void;
}

export function HTSTree({ codes, onSelect }: HTSTreeProps) {
  return (
    <div>
      {/* TODO: Tree view with chapter/heading/subheading nesting */}
    </div>
  );
}
