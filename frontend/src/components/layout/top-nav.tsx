"use client";

export function TopNav() {
  return (
    <header className="h-[72px] flex-shrink-0 flex justify-between items-center w-full px-margin-page border-b border-outline-variant/30 bg-primary z-20">
      <div className="flex items-center gap-8">
        <h1 className="font-display-lg text-[24px] text-on-primary uppercase tracking-tighter">
          Landed Cost Ledger
        </h1>
        <nav className="hidden md:flex gap-6">
          <a href="#" className="text-on-primary-container font-medium hover:text-secondary-fixed transition-colors font-label-caps text-label-caps uppercase">
            Dashboard
          </a>
          <a href="#" className="text-on-primary-container font-medium hover:text-secondary-fixed transition-colors font-label-caps text-label-caps uppercase">
            Manifests
          </a>
          <a href="#" className="text-on-primary-container font-medium hover:text-secondary-fixed transition-colors font-label-caps text-label-caps uppercase">
            Compliance
          </a>
        </nav>
      </div>
      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative text-on-primary-container hidden lg:block">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2">search</span>
          <input
            type="text"
            placeholder="Search manifest..."
            className="bg-surface-tint/20 border border-outline-variant/30 text-on-primary pl-10 pr-4 py-2 text-code-sm font-code-sm focus:outline-none focus:border-secondary-fixed transition-colors w-64 rounded-sm"
          />
        </div>
        <button className="text-on-primary hover:text-secondary-fixed transition-colors p-2">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        <button className="text-on-primary hover:text-secondary-fixed transition-colors p-2">
          <span className="material-symbols-outlined">help_outline</span>
        </button>
        {/* Avatar placeholder */}
        <div className="w-8 h-8 bg-surface-tint rounded-full border border-outline-variant/50 ml-2" />
      </div>
    </header>
  );
}
