"use client";

import { useState } from "react";
import type { CalculationRequest, CalculationResult } from "@/lib/types";
import { calculateLandedCost, ApiRequestError } from "@/lib/api";
import { FloatingTotal } from "@/components/calculator/floating-total";
import { TariffStamp } from "@/components/ui/TariffStamp";

export default function CalculatorPage() {
  const [quickEstimate, setQuickEstimate] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CalculationResult | null>(null);

  const [formData, setFormData] = useState({
    hts_code: "8517.12.00",
    invoice_value_usd: "125000.00",
    import_date: "2023-10-24",
    freight_usd: "4500.00",
    insurance_usd: "850.00",
    origin_country: "CN",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const request: CalculationRequest = {
        hts_code: formData.hts_code.replace(/\.00$/, ""),
        invoice_value_usd: parseFloat(formData.invoice_value_usd) || undefined,
        import_date: formData.import_date,
        origin_country: formData.origin_country,
        freight_usd: parseFloat(formData.freight_usd) || 0,
        insurance_usd: parseFloat(formData.insurance_usd) || 0,
      };
      const res = await calculateLandedCost(request);
      setResult(res);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const fmt = (n: number) =>
    n.toLocaleString("en-US", { style: "currency", currency: "USD" });

  return (
    <>
      {/* Mobile: Floating total bar */}
      <FloatingTotal total={result?.landed_cost_usd ?? null} />

      {/* Mobile: Document header */}
      <div className="mb-6 flex justify-between items-end border-b border-outline pb-2 md:hidden">
        <div>
          <h2 className="font-headline-lg text-[24px] text-on-primary">
            {quickEstimate ? "Quick Estimate" : "Full Calculator"}
          </h2>
          <p className="font-label-caps text-label-caps text-on-primary-container mt-1 uppercase">Form 7501-A</p>
        </div>
        <span className="font-code-sm text-code-sm text-secondary-fixed">REV 2.1</span>
      </div>

      {/* Desktop: Manifest paper wrapper */}
      <div className="md:bg-manifest-paper md:text-on-surface md:border md:border-steel-blue/30 md:shadow-[0_10px_30px_rgba(0,0,0,0.5)] flex flex-col md:rounded-sm relative overflow-hidden">
      {/* Red top stripe */}
      <div className="h-2 bg-duty-red w-full flex-shrink-0" />

      {/* Document Header */}
      <div className="px-8 py-6 border-b border-steel-blue/20 flex justify-between items-end flex-wrap gap-4 bg-surface-container-low/50">
        <div>
          <p className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase tracking-widest">
            Form 7501 - Entry Summary
          </p>
          <h2 className="font-headline-lg text-headline-lg text-primary">Duty Calculator</h2>
        </div>
        {/* Toggle */}
        <div className="flex items-center gap-3">
          <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Quick Estimate
          </span>
          <button
            type="button"
            onClick={() => setQuickEstimate(!quickEstimate)}
            className={`relative inline-flex h-6 w-12 items-center rounded-full transition-colors ${
              quickEstimate ? "bg-surface-container-highest" : "bg-brass"
            }`}
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white border-2 transition-transform ${
                quickEstimate ? "translate-x-1 border-surface-container-highest" : "translate-x-6 border-brass"
              }`}
            />
          </button>
          <span className="font-label-caps text-label-caps text-primary font-bold uppercase">
            Full Calculator
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col lg:flex-row">
        {/* Left: Form */}
        <div className="flex-1 border-r border-steel-blue/20 p-8 lg:max-w-[45%] bg-surface-container-low/30">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* HTS Code */}
            <div>
              <label className="block font-label-caps text-label-caps text-primary uppercase mb-2">
                HTS Code (Harmonized Tariff Schedule)
              </label>
              <input
                name="hts_code"
                value={formData.hts_code}
                onChange={handleChange}
                className="w-full bg-transparent border border-steel-blue/40 p-3 font-code-sm text-code-sm text-primary focus:border-ink-navy focus:border-b-2 focus:ring-0 transition-all rounded-none uppercase"
                placeholder="XXXX.XX.XX"
              />
            </div>

            {/* Value + Date */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block font-label-caps text-label-caps text-primary uppercase mb-2">
                  Item Value (USD)
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 font-code-sm text-on-surface-variant">$</span>
                  <input
                    name="invoice_value_usd"
                    type="number"
                    step="0.01"
                    value={formData.invoice_value_usd}
                    onChange={handleChange}
                    className="w-full bg-transparent border border-steel-blue/40 py-3 pl-8 pr-3 font-code-sm text-code-sm text-primary focus:border-ink-navy focus:border-b-2 focus:ring-0 transition-all rounded-none text-right"
                  />
                </div>
              </div>
              <div>
                <label className="block font-label-caps text-label-caps text-primary uppercase mb-2">
                  Date of Import
                </label>
                <input
                  name="import_date"
                  type="date"
                  value={formData.import_date}
                  onChange={handleChange}
                  className="w-full bg-transparent border border-steel-blue/40 p-3 font-code-sm text-code-sm text-primary focus:border-ink-navy focus:border-b-2 focus:ring-0 transition-all rounded-none"
                />
              </div>
            </div>

            {/* Freight + Insurance (hidden in quick estimate) */}
            {!quickEstimate && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-label-caps text-label-caps text-primary uppercase mb-2">Freight Cost</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 font-code-sm text-on-surface-variant">$</span>
                    <input
                      name="freight_usd"
                      type="number"
                      step="0.01"
                      value={formData.freight_usd}
                      onChange={handleChange}
                      className="w-full bg-transparent border border-steel-blue/40 py-3 pl-8 pr-3 font-code-sm text-code-sm text-primary focus:border-ink-navy focus:border-b-2 focus:ring-0 transition-all rounded-none text-right"
                    />
                  </div>
                </div>
                <div>
                  <label className="block font-label-caps text-label-caps text-primary uppercase mb-2">Insurance</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 font-code-sm text-on-surface-variant">$</span>
                    <input
                      name="insurance_usd"
                      type="number"
                      step="0.01"
                      value={formData.insurance_usd}
                      onChange={handleChange}
                      className="w-full bg-transparent border border-steel-blue/40 py-3 pl-8 pr-3 font-code-sm text-code-sm text-primary focus:border-ink-navy focus:border-b-2 focus:ring-0 transition-all rounded-none text-right"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Origin Country */}
            {!quickEstimate && (
              <div className="pt-4 border-t border-steel-blue/20">
                <label className="block font-label-caps text-label-caps text-primary uppercase mb-2">Country of Origin</label>
                <select
                  name="origin_country"
                  value={formData.origin_country}
                  onChange={handleChange}
                  className="w-full bg-transparent border border-steel-blue/40 p-3 font-code-sm text-code-sm text-primary focus:border-ink-navy focus:border-b-2 focus:ring-0 transition-all rounded-none"
                >
                  <option value="CN">China (CN)</option>
                  <option value="VN">Vietnam (VN)</option>
                  <option value="MX">Mexico (MX)</option>
                  <option value="DE">Germany (DE)</option>
                </select>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="bg-error-container text-on-error-container p-3 rounded-sm text-code-sm font-code-sm">
                {error}
              </div>
            )}

            {/* Submit */}
            <div className="pt-6">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-ink-navy text-on-primary font-label-caps text-label-caps py-4 uppercase tracking-widest hover:bg-opacity-90 transition-all border-none flex justify-center items-center gap-2 disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-[18px]">calculate</span>
                {isLoading ? "Calculating..." : "Calculate Assessment"}
              </button>
            </div>
          </form>
        </div>

        {/* Right: Results */}
        <div className="flex-1 p-8 relative flex flex-col">
          {result ? (
            <>
              {/* Tariff Stamps Overlay */}
              <div className="absolute top-4 right-4 pointer-events-none z-10 flex gap-[-8px] mix-blend-multiply">
                {result.tariff_breakdown.map((item, i) => (
                  <TariffStamp
                    key={i}
                    tariffType={item.type}
                    rate={item.rate}
                    applied={item.applied}
                    size="full"
                    index={i}
                    className="drop-shadow-sm"
                  />
                ))}
              </div>

              {/* Total */}
              <div className="mb-12 relative">
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest mb-2">
                  Total Landed Cost
                </p>
                <div className="font-display-lg text-[64px] text-duty-red font-bold leading-none border-b-4 border-duty-red pb-2 inline-block border-double">
                  {fmt(result.landed_cost_usd)}
                </div>
                <p className="font-code-sm text-sm text-on-surface-variant mt-2">
                  Import Date: {result.import_date} | ID: {result.calculation_id.slice(0, 8)}...
                </p>
              </div>

              {/* Breakdown */}
              <div className="flex-1 relative">
                <div className="ledger-lines absolute inset-0 pointer-events-none opacity-50" />
                <div className="relative z-10 font-code-sm text-[15px] space-y-0 text-primary">
                  <div className="flex justify-between py-2 border-b border-steel-blue/10 border-dashed font-bold">
                    <span className="uppercase tracking-wider">Customs Value (CIF)</span>
                    <span>{fmt(result.customs_value_usd)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-steel-blue/10 border-dashed text-on-surface-variant">
                    <span className="pl-4">Invoice Value</span>
                    <span>{fmt(result.invoice_value_usd)}</span>
                  </div>

                  <div className="mt-4" />
                  {result.tariff_breakdown.map((item, i) => (
                    <div
                      key={i}
                      className={`flex justify-between py-2 border-b border-steel-blue/10 border-dashed ${
                        item.applied ? "text-duty-red" : "text-on-surface-variant line-through opacity-60"
                      }`}
                    >
                      <span className="uppercase tracking-wider">
                        {item.type} ({((item.rate ?? 0) * 100).toFixed(1)}%)
                        {!item.applied && item.reason && ` — ${item.reason}`}
                      </span>
                      <span>{item.applied ? fmt(item.amount_usd ?? 0) : "—"}</span>
                    </div>
                  ))}

                  <div className="flex justify-between py-3 mt-4 border-t-2 border-duty-red font-bold text-duty-red">
                    <span className="uppercase tracking-wider">Total Duty</span>
                    <span>{fmt(result.total_duty_usd)}</span>
                  </div>
                </div>
              </div>

              {/* FX info */}
              {result.fx_rate_used && (
                <div className="mt-4 pt-4 border-t border-steel-blue/20 font-code-sm text-code-sm text-on-surface-variant">
                  FX Rate: 1 {result.fx_rate_used.from_currency} = {result.fx_rate_used.rate} {result.fx_rate_used.to_currency} ({result.fx_rate_used.date})
                </div>
              )}
            </>
          ) : (
            /* Empty state */
            <div className="flex-1 flex items-center justify-center text-on-surface-variant">
              <div className="text-center">
                <span className="material-symbols-outlined text-[64px] opacity-30">receipt_long</span>
                <p className="mt-4 font-label-caps text-label-caps uppercase tracking-widest">
                  Enter shipment details to calculate assessment
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
      </div>
    </>
  );
}
