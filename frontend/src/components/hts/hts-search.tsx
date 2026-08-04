"use client";

/**
 * HTSSearch — Search input with debounced autocomplete for HTS codes.
 *
 * Features:
 * - Debounced input (300ms)
 * - Dropdown suggestions from GET /hts-codes?q=...
 * - Shows code + description in suggestions
 * - onSelect callback when user picks a code
 *
 * Props:
 * - onSelect: (code: string) => void
 * - placeholder?: string
 */

interface HTSSearchProps {
  onSelect: (code: string) => void;
  placeholder?: string;
}

export function HTSSearch({ onSelect, placeholder }: HTSSearchProps) {
  return (
    <div>
      {/* TODO: Input field */}
      {/* TODO: Dropdown suggestions list */}
    </div>
  );
}
