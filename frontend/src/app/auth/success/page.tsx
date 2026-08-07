"use client";

import { Suspense, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

function AuthSuccessContent() {
  const router = useRouter();
  const { login } = useAuth();

  useEffect(() => {
    // Read tokens from URL fragment (hash) — secure, never sent to server
    const hash = window.location.hash.substring(1); // remove #
    const params = new URLSearchParams(hash);
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");

    if (accessToken && refreshToken) {
      login(accessToken, refreshToken);
      // Clean the URL (remove fragment)
      window.history.replaceState(null, "", "/auth/success");
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

export default function AuthSuccessPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-[50vh]"><p>Loading...</p></div>}>
      <AuthSuccessContent />
    </Suspense>
  );
}
