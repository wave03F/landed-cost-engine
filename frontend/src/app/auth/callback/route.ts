/**
 * POST /auth/callback
 *
 * Receives tokens via form POST from backend OAuth callback.
 * Stores them in a redirect response with tokens in a short-lived URL fragment.
 *
 * This is secure because:
 * - Tokens are sent via POST body (not visible in URL/logs)
 * - We redirect to /auth/success#token=... (fragment is not sent to server)
 */

import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const accessToken = formData.get("access_token") as string;
  const refreshToken = formData.get("refresh_token") as string;

  if (!accessToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Redirect to success page with tokens in URL fragment (not query params)
  // Fragment (#) is never sent to server, never logged, never in history entries
  const successUrl = new URL("/auth/success", request.url);
  successUrl.hash = `access_token=${accessToken}&refresh_token=${refreshToken}`;

  return NextResponse.redirect(successUrl, { status: 303 });
}
