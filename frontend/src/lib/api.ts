/**
 * API client layer for the Landed Cost Engine backend.
 *
 * All requests go through the `apiFetch` wrapper which:
 * - Prepends NEXT_PUBLIC_API_URL
 * - Adds X-API-Key header
 * - Throws typed errors on non-2xx responses
 */

import type {
  HTSCode,
  HTSCodeCreate,
  TariffRule,
  TariffRuleCreate,
  TariffRuleUpdate,
  Exclusion,
  ExclusionCreate,
  FXRate,
  FXRateCreate,
  CalculationRequest,
  CalculationResult,
  CalculationLog,
} from "./types";

// =============================================================================
// Base fetch wrapper
// =============================================================================

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? "";

export class ApiRequestError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
  }
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
    ...(options.headers as Record<string, string> | undefined),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let code = "UNKNOWN_ERROR";
    let message = `Request failed with status ${response.status}`;

    try {
      const body = await response.json();
      if (body.detail) {
        message = body.detail;
        code = "API_ERROR";
      } else if (body.error) {
        code = body.error.code ?? code;
        message = body.error.message ?? message;
      }
    } catch {
      // Response body not JSON — use default message
    }

    throw new ApiRequestError(response.status, code, message);
  }

  return response.json() as Promise<T>;
}

// =============================================================================
// Calculation
// =============================================================================

export async function calculateLandedCost(
  data: CalculationRequest
): Promise<CalculationResult> {
  return apiFetch<CalculationResult>("/calculate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// =============================================================================
// HTS Codes
// =============================================================================

export async function searchHTSCodes(
  query?: string,
  level?: string
): Promise<HTSCode[]> {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  if (level) params.set("level", level);
  const qs = params.toString();
  return apiFetch<HTSCode[]>(`/hts-codes${qs ? `?${qs}` : ""}`);
}

export async function getHTSCode(code: string): Promise<HTSCode> {
  return apiFetch<HTSCode>(`/hts-codes/${encodeURIComponent(code)}`);
}

export async function createHTSCode(data: HTSCodeCreate): Promise<HTSCode> {
  return apiFetch<HTSCode>("/hts-codes", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// =============================================================================
// Tariff Rules
// =============================================================================

export async function listTariffRules(
  tariffType?: string,
  htsCode?: string
): Promise<TariffRule[]> {
  const params = new URLSearchParams();
  if (tariffType) params.set("tariff_type", tariffType);
  if (htsCode) params.set("hts_code", htsCode);
  const qs = params.toString();
  return apiFetch<TariffRule[]>(`/tariff-rules${qs ? `?${qs}` : ""}`);
}

export async function createTariffRule(
  data: TariffRuleCreate
): Promise<TariffRule> {
  return apiFetch<TariffRule>("/tariff-rules", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateTariffRule(
  ruleId: string,
  data: TariffRuleUpdate
): Promise<TariffRule> {
  return apiFetch<TariffRule>(`/tariff-rules/${encodeURIComponent(ruleId)}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// =============================================================================
// Exclusions
// =============================================================================

export async function listExclusions(htsCode?: string): Promise<Exclusion[]> {
  const params = new URLSearchParams();
  if (htsCode) params.set("hts_code", htsCode);
  const qs = params.toString();
  return apiFetch<Exclusion[]>(`/exclusions${qs ? `?${qs}` : ""}`);
}

export async function createExclusion(
  data: ExclusionCreate
): Promise<Exclusion> {
  return apiFetch<Exclusion>("/exclusions", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// =============================================================================
// FX Rates
// =============================================================================

export async function listFXRates(
  fromCurrency?: string,
  toCurrency?: string,
  dateFrom?: string,
  dateTo?: string
): Promise<FXRate[]> {
  const params = new URLSearchParams();
  if (fromCurrency) params.set("from_currency", fromCurrency);
  if (toCurrency) params.set("to_currency", toCurrency);
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  const qs = params.toString();
  return apiFetch<FXRate[]>(`/fx-rates${qs ? `?${qs}` : ""}`);
}

export async function createFXRate(data: FXRateCreate): Promise<FXRate> {
  return apiFetch<FXRate>("/fx-rates", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// =============================================================================
// Calculations (Audit Trail)
// =============================================================================

export async function listCalculations(
  htsCode?: string,
  limit?: number,
  offset?: number
): Promise<CalculationLog[]> {
  const params = new URLSearchParams();
  if (htsCode) params.set("hts_code", htsCode);
  if (limit) params.set("limit", String(limit));
  if (offset) params.set("offset", String(offset));
  const qs = params.toString();
  return apiFetch<CalculationLog[]>(`/calculations${qs ? `?${qs}` : ""}`);
}

export async function getCalculation(id: string): Promise<CalculationLog> {
  return apiFetch<CalculationLog>(
    `/calculations/${encodeURIComponent(id)}`
  );
}

// =============================================================================
// Health
// =============================================================================

export async function checkHealth(): Promise<{ status: string; service: string }> {
  return apiFetch<{ status: string; service: string }>("/health");
}
