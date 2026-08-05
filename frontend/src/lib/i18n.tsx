"use client";

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

// =============================================================================
// Types
// =============================================================================

export type Locale = "en" | "th";

type TranslationDict = Record<string, string>;

// =============================================================================
// Translations
// =============================================================================

const translations: Record<Locale, TranslationDict> = {
  en: {
    // App
    "app.title": "Landed Cost Ledger",
    "app.subtitle": "Official Ledger v4.1",
    "app.brand": "Duty Manifest",
    "app.new_entry": "New Entry",

    // Nav
    "nav.calculator": "Calculator",
    "nav.compare": "Compare",
    "nav.hts_browser": "HTS Browser",
    "nav.history": "History",
    "nav.settings": "Settings",
    "nav.support": "Support",
    "nav.sign_out": "Sign Out",
    "nav.dashboard": "Dashboard",
    "nav.manifests": "Manifests",
    "nav.compliance": "Compliance",

    // Calculator
    "calc.form_title": "Form 7501 - Entry Summary",
    "calc.page_title": "Duty Calculator",
    "calc.quick_estimate": "Quick Estimate",
    "calc.full_calculator": "Full Calculator",
    "calc.try_example": "Try Example — Industrial Gears from China",
    "calc.hts_code": "HTS Code (Harmonized Tariff Schedule)",
    "calc.hts_hint": "Product classification code (e.g. 8483.40 = gears). Find yours in HTS Browser.",
    "calc.item_value": "Item Value (USD)",
    "calc.item_value_hint": "Invoice/commercial value of goods",
    "calc.import_date": "Date of Import",
    "calc.import_date_hint": "Determines which tariff rules are in effect",
    "calc.freight": "Freight Cost",
    "calc.freight_hint": "Shipping cost to US port",
    "calc.insurance": "Insurance",
    "calc.insurance_hint": "Cargo insurance premium",
    "calc.origin": "Country of Origin",
    "calc.origin_hint": "China: 301/232/IEEPA tariffs apply. MX/CA: USMCA duty-free on MFN.",
    "calc.submit": "Calculate Assessment",
    "calc.calculating": "Calculating...",
    "calc.total_landed_cost": "Total Landed Cost",
    "calc.customs_value": "Customs Value (CIF)",
    "calc.invoice_value": "Invoice Value",
    "calc.total_duty": "Total Duty",
    "calc.de_minimis": "De Minimis Applied — No duties (value under $800)",

    // Empty state
    "calc.how_it_works": "How it works",
    "calc.step_1": "1. Enter your product's HTS code (find it in HTS Browser)",
    "calc.step_2": "2. Enter the commercial value and import date",
    "calc.step_3": "3. Click \"Calculate Assessment\" to see full duty breakdown",
    "calc.preview_note": "This is a sample preview. Click \"Try Example\" or fill the form to get real results.",

    // HTS Browser
    "hts.title": "HTS Browser",
    "hts.search_placeholder": "Search by HTS code or item description (e.g., 8517.12)",
    "hts.search_btn": "Search",
    "hts.empty": "Search HTS codes by number or description",
    "hts.rate_summary": "Rate Summary",
    "hts.select_to_view": "Select a code to view rates",
    "hts.total_duty": "Estimated Total Duty",
    "hts.use_in_calc": "Use in Calculator",
    "hts.no_rules": "No tariff rules found for this code",
    "hts.loading": "Loading rates...",
    "hts.chapter": "Chapter",
    "hts.heading": "Heading",

    // History
    "history.title": "Calculation History",
    "history.subtitle": "Audit Trail",
    "history.empty": "No calculations recorded yet",
    "history.loading": "Loading records...",

    // Admin
    "admin.title": "System Settings",
    "admin.subtitle": "Administration",
    "admin.coming_soon": "management — Coming soon",

    // Common
    "common.search": "Search manifest...",
  },
  th: {
    // App
    "app.title": "ระบบคำนวณต้นทุนนำเข้า",
    "app.subtitle": "บัญชีอย่างเป็นทางการ v4.1",
    "app.brand": "ใบรายงานภาษี",
    "app.new_entry": "รายการใหม่",

    // Nav
    "nav.calculator": "คำนวณภาษี",
    "nav.compare": "เปรียบเทียบ",
    "nav.hts_browser": "ค้นหารหัส HTS",
    "nav.history": "ประวัติ",
    "nav.settings": "ตั้งค่า",
    "nav.support": "ช่วยเหลือ",
    "nav.sign_out": "ออกจากระบบ",
    "nav.dashboard": "แดชบอร์ด",
    "nav.manifests": "ใบรายงาน",
    "nav.compliance": "การปฏิบัติตามกฎ",

    // Calculator
    "calc.form_title": "แบบฟอร์ม 7501 - สรุปรายการนำเข้า",
    "calc.page_title": "เครื่องคำนวณภาษีนำเข้า",
    "calc.quick_estimate": "ประมาณการเร็ว",
    "calc.full_calculator": "คำนวณเต็มรูปแบบ",
    "calc.try_example": "ลองตัวอย่าง — เฟืองอุตสาหกรรมจากจีน",
    "calc.hts_code": "รหัส HTS (พิกัดศุลกากร)",
    "calc.hts_hint": "รหัสจำแนกสินค้า เช่น 8483.40 = เฟือง ค้นหาได้ที่หน้า HTS Browser",
    "calc.item_value": "มูลค่าสินค้า (USD)",
    "calc.item_value_hint": "มูลค่าตามใบกำกับสินค้า/ใบแจ้งหนี้",
    "calc.import_date": "วันที่นำเข้า",
    "calc.import_date_hint": "กำหนดว่าจะใช้กฎภาษีเวอร์ชันไหน",
    "calc.freight": "ค่าขนส่ง",
    "calc.freight_hint": "ค่าขนส่งถึงท่าเรือสหรัฐฯ",
    "calc.insurance": "ค่าประกัน",
    "calc.insurance_hint": "เบี้ยประกันสินค้า",
    "calc.origin": "ประเทศต้นทาง",
    "calc.origin_hint": "จีน: โดนภาษี 301/232/IEEPA, เม็กซิโก/แคนาดา: ยกเว้น MFN ตาม USMCA",
    "calc.submit": "คำนวณภาษี",
    "calc.calculating": "กำลังคำนวณ...",
    "calc.total_landed_cost": "ต้นทุนนำเข้ารวมทั้งหมด",
    "calc.customs_value": "มูลค่าศุลกากร (CIF)",
    "calc.invoice_value": "มูลค่าสินค้า",
    "calc.total_duty": "ภาษีรวม",
    "calc.de_minimis": "De Minimis — ไม่เสียภาษี (มูลค่าต่ำกว่า $800)",

    // Empty state
    "calc.how_it_works": "วิธีใช้งาน",
    "calc.step_1": "1. กรอกรหัส HTS ของสินค้า (ค้นหาได้ที่หน้า HTS Browser)",
    "calc.step_2": "2. กรอกมูลค่าสินค้าและวันที่นำเข้า",
    "calc.step_3": "3. กดปุ่ม \"คำนวณภาษี\" เพื่อดูรายละเอียดภาษีทุกชั้น",
    "calc.preview_note": "นี่คือตัวอย่าง กดปุ่ม \"ลองตัวอย่าง\" หรือกรอกข้อมูลจริงเพื่อคำนวณ",

    // HTS Browser
    "hts.title": "ค้นหารหัส HTS",
    "hts.search_placeholder": "ค้นหาด้วยรหัส HTS หรือคำอธิบาย (เช่น 8517.12)",
    "hts.search_btn": "ค้นหา",
    "hts.empty": "ค้นหารหัส HTS ด้วยตัวเลขหรือคำอธิบาย",
    "hts.rate_summary": "สรุปอัตราภาษี",
    "hts.select_to_view": "เลือกรหัสเพื่อดูอัตราภาษี",
    "hts.total_duty": "ประมาณการภาษีรวม",
    "hts.use_in_calc": "ใช้ในเครื่องคำนวณ",
    "hts.no_rules": "ไม่พบกฎภาษีสำหรับรหัสนี้",
    "hts.loading": "กำลังโหลดอัตราภาษี...",
    "hts.chapter": "หมวด",
    "hts.heading": "ตอน",

    // History
    "history.title": "ประวัติการคำนวณ",
    "history.subtitle": "บันทึกตรวจสอบ",
    "history.empty": "ยังไม่มีประวัติการคำนวณ",
    "history.loading": "กำลังโหลด...",

    // Admin
    "admin.title": "ตั้งค่าระบบ",
    "admin.subtitle": "การจัดการ",
    "admin.coming_soon": "— เร็วๆ นี้",

    // Common
    "common.search": "ค้นหา...",
  },
};

// =============================================================================
// Context
// =============================================================================

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType>({
  locale: "en",
  setLocale: () => {},
  t: (key) => key,
});

// =============================================================================
// Provider
// =============================================================================

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>("en");

  const t = useCallback(
    (key: string): string => {
      return translations[locale][key] ?? translations.en[key] ?? key;
    },
    [locale]
  );

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

// =============================================================================
// Hook
// =============================================================================

export function useI18n() {
  return useContext(I18nContext);
}

// =============================================================================
// Language Switcher Component
// =============================================================================

export function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();

  return (
    <button
      onClick={() => setLocale(locale === "en" ? "th" : "en")}
      className="flex items-center gap-1.5 px-3 py-1.5 bg-brass text-ink-navy text-[12px] font-label-caps font-bold uppercase tracking-wider hover:bg-brass/80 transition-colors rounded-sm shadow-sm"
      title={locale === "en" ? "เปลี่ยนเป็นภาษาไทย" : "Switch to English"}
    >
      <span className="material-symbols-outlined text-[16px]">translate</span>
      <span>{locale === "en" ? "ไทย" : "ENG"}</span>
    </button>
  );
}
