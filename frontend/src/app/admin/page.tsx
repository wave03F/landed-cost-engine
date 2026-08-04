"use client";

import { useState } from "react";

type Tab = "rules" | "exclusions" | "fx" | "hts";

const TABS: { key: Tab; label: string; icon: string }[] = [
  { key: "rules", label: "Tariff Rules", icon: "gavel" },
  { key: "exclusions", label: "Exclusions", icon: "rule" },
  { key: "fx", label: "FX Rates", icon: "currency_exchange" },
  { key: "hts", label: "HTS Codes", icon: "category" },
];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<Tab>("rules");

  return (
    <div className="bg-manifest-paper text-on-surface noise-bg border border-steel-blue/30 shadow-[0_10px_30px_rgba(0,0,0,0.5)] rounded-sm relative overflow-hidden">
      <div className="h-2 bg-on-surface-variant w-full flex-shrink-0" />
      <div className="px-8 py-6 border-b border-steel-blue/20 bg-surface-container-low/50">
        <p className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase tracking-widest">
          Administration
        </p>
        <h2 className="font-headline-lg text-headline-lg text-primary">System Settings</h2>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-steel-blue/20 px-8">
        {TABS.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 px-4 py-3 font-label-caps text-label-caps uppercase tracking-widest transition-colors border-b-2 ${
              activeTab === key
                ? "border-ink-navy text-primary"
                : "border-transparent text-on-surface-variant hover:text-primary"
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">{icon}</span>
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-8">
        <div className="text-center py-16 text-on-surface-variant">
          <span className="material-symbols-outlined text-[48px] opacity-30">construction</span>
          <p className="mt-4 font-label-caps text-label-caps uppercase tracking-widest">
            {activeTab} management — Coming soon
          </p>
          <p className="mt-2 text-body-md text-sm">
            CRUD interface for managing {activeTab} will be implemented here.
          </p>
        </div>
      </div>
    </div>
  );
}
