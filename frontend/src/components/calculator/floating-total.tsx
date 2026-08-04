"use client";

interface FloatingTotalProps {
  total: number | null;
}

export function FloatingTotal({ total }: FloatingTotalProps) {
  if (total === null) return null;

  const fmt = (n: number) =>
    n.toLocaleString("en-US", { style: "currency", currency: "USD" });

  return (
    <div className="fixed bottom-[60px] left-0 right-0 bg-surface border-t-2 border-primary p-4 shadow-[0_-4px_16px_rgba(0,0,0,0.15)] z-40 md:hidden">
      <div className="flex justify-between items-baseline max-w-md mx-auto">
        <span className="font-label-caps text-label-caps text-on-surface uppercase tracking-widest">
          Total Landed Cost
        </span>
        <div className="flex flex-col items-end">
          <span className="font-display-lg text-headline-lg-mobile text-primary border-b-4 border-error pb-1 leading-none">
            {fmt(total)}
          </span>
          <span className="font-code-sm text-[10px] text-outline mt-1 uppercase">
            USD &bull; Est. Final
          </span>
        </div>
      </div>
    </div>
  );
}
