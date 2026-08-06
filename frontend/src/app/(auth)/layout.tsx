/**
 * Auth pages layout — no sidebar, no top nav.
 * Just centered content on dark background.
 */

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-ink-navy flex items-center justify-center p-4">
      {children}
    </div>
  );
}
