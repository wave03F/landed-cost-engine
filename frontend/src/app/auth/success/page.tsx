"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function AuthSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");

    if (accessToken) {
      // Store tokens
      localStorage.setItem("access_token", accessToken);
      if (refreshToken) {
        localStorage.setItem("refresh_token", refreshToken);
      }

      // Redirect to calculator
      router.replace("/");
    } else {
      // No token — something went wrong
      router.replace("/");
    }
  }, [searchParams, router]);

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
