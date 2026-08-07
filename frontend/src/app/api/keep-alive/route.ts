/**
 * Keep-alive endpoint — Vercel Cron hits this every 10 minutes
 * which in turn pings the Render backend to prevent cold start.
 *
 * Configure in vercel.json: crons
 */

import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export async function GET() {
  try {
    const res = await fetch(`${BACKEND_URL}/health`, { cache: "no-store" });
    const data = await res.json();
    return NextResponse.json({ frontend: "alive", backend: data.status });
  } catch {
    return NextResponse.json({ frontend: "alive", backend: "unreachable" });
  }
}
