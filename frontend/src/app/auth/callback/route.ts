/**
 * POST /auth/callback
 *
 * Receives tokens via form POST from backend OAuth callback.
 * Returns HTML that stores tokens via JS then redirects to /auth/success.
 *
 * Secure because:
 * - Tokens arrive via POST body (not in URL/logs/history)
 * - HTML page stores them in localStorage then redirects (tokens never in URL)
 */

import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const accessToken = formData.get("access_token") as string;
  const refreshToken = formData.get("refresh_token") as string;

  if (!accessToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Return HTML that stores tokens in localStorage then redirects
  const html = `<!DOCTYPE html>
<html><head><title>Logging in...</title></head>
<body>
<script>
  var persist = localStorage.getItem("auth_persist") || "local";
  var storage = persist === "session" ? sessionStorage : localStorage;
  storage.setItem("access_token", ${JSON.stringify(accessToken)});
  storage.setItem("refresh_token", ${JSON.stringify(refreshToken)});
  window.location.replace("/auth/success");
</script>
<noscript><a href="/login">Click here if not redirected</a></noscript>
</body></html>`;

  return new NextResponse(html, {
    status: 200,
    headers: { "Content-Type": "text/html" },
  });
}
