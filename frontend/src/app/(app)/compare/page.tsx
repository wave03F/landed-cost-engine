"use client";

import { useState } from "react";
import type { CalculationRequest, CalculationResult } from "@/lib/types";
import { calculateLandedCost, ApiRequestError } from "@/lib/api";
import { TariffStamp } from "@/components/ui/TariffStamp";
import { useI18n } from "@/lib/i18n";
import { exportCalculationPDF } from "@/lib/export-pdf";

const EMPTY_FORM = {
  hts_code: "",
  invoice_value_usd: "",
  import_date: new Date().toISOString().split("T")[0],
  freight_usd: "0",
  insurance_usd: "0",
  origin_country: "CN",
};

export default function ComparePage() {
  const { t } = useI18n();
  const [formA, setFormA] = useState({ ...EMPTY_FORM, hts_code: "8483.40", invoice_value_usd: "50000" });
  const [formB, setFormB] = useState({ ...EMPTY_FORM, hts_code: "8483.40", invoice_value_usd: "50000", origin_country: "MX" });
  const [resultA, setResultA] = useState<CalculationResult | null>(null);
  const [resultB, setResultB] = useState<CalculationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (side: "A" | "B") => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const setter = side === "A" ? setFormA : setFormB;
    setter((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const buildRequest = (form: typeof EMPTY_FORM): CalculationRequest => ({
        hts_code: form.hts_code,
        invoice_value_usd: parseFloat(form.invoice_value_usd) || undefined,
        import_date: form.import_date,
        origin_country: form.origin_country,
        freight_usd: parseFloat(form.freight_usd) || 0,
        insurance_usd: parseFloat(form.insurance_usd) || 0,
      });

      const [resA, resB] = await Promise.all([
        calculateLandedCost(buildRequest(formA)),
        calculateLandedCost(buildRequest(formB)),
      ]);
      setResultA(resA);
      setResultB(resB);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Calculation failed");
    } finally {
      setIsLoading(false);
    }
  };

  const fmt = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD" });
  const pct = (a: number, b: number) => {
    if (b === 0) return "—";
    const diff = ((a - b) / b) * 100;
    return `${diff > 0 ? "+" : ""}${diff.toFixed(1)}%`;
  };

  const renderForm = (side: "A" | "B", form: typeof EMPTY_FORM) => (
    <div className="flex-1">
      <h3 className="font-label-caps text-label-caps text-primary uppercase mb-3">
        {side === "A" ? "Product A" : "Product B"}
      </h3>
      <div className="space-y-3">
        <input name="hts_code" value={form.hts_code} onChange={handleChange(side)} placeholder="HTS Code"
          className="w-full bg-transparent border border-steel-blue/40 p-2 font-code-sm text-code-sm text-primary rounded-none uppercase" />
        <input name="invoice_value_usd" type="number" value={form.invoice_value_usd} onChange={handleChange(side)} placeholder="Value USD"
          className="w-full bg-transparent border border-steel-blue/40 p-2 font-code-sm text-code-sm text-primary rounded-none" />
        <input name="import_date" type="date" value={form.import_date} onChange={handleChange(side)}
          className="w-full bg-transparent border border-steel-blue/40 p-2 font-code-sm text-code-sm text-primary rounded-none" />
        <select name="origin_country" value={form.origin_country} onChange={handleChange(side)}
          className="w-full bg-transparent border border-steel-blue/40 p-2 font-code-sm text-code-sm text-primary rounded-none">
          <option value="CN">China (CN)</option>
          <option value="VN">Vietnam (VN)</option>
          <option value="MX">Mexico (MX) — USMCA</option>
          <option value="CA">Canada (CA) — USMCA</option>
          <option value="DE">Germany (DE)</option>
          <option value="JP">Japan (JP)</option>
        </select>
      </div>
    </div>
  );

  const renderResult = (result: CalculationResult | null, label: string) => {
    if (!result) return null;
    return (
      <div className="flex-1 p-4 border border-steel-blue/20 bg-surface-container-low/30">
        <p className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-2">{label}</p>
        <div className="font-display-lg text-[28px] text-duty-red font-bold mb-3">
          {fmt(result.landed_cost_usd)}
        </div>
        <div className="space-y-1 font-code-sm text-[12px]">
          <div className="flex justify-between">
            <span>Customs Value</span>
            <span>{fmt(result.customs_value_usd)}</span>
          </div>
          <div className="flex justify-between text-duty-red">
            <span>Total Duty</span>
            <span>{fmt(result.total_duty_usd)}</span>
          </div>
          {result.fees && (
            <div className="flex justify-between">
              <span>Fees</span>
              <span>{fmt(result.fees.total_fees_usd)}</span>
            </div>
          )}
          {result.fta_applied && (
            <div className="text-[11px] text-green-700 mt-1">FTA: {result.fta_applied}</div>
          )}
        </div>
        {/* Stamps */}
        <div className="flex flex-wrap gap-1 mt-3">
          {result.tariff_breakdown
            .filter((i) => i.type !== "MPF" && i.type !== "HMF" && i.applied)
            .map((item, i) => (
              <TariffStamp key={i} tariffType={item.type} rate={item.rate} applied={item.applied} size="compact" index={i} />
            ))}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-manifest-paper text-on-surface noise-bg border border-steel-blue/30 shadow-[0_10px_30px_rgba(0,0,0,0.5)] rounded-sm relative overflow-hidden">
      <div className="h-2 bg-steel-blue w-full flex-shrink-0" />
      <div className="px-8 py-6 border-b border-steel-blue/20 bg-surface-container-low/50">
        <p className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase tracking-widest">
          Side-by-Side Analysis
        </p>
        <h2 className="font-headline-lg text-headline-lg text-primary">Compare Products</h2>
      </div>

      <form onSubmit={handleCompare} className="p-8">
        {/* Two forms side by side */}
        <div className="flex gap-6 mb-6">
          {renderForm("A", formA)}
          <div className="w-[1px] bg-steel-blue/20 self-stretch" />
          {renderForm("B", formB)}
        </div>

        {error && (
          <div className="bg-error-container text-on-error-container p-3 rounded-sm text-code-sm mb-4">{error}</div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-ink-navy text-on-primary font-label-caps text-label-caps py-4 uppercase tracking-widest hover:bg-opacity-90 transition-all disabled:opacity-50 flex justify-center items-center gap-2"
        >
          <span className="material-symbols-outlined text-[18px]">compare_arrows</span>
          {isLoading ? "Comparing..." : "Compare Landed Costs"}
        </button>
      </form>

      {/* Results */}
      {resultA && resultB && (
        <div className="px-8 pb-8">
          <div className="flex gap-6 mb-6">
            {renderResult(resultA, "Product A")}
            {renderResult(resultB, "Product B")}
          </div>

          {/* Difference summary */}
          <div className="border-t-2 border-primary pt-4 mt-4">
            <div className="flex justify-between items-center">
              <span className="font-label-caps text-label-caps text-primary uppercase">Cost Difference</span>
              <span className={`font-display-lg text-[24px] font-bold ${
                resultA.landed_cost_usd > resultB.landed_cost_usd ? "text-duty-red" : "text-green-700"
              }`}>
                {fmt(Math.abs(resultA.landed_cost_usd - resultB.landed_cost_usd))}
                <span className="text-[14px] ml-2">
                  ({pct(resultA.landed_cost_usd, resultB.landed_cost_usd)} A vs B)
                </span>
              </span>
            </div>
            <p className="text-[12px] text-on-surface-variant mt-2">
              {resultA.landed_cost_usd > resultB.landed_cost_usd
                ? "Product B is cheaper to import."
                : resultA.landed_cost_usd < resultB.landed_cost_usd
                ? "Product A is cheaper to import."
                : "Both products have the same landed cost."}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
