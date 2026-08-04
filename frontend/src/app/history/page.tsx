"use client";

import { useState, useEffect } from "react";
import type { CalculationLog, TariffType } from "@/lib/types";
import { listCalculations } from "@/lib/api";
import { TariffStamp } from "@/components/ui/TariffStamp";

export default function HistoryPage() {
  const [items, setItems] = useState<CalculationLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const data = await listCalculations();
      setItems(data);
    } catch {
      setItems([]);
    } finally {
      setIsLoading(false);
    }
  };

  const fmt = (n: number) =>
    n.toLocaleString("en-US", { style: "currency", currency: "USD" });

  return (
    <div className="bg-manifest-paper text-on-surface noise-bg border border-steel-blue/30 shadow-[0_10px_30px_rgba(0,0,0,0.5)] rounded-sm relative overflow-hidden">
      <div className="h-2 bg-brass w-full flex-shrink-0" />
      <div className="px-8 py-6 border-b border-steel-blue/20 bg-surface-container-low/50">
        <p className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase tracking-widest">
          Audit Trail
        </p>
        <h2 className="font-headline-lg text-headline-lg text-primary">Calculation History</h2>
      </div>

      <div className="p-8">
        {isLoading ? (
          <div className="text-center py-16 text-on-surface-variant">
            <p className="font-label-caps text-label-caps uppercase tracking-widest animate-pulse">
              Loading records...
            </p>
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-16 text-on-surface-variant">
            <span className="material-symbols-outlined text-[48px] opacity-30">history</span>
            <p className="mt-4 font-label-caps text-label-caps uppercase tracking-widest">
              No calculations recorded yet
            </p>
          </div>
        ) : (
          <div className="font-code-sm text-[15px] text-primary">
            {items.map((item) => (
              <div key={item.id} className="border-b border-steel-blue/10 border-dashed">
                <div
                  onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
                  className="flex justify-between py-3 px-4 cursor-pointer hover:bg-surface-container-high/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    {/* Compact stamps for matched rules */}
                    <div className="flex -space-x-1">
                      {item.matched_rules.slice(0, 3).map((ruleId, i) => {
                        const type = ruleId.split("-")[0].toUpperCase() as TariffType;
                        const validType = ["MFN", "SECTION_301", "SECTION_232", "IEEPA"].includes(type)
                          ? type
                          : ruleId.includes("301") ? "SECTION_301"
                          : ruleId.includes("232") ? "SECTION_232"
                          : ruleId.includes("ieepa") ? "IEEPA"
                          : "MFN";
                        return (
                          <TariffStamp key={i} tariffType={validType as TariffType} size="compact" index={i} />
                        );
                      })}
                    </div>
                    <span className="font-bold uppercase">{item.hts_code}</span>
                    <span className="text-on-surface-variant hidden sm:inline">{item.import_date}</span>
                    <span className="text-on-surface-variant hidden sm:inline">{item.origin_country}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-duty-red font-bold">
                      {fmt((item.result_data as Record<string, number>).landed_cost_usd ?? 0)}
                    </span>
                    <span className="material-symbols-outlined text-[16px] text-on-surface-variant">
                      {expandedId === item.id ? "expand_less" : "expand_more"}
                    </span>
                  </div>
                </div>
                {expandedId === item.id && (
                  <div className="px-4 pb-4 pt-2 bg-surface-container-low/30">
                    {/* Full stamps in expanded view */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {item.matched_rules.map((ruleId, i) => {
                        const validType = ruleId.includes("301") ? "SECTION_301"
                          : ruleId.includes("232") ? "SECTION_232"
                          : ruleId.includes("ieepa") ? "IEEPA"
                          : "MFN";
                        return (
                          <TariffStamp
                            key={i}
                            tariffType={validType as TariffType}
                            size="full"
                            applied={true}
                            index={i}
                          />
                        );
                      })}
                    </div>
                    <pre className="text-[12px] text-on-surface-variant overflow-x-auto">
                      {JSON.stringify(item.result_data, null, 2)}
                    </pre>
                    <p className="text-[11px] text-on-surface-variant mt-2">
                      Calculated: {item.calculated_at} | Rules: {item.matched_rules.join(", ")}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
