"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { LanguageSwitcher, useI18n } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";

export function TopNav() {
  const { t } = useI18n();
  const { user, isLoggedIn, logout } = useAuth();
  const router = useRouter();
  const [showMenu, setShowMenu] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="h-[56px] flex-shrink-0 flex justify-between items-center w-full px-6 border-b border-outline-variant/20 bg-primary z-20 relative">
      {/* Left: Brand */}
      <h1 className="font-display-lg text-[18px] text-on-primary uppercase tracking-tight">
        {t("app.title")}
      </h1>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        <LanguageSwitcher />
        <div className="w-[1px] h-5 bg-outline-variant/30" />

        {/* Notifications */}
        <button
          className="text-on-primary/70 hover:text-on-primary transition-colors p-1.5 relative"
          title="Notifications"
          onClick={() => router.push("/history")}
        >
          <span className="material-symbols-outlined text-[20px]">notifications</span>
          <span className="absolute top-0.5 right-0.5 w-2 h-2 bg-duty-red rounded-full" />
        </button>

        {/* Help */}
        <div className="relative">
          <button
            className="text-on-primary/70 hover:text-on-primary transition-colors p-1.5"
            title="Help"
            onClick={() => setShowHelp(!showHelp)}
          >
            <span className="material-symbols-outlined text-[20px]">help_outline</span>
          </button>

          {showHelp && (
            <div className="absolute right-0 top-10 w-64 bg-surface border border-outline-variant shadow-lg rounded-sm p-4 z-50">
              <h3 className="font-label-caps text-label-caps text-primary uppercase mb-2">Quick Help</h3>
              <ul className="text-[12px] text-on-surface-variant space-y-2">
                <li className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-[14px] mt-0.5">calculate</span>
                  <span><strong>Calculator</strong> — Enter HTS code + value to get landed cost</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-[14px] mt-0.5">search_insights</span>
                  <span><strong>HTS Browser</strong> — Look up product classification codes</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-[14px] mt-0.5">compare_arrows</span>
                  <span><strong>Compare</strong> — Side-by-side cost comparison</span>
                </li>
              </ul>
              <a
                href="mailto:honasas1101@gmail.com"
                className="block mt-3 pt-3 border-t border-outline-variant text-[11px] text-brass hover:underline"
              >
                Need more help? Contact support →
              </a>
            </div>
          )}
        </div>

        {/* Avatar / Profile */}
        <div className="relative ml-1">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="w-7 h-7 rounded-full border border-outline-variant/40 overflow-hidden hover:ring-2 hover:ring-brass transition-all flex items-center justify-center bg-surface-tint"
          >
            {user?.avatar_url ? (
              <img src={user.avatar_url} alt={user.name} className="w-full h-full object-cover" />
            ) : (
              <span className="material-symbols-outlined text-on-primary text-[16px]">person</span>
            )}
          </button>

          {showMenu && (
            <div className="absolute right-0 top-10 w-56 bg-surface border border-outline-variant shadow-lg rounded-sm z-50 overflow-hidden">
              {isLoggedIn && user ? (
                <>
                  <div className="p-3 border-b border-outline-variant bg-surface-container-low/50">
                    <p className="font-code-sm text-code-sm text-primary font-bold truncate">{user.name}</p>
                    <p className="text-[11px] text-on-surface-variant truncate">{user.email}</p>
                    <span className="inline-block mt-1 bg-brass/20 text-brass text-[9px] font-bold px-1.5 py-0.5 uppercase">
                      {user.role}
                    </span>
                  </div>
                  <button
                    onClick={() => { setShowMenu(false); router.push("/admin"); }}
                    className="w-full text-left px-3 py-2.5 text-[12px] text-on-surface-variant hover:bg-surface-container-high flex items-center gap-2 transition-colors"
                  >
                    <span className="material-symbols-outlined text-[16px]">settings</span>
                    Settings
                  </button>
                  <button
                    onClick={() => { setShowMenu(false); handleLogout(); }}
                    className="w-full text-left px-3 py-2.5 text-[12px] text-error hover:bg-error-container/30 flex items-center gap-2 transition-colors border-t border-outline-variant"
                  >
                    <span className="material-symbols-outlined text-[16px]">logout</span>
                    Sign Out
                  </button>
                </>
              ) : (
                <button
                  onClick={() => { setShowMenu(false); router.push("/login"); }}
                  className="w-full text-left px-3 py-3 text-[12px] text-primary hover:bg-surface-container-high flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-[16px]">login</span>
                  Sign In
                </button>
              )}
            </div>
          )}
        </div>
      </div>

    </header>
  );
}
