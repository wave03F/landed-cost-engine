"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      // Logged in → go to calculator
      router.replace("/calculator");
    } else {
      // Not logged in → go to login
      router.replace("/login");
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <span className="material-symbols-outlined text-[48px] text-brass animate-spin">progress_activity</span>
    </div>
  );
}
