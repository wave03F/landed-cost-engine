import { SideNav } from "@/components/layout/side-nav";
import { TopNav } from "@/components/layout/top-nav";
import { MobileHeader } from "@/components/layout/mobile-header";
import { MobileNav } from "@/components/layout/mobile-nav";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      {/* Mobile Layout */}
      <div className="md:hidden flex flex-col min-h-screen bg-ink-navy">
        <MobileHeader />
        <main className="flex-grow p-3 pb-32">
          <div className="paper-texture min-h-full rounded-2xl bg-surface-bright p-4 shadow-[0_8px_24px_rgba(0,0,0,0.25)]">
            {children}
          </div>
        </main>
        <MobileNav />
      </div>

      {/* Desktop Layout */}
      <div className="hidden md:flex h-screen overflow-hidden bg-ink-navy">
        <SideNav />
        <div className="flex-1 flex flex-col h-screen overflow-hidden">
          <TopNav />
          {/* Content sits inside a rounded "manifest card" floating on the ink-navy
              canvas, echoing the rounded hero panel on the landing page. */}
          <main className="flex-1 overflow-hidden p-gutter lg:p-margin-page">
            <div className="paper-texture h-full overflow-y-auto rounded-2xl bg-surface-bright shadow-[0_8px_32px_rgba(0,0,0,0.3)] md:rounded-[1.5rem]">
              <div className="max-w-[1200px] mx-auto min-h-full p-gutter lg:p-stack-lg">
                {children}
              </div>
            </div>
          </main>
        </div>
      </div>
    </>
  );
}
