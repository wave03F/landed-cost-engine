"use client";

import type { TariffType } from "@/lib/types";
import { TariffStamp } from "@/components/ui/TariffStamp";

const TARIFF_TYPES: TariffType[] = ["MFN", "SECTION_301", "SECTION_232", "IEEPA", "AD_CVD", "MPF", "HMF"];
const SAMPLE_RATES: Record<TariffType, number> = {
  MFN: 0.025,
  SECTION_301: 0.25,
  SECTION_232: 0.25,
  IEEPA: 0.145,
  AD_CVD: 1.3692,
  MPF: 0.003464,
  HMF: 0.00125,
};

export default function StampDemoPage() {
  return (
    <div className="bg-surface p-8 min-h-screen">
      <h1 className="font-headline-lg text-headline-lg text-primary mb-8">TariffStamp Demo</h1>
      <div className="flex flex-wrap gap-6">
        {TARIFF_TYPES.map((type, i) => (
          <div key={type} className="flex flex-col items-center gap-2">
            <TariffStamp tariffType={type} rate={SAMPLE_RATES[type]} applied={true} size="full" index={i} />
            <span className="font-code-sm text-code-sm text-on-surface-variant">{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
