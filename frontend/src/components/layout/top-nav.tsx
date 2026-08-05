"use client";

import { LanguageSwitcher, useI18n } from "@/lib/i18n";

export function TopNav() {
  const { t } = useI18n();

  return (
    <header className="h-[56px] flex-shrink-0 flex justify-between items-center w-full px-6 border-b border-outline-variant/20 bg-primary z-20">
      {/* Left: Brand */}
      <h1 className="font-display-lg text-[18px] text-on-primary uppercase tracking-tight">
        {t("app.title")}
      </h1>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        <LanguageSwitcher />
        <div className="w-[1px] h-5 bg-outline-variant/30" />
        <button className="text-on-primary/70 hover:text-on-primary transition-colors p-1.5" title="Notifications">
          <span className="material-symbols-outlined text-[20px]">notifications</span>
        </button>
        <button className="text-on-primary/70 hover:text-on-primary transition-colors p-1.5" title="Help">
          <span className="material-symbols-outlined text-[20px]">help_outline</span>
        </button>
        <div className="w-7 h-7 bg-surface-tint rounded-full border border-outline-variant/40 ml-1" />
      </div>
    </header>
  );
}
