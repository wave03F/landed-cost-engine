"use client";

/**
 * Print-friendly page for Thai PDF export.
 *
 * Flow:
 * 1. Calculator stores result in sessionStorage
 * 2. User navigates here (same tab, no popup)
 * 3. This page renders the styled Thai document
 * 4. User taps "บันทึก PDF" → triggers browser share/print
 * 5. "กลับ" button returns to calculator
 *
 * Works on mobile (iOS Safari, Chrome Android) because:
 * - No popup needed
 * - Uses native share sheet on mobile (if available)
 * - Falls back to window.print() on desktop
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { CalculationResult } from "@/lib/types";

export default function PrintPage() {
  const router = useRouter();
  const [result, setResult] = useState<CalculationResult | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("print-result");
    if (stored) {
      setResult(JSON.parse(stored));
    }
  }, []);

  const fmt = (n: number) => `$${n.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;

  const handlePrint = () => {
    window.print();
  };

  const handleBack = () => {
    router.back();
  };

  if (!result) {
    return (
      <div className="p-8 text-center">
        <p>ไม่พบข้อมูลการคำนวณ</p>
        <button onClick={handleBack} className="mt-4 underline">กลับ</button>
      </div>
    );
  }

  return (
    <>
      {/* Action buttons — hidden when printing */}
      <div className="print:hidden fixed top-0 left-0 right-0 bg-[#16233A] text-white flex justify-between items-center px-4 py-3 z-50 shadow-lg">
        <button onClick={handleBack} className="flex items-center gap-1 text-sm">
          <span className="material-symbols-outlined text-[18px]">arrow_back</span>
          กลับ
        </button>
        <button
          onClick={handlePrint}
          className="bg-[#F5BC6C] text-[#16233A] font-bold px-4 py-2 text-sm flex items-center gap-1.5"
        >
          <span className="material-symbols-outlined text-[18px]">save</span>
          บันทึก PDF
        </button>
      </div>

      {/* Document content */}
      <div className="pt-16 print:pt-0 max-w-[800px] mx-auto p-6 print:p-10 font-sans text-[#1c1c15]">
        {/* Accent bar */}
        <div className="h-[6px] bg-[#C0392B] mb-0 print:mb-0" />

        {/* Header */}
        <div className="bg-[#16233A] text-white px-5 py-4 mb-5">
          <h1 className="text-lg font-bold">ระบบคำนวณต้นทุนนำเข้า</h1>
          <p className="text-[#F5BC6C] text-xs mt-0.5">ใบสรุปการประเมินภาษีนำเข้า</p>
          <div className="text-right text-[10px] text-gray-300 -mt-6">
            <p>เลขอ้างอิง: {result.calculation_id.slice(0, 8).toUpperCase()}</p>
            <p>วันที่: {new Date().toISOString().split("T")[0]}</p>
          </div>
        </div>

        {/* Shipment info */}
        <div className="grid grid-cols-3 gap-3 bg-[#F0ECE1] border border-gray-300 p-4 mb-5 text-sm">
          <div>
            <div className="text-[9px] text-gray-500 uppercase">รหัส HTS</div>
            <div className="font-bold text-base">{result.hts_code}</div>
          </div>
          <div>
            <div className="text-[9px] text-gray-500 uppercase">ประเทศต้นทาง</div>
            <div className="font-bold text-base">{result.origin_country}</div>
          </div>
          <div>
            <div className="text-[9px] text-gray-500 uppercase">วันที่นำเข้า</div>
            <div className="font-bold text-base">{result.import_date}</div>
          </div>
        </div>

        {result.de_minimis_applied ? (
          <div className="bg-green-50 border border-green-300 p-4 text-green-800 font-semibold">
            ยกเว้นภาษี (DE MINIMIS) — มูลค่า {fmt(result.customs_value_usd)} ต่ำกว่า $800
          </div>
        ) : (
          <>
            {/* Valuation */}
            <div className="mb-5">
              <h2 className="text-[10px] font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200 pb-1 mb-2">
                การประเมินมูลค่า
              </h2>
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[#16233A] text-white text-[10px]">
                    <th className="text-left py-2 px-3">รายการ</th>
                    <th className="text-right py-2 px-3">จำนวนเงิน (USD)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-gray-100">
                    <td className="py-2 px-3">มูลค่าตามใบกำกับสินค้า</td>
                    <td className="py-2 px-3 text-right">{fmt(result.invoice_value_usd)}</td>
                  </tr>
                  <tr className="border-b border-gray-100">
                    <td className="py-2 px-3">+ ค่าขนส่งและประกัน</td>
                    <td className="py-2 px-3 text-right">{fmt(result.customs_value_usd - result.invoice_value_usd)}</td>
                  </tr>
                  <tr className="font-bold">
                    <td className="py-2 px-3">มูลค่าศุลกากร (CIF)</td>
                    <td className="py-2 px-3 text-right">{fmt(result.customs_value_usd)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Duty Assessment */}
            <div className="mb-5">
              <h2 className="text-[10px] font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200 pb-1 mb-2">
                การประเมินภาษี
              </h2>
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[#C0392B] text-white text-[10px]">
                    <th className="text-left py-2 px-3">ประเภท</th>
                    <th className="text-center py-2 px-3">อัตรา</th>
                    <th className="text-right py-2 px-3">จำนวนเงิน</th>
                    <th className="text-center py-2 px-3">สถานะ</th>
                  </tr>
                </thead>
                <tbody>
                  {result.tariff_breakdown.map((item, i) => (
                    <tr
                      key={i}
                      className={`border-b border-gray-100 ${!item.applied ? "text-gray-400 line-through" : ""}`}
                    >
                      <td className="py-2 px-3">{item.type.replace("_", " ")}</td>
                      <td className="py-2 px-3 text-center">
                        {item.rate != null ? `${(item.rate * 100).toFixed(3)}%` : "—"}
                      </td>
                      <td className="py-2 px-3 text-right">
                        {item.applied ? fmt(item.amount_usd ?? 0) : "—"}
                      </td>
                      <td className="py-2 px-3 text-center text-[10px]">
                        {item.applied ? (
                          <span className="text-green-700 font-bold">เก็บภาษี</span>
                        ) : (
                          <span className="text-gray-400">{item.reason ?? "ไม่เก็บ"}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Totals */}
            <div className="border-t-[3px] border-double border-[#16233A] pt-3 mb-3">
              <div className="flex justify-between text-sm py-1">
                <span>ภาษีรวม:</span>
                <span>{fmt(result.total_duty_usd)}</span>
              </div>
              {result.fees && (
                <div className="flex justify-between text-sm py-1">
                  <span>ค่าธรรมเนียม (MPF + HMF):</span>
                  <span>{fmt(result.fees.total_fees_usd)}</span>
                </div>
              )}
            </div>

            {/* Grand total */}
            <div className="bg-[#16233A] text-white px-5 py-4 flex justify-between items-center">
              <span className="font-bold text-sm">ต้นทุนนำเข้ารวมทั้งหมด</span>
              <span className="font-bold text-2xl">{fmt(result.landed_cost_usd)}</span>
            </div>

            {/* Notes */}
            <div className="mt-4 text-[10px] text-gray-500">
              {result.fta_applied && (
                <p>ข้อตกลงการค้าเสรี: {result.fta_applied} — ยกเว้นภาษี MFN</p>
              )}
              {result.fx_rate_used && (
                <p>
                  อัตราแลกเปลี่ยน: 1 {result.fx_rate_used.from_currency} = {result.fx_rate_used.rate}{" "}
                  {result.fx_rate_used.to_currency} (วันที่: {result.fx_rate_used.date})
                </p>
              )}
            </div>
          </>
        )}

        {/* Disclaimer */}
        <div className="mt-8 pt-3 border-t border-gray-200 text-[9px] text-gray-400 italic">
          <p>หมายเหตุ: เอกสารนี้จัดทำโดยระบบ Landed Cost Ledger เพื่อการประมาณการเท่านั้น</p>
          <p>ไม่ถือเป็นคำแนะนำทางกฎหมายหรือศุลกากร กรุณาปรึกษาตัวแทนออกของ (Customs Broker) สำหรับการยื่นเอกสารจริง</p>
        </div>
      </div>
    </>
  );
}
