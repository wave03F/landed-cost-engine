"use client";

/**
 * CalculatorForm — Main calculation input form.
 *
 * Fields:
 * - HTS code (with autocomplete from /hts-codes)
 * - Invoice value (CNY or USD radio toggle)
 * - Origin country (default CN, select dropdown)
 * - Import date (date picker)
 * - Freight USD
 * - Insurance USD
 *
 * Props:
 * - onSubmit: (data: CalculationRequest) => void
 * - isLoading: boolean
 * - quickEstimate: boolean (hides freight/insurance when true)
 */

export function CalculatorForm() {
  return (
    <form>
      {/* TODO: HTS code input with autocomplete */}
      {/* TODO: Currency toggle (CNY / USD) + value input */}
      {/* TODO: Origin country select */}
      {/* TODO: Import date picker */}
      {/* TODO: Freight input (hidden in quick-estimate mode) */}
      {/* TODO: Insurance input (hidden in quick-estimate mode) */}
      {/* TODO: Submit button */}
    </form>
  );
}
