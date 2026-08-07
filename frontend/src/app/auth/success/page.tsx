"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function AuthSuccessPage() {
  const router = useRouter();
  const { login } = useAuth();

  useEffect(() => {
    // Try hash fragment first (from OAuth redirect)
    const hash = window.location.hash.substring(1);
    if (hash) {
      const params = new URLSearchParams(hash);
      const accessToken = params.get("access_token");
      const refreshToken = params.get("refresh_token");

      if (accessToken && refreshToken) {
        login(accessToken, refreshToken);
        window.history.replaceState(null, "", "/auth/success");
        router.replace("/calculator");
        return;
      }
    }

    // Fallback: check localStorage (tokens may already be stored by /auth/callback)
    const storedToken = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    if (storedToken) {
      router.replace("/calculator");
      return;
    }

    // Nothing found — back to login
    router.replace("/login");
  }, [router, login]);

  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="text-center">
        <span className="material-symbols-outlined text-[48px] text-brass animate-spin">progress_activity</span>
        <p className="mt-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest">
          Logging in...
        </p>
      </div>
    </div>
  );
}
