"use client";

import { LanguageSwitcher, useI18n } from "@/lib/i18n";

export function MobileHeader() {
  const { t } = useI18n();

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
          {t("app.title")}
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <LanguageSwitcher />
        <span className="material-symbols-outlined text-on-primary">notifications</span>
        <span className="material-symbols-outlined text-on-primary">help_outline</span>
      </div>
    </header>
  );
}
