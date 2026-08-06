"use client";

/**
 * Stamp Demo Page — /demo/stamps
 *
 * Shows all 16 combinations:
 * 4 tariff types × 2 sizes × 2 states (applied/not applied)
 *
 * Use this for visual QA before integrating stamps into production pages.
 */

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
      <h1 className="font-headline-lg text-headline-lg text-primary mb-8">
        TariffStamp Component — All Variations
      </h1>

      {/* Full Size */}
      <section className="mb-12">
        <h2 className="font-title-md text-title-md text-primary mb-4 border-b border-outline-variant pb-2">
          Size: Full (128px) — Applied
        </h2>
        <div className="flex flex-wrap gap-6">
          {TARIFF_TYPES.map((type, i) => (
            <div key={type} className="flex flex-col items-center gap-2">
              <TariffStamp
                tariffType={type}
                rate={SAMPLE_RATES[type]}
                applied={true}
                size="full"
                index={i}
              />
              <span className="font-code-sm text-code-sm text-on-surface-variant">{type}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="font-title-md text-title-md text-primary mb-4 border-b border-outline-variant pb-2">
          Size: Full (128px) — Not Applied
        </h2>
        <div className="flex flex-wrap gap-6">
          {TARIFF_TYPES.map((type, i) => (
            <div key={type} className="flex flex-col items-center gap-2">
              <TariffStamp
                tariffType={type}
                rate={SAMPLE_RATES[type]}
                applied={false}
                size="full"
                index={i}
              />
              <span className="font-code-sm text-code-sm text-on-surface-variant">{type} (inactive)</span>
            </div>
          ))}
        </div>
      </section>

      {/* Compact Size */}
      <section className="mb-12">
        <h2 className="font-title-md text-title-md text-primary mb-4 border-b border-outline-variant pb-2">
          Size: Compact (32px) — Applied
        </h2>
        <div className="flex flex-wrap gap-4">
          {TARIFF_TYPES.map((type, i) => (
            <div key={type} className="flex items-center gap-2">
              <TariffStamp
                tariffType={type}
                rate={SAMPLE_RATES[type]}
                applied={true}
                size="compact"
                index={i}
              />
              <span className="font-code-sm text-code-sm text-on-surface-variant">{type}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="font-title-md text-title-md text-primary mb-4 border-b border-outline-variant pb-2">
          Size: Compact (32px) — Not Applied
        </h2>
        <div className="flex flex-wrap gap-4">
          {TARIFF_TYPES.map((type, i) => (
            <div key={type} className="flex items-center gap-2">
              <TariffStamp
                tariffType={type}
                rate={SAMPLE_RATES[type]}
                applied={false}
                size="compact"
                index={i}
              />
              <span className="font-code-sm text-code-sm text-on-surface-variant">{type} (inactive)</span>
            </div>
          ))}
        </div>
      </section>

      {/* Cluster preview (like in calculator results) */}
      <section>
        <h2 className="font-title-md text-title-md text-primary mb-4 border-b border-outline-variant pb-2">
          Cluster Preview (Calculator Results)
        </h2>
        <div className="bg-manifest-paper border border-steel-blue/30 p-8 inline-block relative">
          <div className="flex -space-x-4">
            <TariffStamp tariffType="MFN" rate={0.025} applied={true} size="full" index={0} />
            <TariffStamp tariffType="SECTION_301" rate={0.25} applied={true} size="full" index={1} />
            <TariffStamp tariffType="IEEPA" rate={0.145} applied={false} size="full" index={2} />
          </div>
        </div>
      </section>
    </div>
  );
}
