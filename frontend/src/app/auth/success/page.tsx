"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

function AuthSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");

    if (accessToken && refreshToken) {
      // Store tokens + fetch user (remember me via localStorage)
      login(accessToken, refreshToken);
      router.replace("/");
    } else {
      router.replace("/login");
    }
  }, [searchParams, router, login]);

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
