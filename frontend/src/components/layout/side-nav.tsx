"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Calculator", icon: "calculate", fill: true },
  { href: "/hts-codes", label: "HTS Browser", icon: "search_insights", fill: false },
  { href: "/history", label: "History", icon: "history", fill: false },
  { href: "/admin", label: "Settings", icon: "settings", fill: false },
] as const;

export function SideNav() {
  const pathname = usePathname();

  return (
    <nav className="h-screen w-64 flex-shrink-0 flex flex-col border-r border-outline-variant bg-surface-container-low text-primary relative z-20">
      {/* Header */}
      <div className="p-6 border-b border-outline-variant">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-on-primary">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
              account_balance
            </span>
          </div>
          <div>
            <h2 className="font-display-lg text-[20px] font-bold leading-tight">Duty Manifest</h2>
            <p className="font-code-sm text-code-sm text-on-surface-variant">Official Ledger v4.1</p>
          </div>
        </div>
        <Link
          href="/"
          className="block w-full bg-brass text-ink-navy font-label-caps text-label-caps py-3 uppercase tracking-widest hover:opacity-90 transition-opacity text-center"
        >
          New Entry
        </Link>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {NAV_ITEMS.map(({ href, label, icon, fill }) => {
            const isActive = pathname === href;
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={
                    isActive
                      ? "bg-secondary text-on-secondary font-bold p-3 flex items-center gap-3 rounded-sm scale-95 duration-100 shadow-[0_2px_4px_rgba(0,0,0,0.1)]"
                      : "text-on-surface-variant hover:bg-surface-container-high p-3 flex items-center gap-3 transition-all rounded-sm"
                  }
                >
                  <span
                    className="material-symbols-outlined"
                    style={isActive || fill ? { fontVariationSettings: "'FILL' 1" } : undefined}
                  >
                    {icon}
                  </span>
                  <span className="font-label-caps text-label-caps uppercase">{label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-outline-variant">
        <ul className="space-y-1">
          <li>
            <a href="#" className="text-on-surface-variant hover:bg-surface-container-high p-3 flex items-center gap-3 transition-all rounded-sm">
              <span className="material-symbols-outlined">contact_support</span>
              <span className="font-label-caps text-label-caps uppercase">Support</span>
            </a>
          </li>
          <li>
            <a href="#" className="text-on-surface-variant hover:bg-surface-container-high p-3 flex items-center gap-3 transition-all rounded-sm">
              <span className="material-symbols-outlined">logout</span>
              <span className="font-label-caps text-label-caps uppercase">Sign Out</span>
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
}
