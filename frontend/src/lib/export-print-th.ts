/**
 * Thai PDF Export — Opens a styled print-friendly window with Thai text,
 * then triggers browser's Print dialog (user selects "Save as PDF").
 *
 * This approach guarantees perfect Thai rendering since the browser
 * handles font rendering natively (no font embedding needed).
 */

import type { CalculationResult } from "./types";

export function exportCalculationPrintTH(result: CalculationResult) {
  const fmt = (n: number) => `$${n.toLocaleString("en-US", { minimumFractionDigits: 2 })}`;

  const tariffRows = result.tariff_breakdown
    .map(
      (item) => `
      <tr class="${item.applied ? "" : "not-applied"}">
        <td>${item.type.replace("_", " ")}</td>
        <td class="center">${item.rate != null ? `${(item.rate * 100).toFixed(3)}%` : "—"}</td>
        <td class="right">${item.applied ? fmt(item.amount_usd ?? 0) : "—"}</td>
        <td class="center status">${item.applied ? "เก็บภาษี" : (item.reason ?? "ไม่เก็บ")}</td>
      </tr>`
    )
    .join("");

  const html = `<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8" />
  <title>ใบสรุปการประเมินภาษีนำเข้า — ${result.hts_code}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Sarabun', 'Noto Sans Thai', 'Segoe UI', sans-serif; color: #1c1c15; padding: 40px; max-width: 800px; margin: 0 auto; }
    .accent-bar { height: 6px; background: #C0392B; margin-bottom: 0; }
    .header { background: #16233A; color: white; padding: 20px 24px; margin-bottom: 24px; }
    .header h1 { font-size: 20px; font-weight: 700; margin-bottom: 4px; }
    .header .subtitle { color: #F5BC6C; font-size: 12px; }
    .header .meta { color: #ccc; font-size: 10px; text-align: right; margin-top: -30px; }
    .section { margin-bottom: 20px; }
    .section-title { font-size: 11px; font-weight: 700; color: #45474d; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; padding-bottom: 4px; border-bottom: 1px solid #e6e2d7; }
    .info-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; background: #F0ECE1; padding: 16px; border: 1px solid #ddd; margin-bottom: 20px; }
    .info-grid .label { font-size: 9px; color: #666; text-transform: uppercase; }
    .info-grid .value { font-size: 14px; font-weight: 700; margin-top: 2px; }
    table { width: 100%; border-collapse: collapse; font-size: 12px; }
    th { background: #16233A; color: white; padding: 8px 12px; text-align: left; font-size: 10px; font-weight: 700; }
    th.duty { background: #C0392B; }
    td { padding: 8px 12px; border-bottom: 1px solid #eee; }
    tr:nth-child(even) td { background: #fafaf5; }
    .right { text-align: right; }
    .center { text-align: center; }
    .not-applied td { color: #999; text-decoration: line-through; }
    .status { font-size: 10px; }
    .totals { margin-top: 20px; border-top: 3px double #16233A; padding-top: 12px; }
    .total-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
    .grand-total { background: #16233A; color: white; padding: 14px 20px; margin-top: 12px; display: flex; justify-content: space-between; align-items: center; }
    .grand-total .label { font-size: 13px; font-weight: 700; }
    .grand-total .value { font-size: 22px; font-weight: 700; }
    .notes { margin-top: 20px; font-size: 10px; color: #666; }
    .notes p { margin-bottom: 4px; }
    .disclaimer { margin-top: 30px; padding-top: 12px; border-top: 1px solid #ddd; font-size: 9px; color: #999; font-style: italic; }
    .de-minimis { background: #dcfce7; border: 1px solid #86efac; padding: 16px; color: #166534; font-size: 14px; font-weight: 600; }
    @media print { body { padding: 20px; } .no-print { display: none; } }
  </style>
</head>
<body>
  <button class="no-print" onclick="window.print()" style="position:fixed;top:10px;right:10px;background:#16233A;color:white;border:none;padding:10px 20px;cursor:pointer;font-size:14px;z-index:100;">
    พิมพ์ / บันทึก PDF
  </button>

  <div class="accent-bar"></div>
  <div class="header">
    <h1>ระบบคำนวณต้นทุนนำเข้า</h1>
    <div class="subtitle">ใบสรุปการประเมินภาษีนำเข้า</div>
    <div class="meta">
      เลขอ้างอิง: ${result.calculation_id.slice(0, 8).toUpperCase()}<br/>
      วันที่: ${new Date().toISOString().split("T")[0]}<br/>
      หน้า 1/1
    </div>
  </div>

  <div class="info-grid">
    <div><div class="label">รหัส HTS</div><div class="value">${result.hts_code}</div></div>
    <div><div class="label">ประเทศต้นทาง</div><div class="value">${result.origin_country}</div></div>
    <div><div class="label">วันที่นำเข้า</div><div class="value">${result.import_date}</div></div>
  </div>

  ${result.de_minimis_applied ? `
  <div class="de-minimis">
    ยกเว้นภาษี (DE MINIMIS) — มูลค่า ${fmt(result.customs_value_usd)} ต่ำกว่า $800 ไม่เสียภาษีและค่าธรรมเนียม
  </div>
  ` : `
  <div class="section">
    <div class="section-title">การประเมินมูลค่า</div>
    <table>
      <thead><tr><th>รายการ</th><th class="right">จำนวนเงิน (USD)</th></tr></thead>
      <tbody>
        <tr><td>มูลค่าตามใบกำกับสินค้า</td><td class="right">${fmt(result.invoice_value_usd)}</td></tr>
        <tr><td>+ ค่าขนส่งและประกัน</td><td class="right">${fmt(result.customs_value_usd - result.invoice_value_usd)}</td></tr>
        <tr style="font-weight:700"><td>มูลค่าศุลกากร (CIF)</td><td class="right">${fmt(result.customs_value_usd)}</td></tr>
      </tbody>
    </table>
  </div>

  <div class="section">
    <div class="section-title">การประเมินภาษี</div>
    <table>
      <thead><tr><th class="duty">ประเภทภาษี/ค่าธรรมเนียม</th><th class="duty center">อัตรา</th><th class="duty right">จำนวนเงิน (USD)</th><th class="duty center">สถานะ</th></tr></thead>
      <tbody>${tariffRows}</tbody>
    </table>
  </div>

  <div class="totals">
    <div class="total-row"><span>ภาษีรวม:</span><span>${fmt(result.total_duty_usd)}</span></div>
    ${result.fees ? `<div class="total-row"><span>ค่าธรรมเนียม (MPF + HMF):</span><span>${fmt(result.fees.total_fees_usd)}</span></div>` : ""}
  </div>

  <div class="grand-total">
    <span class="label">ต้นทุนนำเข้ารวมทั้งหมด</span>
    <span class="value">${fmt(result.landed_cost_usd)}</span>
  </div>

  <div class="notes">
    ${result.fta_applied ? `<p>ข้อตกลงการค้าเสรี: ${result.fta_applied} — ยกเว้นภาษี MFN สำหรับสินค้าที่เข้าเงื่อนไข</p>` : ""}
    ${result.fx_rate_used ? `<p>อัตราแลกเปลี่ยน: 1 ${result.fx_rate_used.from_currency} = ${result.fx_rate_used.rate} ${result.fx_rate_used.to_currency} (วันที่: ${result.fx_rate_used.date})</p>` : ""}
  </div>
  `}

  <div class="disclaimer">
    <p>หมายเหตุ: เอกสารนี้จัดทำโดยระบบ Landed Cost Ledger เพื่อการประมาณการเท่านั้น</p>
    <p>ไม่ถือเป็นคำแนะนำทางกฎหมายหรือศุลกากร กรุณาปรึกษาตัวแทนออกของ (Customs Broker) สำหรับการยื่นเอกสารจริง</p>
    <p>อัตราภาษีอ้างอิงจากข้อมูลที่มี อาจไม่สะท้อนการแก้ไขล่าสุดจาก Federal Register</p>
  </div>
</body>
</html>`;

  // Open new window and print
  const printWindow = window.open("", "_blank", "width=800,height=1000");
  if (printWindow) {
    printWindow.document.write(html);
    printWindow.document.close();
    // Auto-trigger print after a brief delay for rendering
    setTimeout(() => printWindow.print(), 500);
  }
}
