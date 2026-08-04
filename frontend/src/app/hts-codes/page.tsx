"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { HTSCode, TariffRule } from "@/lib/types";
import { searchHTSCodes, listTariffRules } from "@/lib/api";
import { HTSBottomSheet } from "@/components/hts/hts-bottom-sheet";

export default function HTSCodesPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<HTSCode[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCode, setSelectedCode] = useState<HTSCode | null>(null);
  const [applicableRules, setApplicableRules] = useState<TariffRule[]>([]);
  const [rulesLoading, setRulesLoading] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    try {
      const data = await searchHTSCodes(query);
      setResults(data);
      setSelectedCode(null);
      setApplicableRules([]);
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectCode = async (code: HTSCode) => {
    setSelectedCode(code);
    setSheetOpen(true);
    setRulesLoading(true);
    try {
      const cleanCode = code.code.replace(".", "");
      const prefix = cleanCode.slice(0, 4);
      const rules = await listTariffRules(undefined, prefix);
      setApplicableRules(rules);
    } catch {
      setApplicableRules([]);
    } finally {
      setRulesLoading(false);
    }
  };

  const handleUseInCalculator = () => {
    if (selectedCode) {
      router.push(`/?hts=${selectedCode.code}`);
    }
  };

  // Group results by hierarchy
  const chapters = results.filter((r) => r.level === "chapter");
  const headings = results.filter((r) => r.level === "heading");
  const subheadings = results.filter((r) => r.level === "subheading");

  const totalRate = applicableRules
    .filter((r) => r.rate > 0)
    .reduce((sum, r) => sum + r.rate, 0);

  return (
    <>
      {/* ===== MOBILE VIEW ===== */}
      <div className="md:hidden flex flex-col gap-6">
        {/* Search */}
        <div className="flex flex-col gap-2">
          <h1 className="font-title-md text-title-md text-primary">HTS Browser</h1>
          <div className="relative w-full">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">
              search
            </span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="w-full pl-10 pr-4 py-3 bg-surface-container border border-outline font-code-sm text-code-sm focus:border-secondary focus:ring-1 focus:ring-secondary focus:outline-none transition-all placeholder:text-on-surface-variant/70"
              placeholder="Search HTS Code..."
              type="text"
            />
          </div>
        </div>

        {/* Results List (Card style) */}
        <div className="flex flex-col gap-3">
          {isLoading && (
            <p className="font-label-caps text-label-caps text-on-surface-variant uppercase animate-pulse text-center py-8">
              Searching...
            </p>
          )}

          {!isLoading && results.length === 0 && (
            <div className="text-center py-12 text-on-surface-variant">
              <span className="material-symbols-outlined text-[48px] opacity-30">menu_book</span>
              <p className="mt-4 font-label-caps text-label-caps uppercase tracking-widest">
                Search by code or description
              </p>
            </div>
          )}

          {!isLoading &&
            results.map((code) => (
              <button
                key={code.id}
                onClick={() => handleSelectCode(code)}
                className="text-left w-full bg-surface-container-lowest border border-on-tertiary-container/30 p-4 hover:shadow-[0_4px_12px_rgba(0,0,0,0.05)] transition-all active:scale-[0.98] group relative overflow-hidden"
              >
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-secondary opacity-0 group-hover:opacity-100 group-active:opacity-100 transition-opacity" />
                <div className="flex justify-between items-start mb-1">
                  <span className="font-code-sm text-code-sm text-primary font-bold">{code.code}</span>
                  <span className="material-symbols-outlined text-outline-variant group-hover:text-secondary transition-colors">
                    chevron_right
                  </span>
                </div>
                <p className="text-sm text-on-surface-variant line-clamp-2">{code.description}</p>
              </button>
            ))}
        </div>

        {/* Bottom Sheet (Mobile) */}
        <HTSBottomSheet
          isOpen={sheetOpen}
          onClose={() => setSheetOpen(false)}
          code={selectedCode}
          rules={applicableRules}
          rulesLoading={rulesLoading}
          onUseInCalculator={handleUseInCalculator}
        />
      </div>

      {/* ===== DESKTOP VIEW ===== */}
      <div className="hidden md:flex md:flex-col gap-stack-lg">
        {/* Search Header */}
        <header className="pb-stack-sm border-b border-outline-variant">
          <h1 className="font-headline-lg text-headline-lg text-primary mb-stack-sm">HTS BROWSER</h1>
          <div className="relative w-full max-w-2xl mt-stack-md">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">
              search
            </span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="w-full pl-10 pr-4 py-3 bg-surface-container-highest border border-outline focus:border-primary focus:border-2 font-code-sm text-code-sm text-on-surface rounded-none outline-none transition-all placeholder:text-on-surface-variant/60 shadow-[0_2px_4px_rgba(0,0,0,0.05)]"
              placeholder="Search by HTS code or item description (e.g., 8517.12)"
              type="text"
            />
          </div>
        </header>

        {/* Grid: Hierarchy + Rate Summary */}
        <div className="grid grid-cols-12 gap-gutter">
          {/* Left: Hierarchy */}
          <div className="col-span-7 flex flex-col gap-stack-sm">
            {isLoading && (
              <p className="font-label-caps text-label-caps text-on-surface-variant uppercase animate-pulse text-center py-8">
                Searching...
              </p>
            )}

            {!isLoading && results.length === 0 && (
              <div className="bg-surface paper-texture border border-outline p-margin-page text-center shadow-[0_2px_4px_rgba(0,0,0,0.05)]">
                <span className="material-symbols-outlined text-[48px] text-on-surface-variant/30">menu_book</span>
                <p className="mt-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest">
                  Search HTS codes by number or description
                </p>
              </div>
            )}

            {!isLoading && results.length > 0 && (
              <>
                {/* Chapters */}
                {chapters.map((chapter) => (
                  <div key={chapter.id}>
                    <div
                      onClick={() => handleSelectCode(chapter)}
                      className={`bg-surface paper-texture border p-stack-md shadow-[0_2px_4px_rgba(0,0,0,0.05)] cursor-pointer transition-colors ${
                        selectedCode?.id === chapter.id ? "border-primary" : "border-outline hover:border-primary"
                      }`}
                    >
                      <p className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase tracking-wider">
                        Chapter {chapter.code}
                      </p>
                      <h3 className="font-title-md text-title-md text-primary">{chapter.description}</h3>
                    </div>

                    {headings
                      .filter((h) => h.parent_code === chapter.code)
                      .map((heading) => (
                        <div key={heading.id} className="ml-stack-lg border-l-2 border-outline-variant pl-stack-md mt-stack-sm">
                          <div
                            onClick={() => handleSelectCode(heading)}
                            className={`bg-surface paper-texture border p-stack-md shadow-[0_2px_4px_rgba(0,0,0,0.05)] cursor-pointer group transition-colors ${
                              selectedCode?.id === heading.id ? "border-primary" : "border-outline hover:border-primary"
                            }`}
                          >
                            <p className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase">
                              Heading {heading.code}
                            </p>
                            <h4 className="font-body-md text-body-md text-on-surface group-hover:text-primary">
                              {heading.description}
                            </h4>
                          </div>

                          {subheadings
                            .filter((s) => s.parent_code === heading.code)
                            .map((sub) => (
                              <div key={sub.id} className="ml-stack-lg border-l-2 border-primary pl-stack-md mt-stack-sm">
                                <div
                                  onClick={() => handleSelectCode(sub)}
                                  className={`paper-texture border p-stack-md shadow-[0_4px_12px_rgba(0,0,0,0.08)] relative overflow-hidden cursor-pointer transition-colors ${
                                    selectedCode?.id === sub.id
                                      ? "bg-surface-container-lowest border-primary"
                                      : "bg-surface-container-lowest border-primary/50 hover:border-primary"
                                  }`}
                                >
                                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                                  <p className="font-code-sm text-code-sm text-primary font-bold mb-1">{sub.code}</p>
                                  <h5 className="font-title-md text-title-md text-on-surface">{sub.description}</h5>
                                </div>
                              </div>
                            ))}
                        </div>
                      ))}
                  </div>
                ))}

                {/* Orphan headings */}
                {headings
                  .filter((h) => !chapters.find((c) => c.code === h.parent_code))
                  .map((heading) => (
                    <div key={heading.id}>
                      <div
                        onClick={() => handleSelectCode(heading)}
                        className={`bg-surface paper-texture border p-stack-md shadow-[0_2px_4px_rgba(0,0,0,0.05)] cursor-pointer group transition-colors ${
                          selectedCode?.id === heading.id ? "border-primary" : "border-outline hover:border-primary"
                        }`}
                      >
                        <p className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase">
                          Heading {heading.code}
                        </p>
                        <h4 className="font-body-md text-body-md text-on-surface group-hover:text-primary">
                          {heading.description}
                        </h4>
                      </div>
                      {subheadings
                        .filter((s) => s.parent_code === heading.code)
                        .map((sub) => (
                          <div key={sub.id} className="ml-stack-lg border-l-2 border-primary pl-stack-md mt-stack-sm">
                            <div
                              onClick={() => handleSelectCode(sub)}
                              className={`paper-texture border p-stack-md shadow-[0_4px_12px_rgba(0,0,0,0.08)] relative overflow-hidden cursor-pointer transition-colors ${
                                selectedCode?.id === sub.id
                                  ? "bg-surface-container-lowest border-primary"
                                  : "bg-surface-container-lowest border-primary/50 hover:border-primary"
                              }`}
                            >
                              <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                              <p className="font-code-sm text-code-sm text-primary font-bold mb-1">{sub.code}</p>
                              <h5 className="font-title-md text-title-md text-on-surface">{sub.description}</h5>
                            </div>
                          </div>
                        ))}
                    </div>
                  ))}

                {/* Orphan subheadings */}
                {subheadings
                  .filter((s) => !headings.find((h) => h.code === s.parent_code))
                  .map((sub) => (
                    <div key={sub.id} className="border-l-2 border-primary pl-stack-md">
                      <div
                        onClick={() => handleSelectCode(sub)}
                        className={`paper-texture border p-stack-md shadow-[0_4px_12px_rgba(0,0,0,0.08)] relative overflow-hidden cursor-pointer transition-colors ${
                          selectedCode?.id === sub.id
                            ? "bg-surface-container-lowest border-primary"
                            : "bg-surface-container-lowest border-primary/50 hover:border-primary"
                        }`}
                      >
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                        <p className="font-code-sm text-code-sm text-primary font-bold mb-1">{sub.code}</p>
                        <h5 className="font-title-md text-title-md text-on-surface">{sub.description}</h5>
                      </div>
                    </div>
                  ))}
              </>
            )}
          </div>

          {/* Right: Rate Summary (Desktop) */}
          <div className="col-span-5 relative">
            <div className="bg-surface paper-texture border border-outline p-stack-lg shadow-[0_4px_16px_rgba(0,0,0,0.06)] sticky top-gutter overflow-hidden flex flex-col min-h-[400px]">
              <div className="relative z-10 flex flex-col h-full">
                <div className="border-b border-outline-variant pb-stack-sm mb-stack-md">
                  <h2 className="font-headline-lg text-headline-lg text-primary">RATE SUMMARY</h2>
                  <p className="font-code-sm text-code-sm text-on-surface-variant mt-1">
                    {selectedCode ? `HTS: ${selectedCode.code}` : "Select a code to view rates"}
                  </p>
                </div>

                {selectedCode && !rulesLoading ? (
                  <div className="flex-1 flex flex-col gap-stack-md">
                    {applicableRules.length > 0 ? (
                      <>
                        {applicableRules.map((rule) => (
                          <div key={rule.id} className="flex justify-between items-start border-b border-surface-variant pb-stack-sm">
                            <div className="flex flex-col">
                              <span
                                className={`font-label-caps text-label-caps uppercase flex items-center gap-1 ${
                                  rule.tariff_type === "SECTION_301" || rule.tariff_type === "SECTION_232"
                                    ? "text-error"
                                    : "text-on-surface-variant"
                                }`}
                              >
                                {(rule.tariff_type === "SECTION_301" || rule.tariff_type === "SECTION_232") && (
                                  <span className="material-symbols-outlined text-[16px]">warning</span>
                                )}
                                {rule.tariff_type === "MFN" ? "General MFN Rate" : rule.tariff_type.replace("_", " ")}
                              </span>
                              <span className="font-code-sm text-code-sm text-on-surface-variant text-xs mt-1">
                                {rule.description || `Pattern: ${rule.hts_code_pattern}`}
                              </span>
                            </div>
                            <span
                              className={`font-code-sm text-code-sm font-bold ${
                                rule.tariff_type === "SECTION_301" || rule.tariff_type === "SECTION_232"
                                  ? "text-error"
                                  : "text-on-surface"
                              }`}
                            >
                              {(rule.rate * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                        <div className="mt-auto pt-stack-md border-t-2 border-primary border-double">
                          <div className="flex justify-between items-end">
                            <span className="font-label-caps text-label-caps text-primary uppercase">Estimated Total Duty</span>
                            <span className="font-display-lg text-display-lg text-primary tracking-tight">
                              {(totalRate * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="flex-1 flex items-center justify-center">
                        <p className="font-label-caps text-label-caps text-on-surface-variant uppercase">
                          No tariff rules found for this code
                        </p>
                      </div>
                    )}
                    <button
                      onClick={handleUseInCalculator}
                      className="w-full mt-stack-lg bg-secondary text-on-secondary font-label-caps text-label-caps py-3 uppercase tracking-wider hover:bg-secondary/90 transition-colors border border-secondary shadow-[0_2px_4px_rgba(0,0,0,0.1)] active:scale-[0.98]"
                    >
                      USE IN CALCULATOR
                    </button>
                  </div>
                ) : rulesLoading ? (
                  <div className="flex-1 flex items-center justify-center">
                    <p className="font-label-caps text-label-caps text-on-surface-variant uppercase animate-pulse">
                      Loading rates...
                    </p>
                  </div>
                ) : (
                  <div className="flex-1 flex items-center justify-center text-on-surface-variant">
                    <div className="text-center">
                      <span className="material-symbols-outlined text-[48px] opacity-20">percent</span>
                      <p className="mt-4 font-label-caps text-label-caps uppercase tracking-widest">
                        Select an HTS code to view applicable rates
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
