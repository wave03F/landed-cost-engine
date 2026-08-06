import type { Metadata } from "next";
import { SideNav } from "@/components/layout/side-nav";
import { TopNav } from "@/components/layout/top-nav";
import { MobileHeader } from "@/components/layout/mobile-header";
import { MobileNav } from "@/components/layout/mobile-nav";
import { I18nProvider } from "@/lib/i18n";
import "./globals.css";

export const metadata: Metadata = {
  title: "Landed Cost Ledger",
  description: "Calculate US import landed costs with multi-layer tariff rules",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Public+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400..700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-primary text-on-surface min-h-screen font-body-md">
        <I18nProvider>
          {/* Mobile Layout */}
          <div className="md:hidden flex flex-col min-h-screen">
            <MobileHeader />
            <main className="flex-grow p-4 pb-32">
              {children}
            </main>
            <MobileNav />
          </div>

          {/* Desktop Layout */}
          <div className="hidden md:flex h-screen overflow-hidden bg-ink-navy">
            <SideNav />
            <div className="flex-1 flex flex-col h-screen overflow-hidden">
              <TopNav />
              <main className="flex-1 overflow-y-auto p-gutter lg:p-margin-page">
                <div className="max-w-[1200px] mx-auto min-h-full">
                  {children}
                </div>
              </main>
            </div>
          </div>
        </I18nProvider>
      </body>
    </html>
  );
}
