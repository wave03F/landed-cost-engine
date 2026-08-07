"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthSuccessPage() {
  const router = useRouter();
  const [status, setStatus] = useState("Processing...");

  useEffect(() => {
    try {
      // Read tokens from URL fragment
      const hash = window.location.hash.substring(1);
      const params = new URLSearchParams(hash);
      const accessToken = params.get("access_token");
      const refreshToken = params.get("refresh_token");

      if (accessToken && refreshToken) {
        // Store tokens
        const persist = localStorage.getItem("auth_persist") || "local";
        const storage = persist === "session" ? sessionStorage : localStorage;
        storage.setItem("access_token", accessToken);
        storage.setItem("refresh_token", refreshToken);

        // Clean URL
        window.history.replaceState(null, "", "/auth/success");
        
        setStatus("Login successful! Redirecting...");
        
        // Small delay to ensure storage is written
        setTimeout(() => {
          window.location.href = "/calculator";
        }, 300);
      } else {
        setStatus("No tokens found. Redirecting to login...");
        setTimeout(() => {
          window.location.href = "/login";
        }, 1000);
      }
    } catch (e) {
      setStatus("Error: " + String(e));
      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);
    }
  }, []);

  return (
    <div className="min-h-screen bg-ink-navy flex items-center justify-center">
      <div className="text-center">
        <span className="material-symbols-outlined text-[48px] text-brass animate-spin">progress_activity</span>
        <p className="mt-4 font-label-caps text-label-caps text-on-primary uppercase tracking-widest">
          {status}
        </p>
      </div>
    </div>
  );
}
