"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export default function LoginPage() {
  const { isLoggedIn, isLoading } = useAuth();
  const router = useRouter();
  const [rememberMe, setRememberMe] = useState(true);

  useEffect(() => {
    if (!isLoading && isLoggedIn) {
      router.replace("/");
    }
  }, [isLoggedIn, isLoading, router]);

  // Pass remember preference via sessionStorage so auth/success page knows
  const handleLogin = (provider: "google" | "github") => {
    if (rememberMe) {
      localStorage.setItem("auth_persist", "local");
    } else {
      localStorage.setItem("auth_persist", "session");
    }
    window.location.href = `${API_URL}/auth/login/${provider}`;
  };

  return (
    <div className="w-full max-w-[400px]">
      <div className="bg-manifest-paper border border-steel-blue/30 shadow-[0_10px_30px_rgba(0,0,0,0.5)] rounded-sm overflow-hidden">
        {/* Red accent */}
        <div className="h-2 bg-duty-red w-full" />

        {/* Header */}
        <div className="px-8 pt-8 pb-4 text-center">
          <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center text-on-primary mx-auto mb-4">
            <span className="material-symbols-outlined text-[32px]" style={{ fontVariationSettings: "'FILL' 1" }}>
              account_balance
            </span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-primary">Landed Cost Ledger</h1>
          <p className="font-code-sm text-code-sm text-on-surface-variant mt-2">
            Sign in to calculate duties and track history
          </p>
        </div>

        {/* OAuth Buttons */}
        <div className="px-8 pb-4 pt-4 space-y-3">
          {/* Google */}
          <button
            onClick={() => handleLogin("google")}
            className="w-full flex items-center justify-center gap-3 bg-white border border-gray-300 text-gray-700 font-medium py-3 px-4 hover:bg-gray-50 hover:shadow-sm transition-all cursor-pointer"
          >
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            <span className="font-label-caps text-label-caps uppercase tracking-wider">
              Sign in with Google
            </span>
          </button>

          {/* GitHub */}
          <button
            onClick={() => handleLogin("github")}
            className="w-full flex items-center justify-center gap-3 bg-[#24292f] text-white font-medium py-3 px-4 hover:bg-[#1b1f23] transition-all cursor-pointer"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            <span className="font-label-caps text-label-caps uppercase tracking-wider">
              Sign in with GitHub
            </span>
          </button>
        </div>

        {/* Remember Me Toggle */}
        <div className="px-8 pb-6">
          <label className="flex items-center gap-3 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="w-4 h-4 border-2 border-steel-blue/40 rounded-sm bg-transparent checked:bg-brass checked:border-brass focus:ring-0 cursor-pointer"
            />
            <span className="font-code-sm text-code-sm text-on-surface-variant">
              Remember me on this device
            </span>
          </label>
        </div>

        {/* Footer */}
        <div className="px-8 pb-6 text-center border-t border-steel-blue/10 pt-4">
          <p className="text-[11px] text-on-surface-variant italic">
            No password needed. We only access your name and email.
          </p>
        </div>
      </div>
    </div>
  );
}
