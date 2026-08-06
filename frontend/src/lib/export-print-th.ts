/**
 * Thai PDF Export — Mobile-friendly approach.
 *
 * Instead of window.open (blocked on mobile), this:
 * 1. Stores the result in sessionStorage
 * 2. Navigates to /print page (same tab)
 * 3. /print page renders styled Thai document
 * 4. User taps "บันทึก PDF" → browser print/share
 * 5. "กลับ" returns to calculator
 *
 * Works on: iOS Safari, Chrome Android, all desktop browsers.
 */

import type { CalculationResult } from "./types";

export function exportCalculationPrintTH(result: CalculationResult) {
  // Store result for the print page to read
  sessionStorage.setItem("print-result", JSON.stringify(result));
  // Navigate to print page (works on mobile — no popup)
  window.location.href = "/print";
}
