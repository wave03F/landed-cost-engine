/**
 * TypeScript type definitions matching the backend API responses.
 * These mirror the Pydantic schemas from the FastAPI backend.
 */

// =============================================================================
// HTS Codes
// =============================================================================

export interface HTSCode {
  id: string;
  code: string;
  level: "chapter" | "heading" | "subheading";
  description: string;
  parent_code: string | null;
}

export interface HTSCodeCreate {
  code: string;
  description: string;
  parent_code?: string | null;
}

// =============================================================================
// Tariff Rules
// =============================================================================

export type TariffType = "MFN" | "SECTION_301" | "SECTION_232" | "IEEPA" | "AD_CVD" | "MPF" | "HMF";

export interface TariffRule {
  id: string;
  tariff_type: TariffType;
  hts_code_pattern: string;
  origin_country: string;
  rate: number;
  effective_from: string; // ISO date
  effective_to: string | null;
  stacks_with: string[];
  mutually_exclusive_with: string[];
  description: string;
  source_reference: string;
}

export interface TariffRuleCreate {
  tariff_type: TariffType;
  hts_code_pattern: string;
  origin_country?: string;
  rate: number;
  effective_from: string;
  effective_to?: string | null;
  stacks_with?: string[];
  mutually_exclusive_with?: string[];
  description?: string;
  source_reference?: string;
}

export interface TariffRuleUpdate {
  rate?: number | null;
  effective_to?: string | null;
  stacks_with?: string[] | null;
  mutually_exclusive_with?: string[] | null;
  description?: string | null;
  source_reference?: string | null;
}

// =============================================================================
// Exclusions
// =============================================================================

export interface Exclusion {
  id: string;
  hts_code: string;
  tariff_type: TariffType;
  origin_country: string;
  effective_from: string;
  effective_to: string | null;
  description: string;
  source_reference: string;
}

export interface ExclusionCreate {
  hts_code: string;
  tariff_type: TariffType;
  origin_country?: string;
  effective_from: string;
  effective_to?: string | null;
  description?: string;
  source_reference?: string;
}

// =============================================================================
// FX Rates
// =============================================================================

export interface FXRate {
  id: string;
  from_currency: string;
  to_currency: string;
  rate: number;
  date: string; // ISO date
}

export interface FXRateCreate {
  from_currency?: string;
  to_currency?: string;
  rate: number;
  date: string;
}

// =============================================================================
// Calculation (request & response)
// =============================================================================

export interface CalculationRequest {
  hts_code: string;
  invoice_value_cny?: number | null;
  invoice_value_usd?: number | null;
  origin_country?: string;
  import_date: string; // ISO date
  freight_usd?: number;
  insurance_usd?: number;
}

export interface TariffBreakdownItem {
  type: TariffType;
  rate: number | null;
  amount_usd: number | null;
  applied: boolean;
  reason: string | null;
  rule_id: string | null;
}

export interface ExclusionApplied {
  exclusion_id: string;
  tariff_type: string;
  description: string;
}

export interface FXRateUsed {
  from_currency: string;
  to_currency: string;
  rate: number;
  date: string;
}

export interface CalculationResult {
  calculation_id: string;
  hts_code: string;
  import_date: string;
  origin_country: string;
  de_minimis_applied: boolean;
  invoice_value_usd: number;
  customs_value_usd: number;
  total_duty_usd: number;
  tariff_breakdown: TariffBreakdownItem[];
  fees: { mpf_usd: number; hmf_usd: number; total_fees_usd: number } | null;
  fta_applied: string | null;
  total_fees_usd: number;
  landed_cost_usd: number;
  exclusions_applied: ExclusionApplied[];
  fx_rate_used: FXRateUsed | null;
}

// =============================================================================
// Calculation Log (audit trail)
// =============================================================================

export interface CalculationLog {
  id: string;
  hts_code: string;
  import_date: string;
  origin_country: string;
  input_data: Record<string, unknown>;
  matched_rules: string[];
  exclusions_applied: string[];
  result_data: Record<string, unknown>;
  calculated_at: string; // ISO datetime
}

// =============================================================================
// API Error
// =============================================================================

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}
