"use client";

export function MobileHeader() {
  return (
    <header className="bg-primary border-b border-outline-variant flex justify-between items-center w-full px-4 py-3 sticky top-0 z-50 shadow-md md:hidden">
      <div className="flex items-center gap-2">
        <span
          className="material-symbols-outlined text-on-primary"
          style={{ fontVariationSettings: "'FILL' 1" }}
        >
          description
        </span>
        <h1 className="font-display-lg text-[20px] text-on-primary uppercase tracking-tighter leading-none">
          Landed Cost Ledger
        </h1>
      </div>
      <div className="flex gap-4">
        <span className="material-symbols-outlined text-on-primary">notifications</span>
        <span className="material-symbols-outlined text-on-primary">help_outline</span>
      </div>
    </header>
  );
}
