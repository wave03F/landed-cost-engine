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
    </>
  );
}
