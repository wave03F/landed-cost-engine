"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Calculator", icon: "calculate" },
  { href: "/hts-codes", label: "HTS Browser", icon: "search_insights" },
  { href: "/history", label: "History", icon: "history" },
  { href: "/admin", label: "Settings", icon: "settings" },
] as const;

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 w-full bg-surface-container-low border-t border-outline-variant flex justify-around items-center py-2 z-50 h-[60px] md:hidden">
      {NAV_ITEMS.map(({ href, label, icon }) => {
        const isActive = pathname === href;
        return (
          <Link
            key={href}
            href={href}
            className={`flex flex-col items-center gap-1 p-2 w-1/4 transition-colors group ${
              isActive
                ? "text-secondary-fixed bg-primary rounded-sm"
                : "text-on-surface-variant hover:text-primary hover:bg-surface-container-high"
            }`}
          >
            <span
              className="material-symbols-outlined group-hover:scale-110 transition-transform"
              style={isActive ? { fontVariationSettings: "'FILL' 1" } : undefined}
            >
              {icon}
            </span>
            <span className={`font-label-caps text-[10px] uppercase tracking-wider ${isActive ? "font-bold" : ""}`}>
              {label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
