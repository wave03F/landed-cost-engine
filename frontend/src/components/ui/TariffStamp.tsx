/**
 * TariffStamp — SVG circular stamp representing a tariff layer.
 *
 * Based on real customs stamp designs:
 * - Outer circle: dashed stroke (r=90)
 * - Inner circle: solid stroke (r=80-82)
 * - 3 lines of centered serif text
 *
 * Reference SVGs preserved as comments at bottom of file.
 */

import type { TariffType } from "@/lib/types";

// =============================================================================
// Config
// =============================================================================

const COLOR_MAP: Record<TariffType, string> = {
  MFN: "#3D5166",
  SECTION_301: "#B8863B",
  SECTION_232: "#8C6D46",
  IEEPA: "#C0392B",
};

const INACTIVE_COLOR = "#B7BEC7";

const TEXT_MAP: Record<TariffType, [string, string]> = {
  MFN: ["CUSTOMS", "MFN DUTY"],
  SECTION_301: ["TRADE REMEDY", "SECTION 301"],
  SECTION_232: ["NATIONAL SECURITY", "SECTION 232"],
  IEEPA: ["RECIPROCAL", "IEEPA"],
};

const SHORT_LABEL: Record<TariffType, string> = {
  MFN: "MFN",
  SECTION_301: "301",
  SECTION_232: "232",
  IEEPA: "IEEPA",
};

// =============================================================================
// Props
// =============================================================================

interface TariffStampProps {
  tariffType: TariffType;
  rate?: number | null;
  applied?: boolean;
  size?: "full" | "compact";
  /** Index used for deterministic rotation (avoids random flicker on re-render) */
  index?: number;
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export function TariffStamp({
  tariffType,
  rate,
  applied = true,
  size = "full",
  index = 0,
  className = "",
}: TariffStampProps) {
  const color = applied ? COLOR_MAP[tariffType] : INACTIVE_COLOR;
  const [line1, line2] = TEXT_MAP[tariffType];
  const line3 = applied && rate != null ? `${(rate * 100).toFixed(1)}%` : "N/A";
  const shortLabel = SHORT_LABEL[tariffType];

  // Deterministic rotation based on index: range [-12, 12] degrees
  const rotation = size === "full" ? ((index * 7 + 3) % 25) - 12 : 0;

  const accessibleTitle = `${line1} ${line2} tariff stamp, ${applied ? "applied" : "not applied"}`;

  // Compact: small circle with abbreviation only
  if (size === "compact") {
    return (
      <svg
        width="32"
        height="32"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label={accessibleTitle}
        className={`${className} ${applied ? "" : "opacity-40"}`}
      >
        <title>{accessibleTitle}</title>
        <circle cx="100" cy="100" r="90" fill="none" stroke={color} strokeWidth="6" strokeDasharray="8,4" />
        <circle cx="100" cy="100" r="78" fill="none" stroke={color} strokeWidth="3" />
        <text
          x="50%"
          y="55%"
          textAnchor="middle"
          dominantBaseline="middle"
          fontFamily="serif"
          fontWeight="bold"
          fontSize="52"
          fill={color}
        >
          {shortLabel}
        </text>
      </svg>
    );
  }

  // Full size stamp
  return (
    <svg
      width="128"
      height="128"
      viewBox="0 0 200 200"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label={accessibleTitle}
      className={`${className} ${applied ? "" : "opacity-40"}`}
      style={{ transform: `rotate(${rotation}deg)` }}
    >
      <title>{accessibleTitle}</title>
      {/* Outer dashed circle */}
      <circle
        cx="100"
        cy="100"
        r="90"
        fill="none"
        stroke={color}
        strokeWidth="4"
        strokeDasharray="8,4"
      />
      {/* Inner solid circle */}
      <circle
        cx="100"
        cy="100"
        r="80"
        fill="none"
        stroke={color}
        strokeWidth="2"
      />
      {/* Line 1: category/agency */}
      <text
        x="50%"
        y="40%"
        textAnchor="middle"
        fontFamily="serif"
        fontWeight="bold"
        fontSize="18"
        fill={color}
      >
        {line1}
      </text>
      {/* Line 2: tariff name (largest) */}
      <text
        x="50%"
        y="58%"
        textAnchor="middle"
        fontFamily="serif"
        fontWeight="bold"
        fontSize={line2.length > 10 ? "22" : "28"}
        fill={color}
      >
        {line2}
      </text>
      {/* Line 3: rate or N/A */}
      <text
        x="50%"
        y="76%"
        textAnchor="middle"
        fontFamily="serif"
        fontSize="16"
        fill={color}
      >
        {line3}
      </text>
    </svg>
  );
}

// =============================================================================
// Reference SVGs (DO NOT DELETE — original designs)
// =============================================================================

/*
MFN Duty Original:
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="90" fill="none" stroke="#B8863B" stroke-width="4" stroke-dasharray="8,4" />
  <circle cx="100" cy="100" r="80" fill="none" stroke="#B8863B" stroke-width="2" />
  <text x="50%" y="45%" text-anchor="middle" font-family="serif" font-weight="bold" font-size="20" fill="#B8863B">CUSTOMS</text>
  <text x="50%" y="60%" text-anchor="middle" font-family="serif" font-weight="bold" font-size="28" fill="#B8863B">MFN DUTY</text>
  <text x="50%" y="75%" text-anchor="middle" font-family="serif" font-size="16" fill="#B8863B">APPROVED</text>
</svg>

Section 301 Original:
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="90" fill="none" stroke="#C0392B" stroke-width="4" stroke-dasharray="10,5" />
  <circle cx="100" cy="100" r="82" fill="none" stroke="#C0392B" stroke-width="1" />
  <text x="50%" y="40%" text-anchor="middle" font-family="serif" font-weight="bold" font-size="18" fill="#C0392B">SECTION 301</text>
  <text x="50%" y="60%" text-anchor="middle" font-family="serif" font-weight="bold" font-size="32" fill="#C0392B">TARIFF</text>
  <text x="50%" y="80%" text-anchor="middle" font-family="serif" font-size="14" fill="#C0392B">TRADE REMEDY</text>
</svg>
*/
