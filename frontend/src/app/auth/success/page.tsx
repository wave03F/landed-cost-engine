"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function AuthSuccessPage() {
  const router = useRouter();
  const { login, isLoggedIn } = useAuth();

  useEffect(() => {
    // Tokens were already stored in localStorage by /auth/callback route handler
    const accessToken = localStorage.getItem("access_token") || sessionStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token") || sessionStorage.getItem("refresh_token");

    if (accessToken && refreshToken) {
      login(accessToken, refreshToken);
      router.replace("/calculator");
    } else {
      router.replace("/login");
    }
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
