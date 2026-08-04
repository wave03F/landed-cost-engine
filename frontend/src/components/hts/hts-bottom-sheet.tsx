"use client";

import type { HTSCode, TariffRule } from "@/lib/types";

interface HTSBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  code: HTSCode | null;
  rules: TariffRule[];
  rulesLoading: boolean;
  onUseInCalculator: () => void;
}

export function HTSBottomSheet({
  isOpen,
  onClose,
  code,
  rules,
  rulesLoading,
  onUseInCalculator,
}: HTSBottomSheetProps) {
  const totalRate = rules.filter((r) => r.rate > 0).reduce((sum, r) => sum + r.rate, 0);

  return (
    <>
      {/* Overlay */}
      <div
        onClick={onClose}
        className={`fixed inset-0 bg-primary/40 z-40 backdrop-blur-sm transition-opacity duration-300 ${
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
      />

      {/* Bottom Sheet */}
      <div
        className={`fixed bottom-0 left-0 w-full bg-surface-container-lowest rounded-t-xl z-50 shadow-[0_-4px_24px_rgba(0,0,0,0.1)] flex flex-col max-h-[90vh] transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] ${
          isOpen ? "translate-y-0" : "translate-y-full"
        }`}
      >
        {/* Drag Handle + Header */}
        <div className="flex flex-col items-center pt-3 pb-2 border-b border-outline-variant relative">
          <div className="w-12 h-1 bg-outline-variant rounded-full mb-3" />
          <h2 className="font-title-md text-title-md text-primary w-full text-center px-8">
            {code ? `Code ${code.code}` : "HTS Details"}
          </h2>
          <button
            onClick={onClose}
            className="absolute right-4 top-4 text-on-surface-variant hover:text-primary"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1 flex flex-col gap-6 relative">
          {code && (
            <>
              {/* HTS Code */}
              <div className="flex flex-col gap-1">
                <span className="font-label-caps text-label-caps text-on-surface-variant">HTS CODE</span>
                <span className="font-code-sm text-code-sm text-primary text-xl font-bold border-b-2 border-secondary pb-1 inline-block w-fit">
                  {code.code}
                </span>
              </div>

              {/* Description */}
              <div className="flex flex-col gap-1">
                <span className="font-label-caps text-label-caps text-on-surface-variant">DESCRIPTION</span>
                <p className="text-on-surface">{code.description}</p>
              </div>

              {/* Rate Cards */}
              {rulesLoading ? (
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase animate-pulse text-center py-4">
                  Loading rates...
                </p>
              ) : rules.length > 0 ? (
                <>
                  <div className="grid grid-cols-2 gap-4 mt-2">
                    {rules.map((rule) => {
                      const isDanger = rule.tariff_type === "SECTION_301" || rule.tariff_type === "SECTION_232";
                      return (
                        <div
                          key={rule.id}
                          className={`p-4 relative overflow-hidden ${
                            isDanger
                              ? "bg-error-container/20 border border-error/30"
                              : "bg-surface-container border border-on-tertiary-container/30"
                          }`}
                        >
                          <div
                            className={`font-label-caps text-label-caps mb-2 ${
                              isDanger ? "text-error" : "text-on-surface-variant"
                            }`}
                          >
                            {rule.tariff_type === "MFN" ? "GENERAL (MFN)" : rule.tariff_type.replace("_", " ")}
                          </div>
                          <div
                            className={`font-display-lg text-display-lg ${
                              isDanger ? "text-error" : "text-primary"
                            }`}
                          >
                            {(rule.rate * 100).toFixed(1)}%
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Total */}
                  <div className="mt-4 pt-4 border-t border-outline-variant flex justify-between items-center">
                    <span className="font-label-caps text-label-caps text-on-surface-variant">
                      EFFECTIVE TOTAL RATE
                    </span>
                    <span className="font-title-md text-title-md text-primary">
                      {(totalRate * 100).toFixed(1)}%
                    </span>
                  </div>
                </>
              ) : (
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase text-center py-4">
                  No tariff rules found
                </p>
              )}

              {/* Action */}
              <button
                onClick={onUseInCalculator}
                className="w-full bg-secondary text-on-secondary font-label-caps text-label-caps py-4 mt-4 uppercase hover:bg-on-secondary-container transition-colors shadow-sm"
              >
                SELECT FOR CALCULATOR
              </button>
            </>
          )}
        </div>
      </div>
    </>
  );
}
