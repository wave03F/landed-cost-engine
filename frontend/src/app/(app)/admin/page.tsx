"use client";

import { useState, useEffect } from "react";
import type { TariffRule, Exclusion, FXRate, HTSCode } from "@/lib/types";
import {
  listTariffRules, createTariffRule,
  listExclusions, createExclusion,
  listFXRates, createFXRate,
  searchHTSCodes, createHTSCode,
  ApiRequestError,
} from "@/lib/api";

type Tab = "rules" | "exclusions" | "fx" | "hts";

const TABS: { key: Tab; label: string; icon: string }[] = [
  { key: "rules", label: "Tariff Rules", icon: "gavel" },
  { key: "exclusions", label: "Exclusions", icon: "rule" },
  { key: "fx", label: "FX Rates", icon: "currency_exchange" },
  { key: "hts", label: "HTS Codes", icon: "category" },
];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<Tab>("rules");

  return (
    <div className="bg-manifest-paper text-on-surface noise-bg border border-steel-blue/30 shadow-[0_10px_30px_rgba(0,0,0,0.5)] rounded-sm relative overflow-hidden">
      <div className="h-2 bg-on-surface-variant w-full flex-shrink-0" />
      <div className="px-8 py-6 border-b border-steel-blue/20 bg-surface-container-low/50">
        <p className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase tracking-widest">
          Administration
        </p>
        <h2 className="font-headline-lg text-headline-lg text-primary">System Settings</h2>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-steel-blue/20 px-8 overflow-x-auto">
        {TABS.map(({ key, label, icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 px-4 py-3 font-label-caps text-label-caps uppercase tracking-widest transition-colors border-b-2 whitespace-nowrap ${
              activeTab === key
                ? "border-ink-navy text-primary"
                : "border-transparent text-on-surface-variant hover:text-primary"
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">{icon}</span>
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === "rules" && <TariffRulesTab />}
        {activeTab === "exclusions" && <ExclusionsTab />}
        {activeTab === "fx" && <FXRatesTab />}
        {activeTab === "hts" && <HTSCodesTab />}
      </div>
    </div>
  );
}

// =============================================================================
// Tariff Rules Tab
// =============================================================================

function TariffRulesTab() {
  const [items, setItems] = useState<TariffRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    try { setItems(await listTariffRules()); } catch {}
    setLoading(false);
  };

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const fd = new FormData(e.currentTarget);
    try {
      await createTariffRule({
        tariff_type: fd.get("tariff_type") as any,
        hts_code_pattern: fd.get("hts_code_pattern") as string,
        origin_country: fd.get("origin_country") as string || "CN",
        rate: parseFloat(fd.get("rate") as string),
        effective_from: fd.get("effective_from") as string,
        effective_to: (fd.get("effective_to") as string) || undefined,
        stacks_with: (fd.get("stacks_with") as string).split(",").map(s => s.trim()).filter(Boolean),
        mutually_exclusive_with: (fd.get("mutually_exclusive_with") as string).split(",").map(s => s.trim()).filter(Boolean),
        description: fd.get("description") as string,
        source_reference: fd.get("source_reference") as string,
      });
      setShowForm(false);
      load();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Failed to create");
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="font-code-sm text-code-sm text-on-surface-variant">{items.length} rules</p>
        <button onClick={() => setShowForm(!showForm)} className="bg-secondary text-on-secondary font-label-caps text-label-caps px-4 py-2 uppercase tracking-wider hover:bg-secondary/90 transition-colors">
          {showForm ? "Cancel" : "+ Add Rule"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="border border-steel-blue/20 p-4 mb-4 bg-surface-container-low/50 grid grid-cols-2 gap-3">
          <select name="tariff_type" required className="col-span-1 border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent">
            <option value="MFN">MFN</option>
            <option value="SECTION_301">SECTION_301</option>
            <option value="SECTION_232">SECTION_232</option>
            <option value="IEEPA">IEEPA</option>
            <option value="AD_CVD">AD_CVD</option>
          </select>
          <input name="hts_code_pattern" placeholder="HTS Pattern (e.g. 8483)" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="origin_country" placeholder="Origin (CN)" defaultValue="CN" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="rate" type="number" step="0.0001" placeholder="Rate (e.g. 0.25)" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="effective_from" type="date" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="effective_to" type="date" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="stacks_with" placeholder="Stacks with (MFN)" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="mutually_exclusive_with" placeholder="Exclusive with (IEEPA)" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="description" placeholder="Description" className="col-span-2 border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="source_reference" placeholder="Source reference" className="col-span-2 border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          {error && <p className="col-span-2 text-error text-[12px]">{error}</p>}
          <button type="submit" className="col-span-2 bg-ink-navy text-on-primary font-label-caps text-label-caps py-2 uppercase tracking-wider">Create Rule</button>
        </form>
      )}

      {loading ? <p className="text-center py-8 animate-pulse font-label-caps text-label-caps">Loading...</p> : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px] font-code-sm">
            <thead>
              <tr className="bg-ink-navy text-on-primary text-left">
                <th className="p-2">Type</th><th className="p-2">Pattern</th><th className="p-2">Origin</th><th className="p-2">Rate</th><th className="p-2">From</th><th className="p-2">To</th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.id} className="border-b border-steel-blue/10 hover:bg-surface-container-high/30">
                  <td className="p-2 font-bold">{r.tariff_type}</td>
                  <td className="p-2">{r.hts_code_pattern}</td>
                  <td className="p-2">{r.origin_country}</td>
                  <td className="p-2 text-duty-red">{(r.rate * 100).toFixed(2)}%</td>
                  <td className="p-2">{r.effective_from}</td>
                  <td className="p-2">{r.effective_to ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Exclusions Tab
// =============================================================================

function ExclusionsTab() {
  const [items, setItems] = useState<Exclusion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    try { setItems(await listExclusions()); } catch {}
    setLoading(false);
  };

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const fd = new FormData(e.currentTarget);
    try {
      await createExclusion({
        hts_code: fd.get("hts_code") as string,
        tariff_type: fd.get("tariff_type") as any,
        origin_country: fd.get("origin_country") as string || "CN",
        effective_from: fd.get("effective_from") as string,
        effective_to: (fd.get("effective_to") as string) || undefined,
        description: fd.get("description") as string,
        source_reference: fd.get("source_reference") as string,
      });
      setShowForm(false);
      load();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Failed to create");
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="font-code-sm text-code-sm text-on-surface-variant">{items.length} exclusions</p>
        <button onClick={() => setShowForm(!showForm)} className="bg-secondary text-on-secondary font-label-caps text-label-caps px-4 py-2 uppercase tracking-wider hover:bg-secondary/90 transition-colors">
          {showForm ? "Cancel" : "+ Add Exclusion"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="border border-steel-blue/20 p-4 mb-4 bg-surface-container-low/50 grid grid-cols-2 gap-3">
          <input name="hts_code" placeholder="HTS Code (e.g. 8542.31)" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <select name="tariff_type" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent">
            <option value="SECTION_301">SECTION_301</option>
            <option value="SECTION_232">SECTION_232</option>
            <option value="IEEPA">IEEPA</option>
          </select>
          <input name="origin_country" placeholder="Origin (CN)" defaultValue="CN" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="effective_from" type="date" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="effective_to" type="date" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="description" placeholder="Description" className="col-span-2 border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="source_reference" placeholder="Source reference" className="col-span-2 border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          {error && <p className="col-span-2 text-error text-[12px]">{error}</p>}
          <button type="submit" className="col-span-2 bg-ink-navy text-on-primary font-label-caps text-label-caps py-2 uppercase tracking-wider">Create Exclusion</button>
        </form>
      )}

      {loading ? <p className="text-center py-8 animate-pulse font-label-caps text-label-caps">Loading...</p> : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px] font-code-sm">
            <thead>
              <tr className="bg-ink-navy text-on-primary text-left">
                <th className="p-2">HTS</th><th className="p-2">Type</th><th className="p-2">Origin</th><th className="p-2">From</th><th className="p-2">To</th><th className="p-2">Description</th>
              </tr>
            </thead>
            <tbody>
              {items.map((e) => (
                <tr key={e.id} className="border-b border-steel-blue/10 hover:bg-surface-container-high/30">
                  <td className="p-2 font-bold">{e.hts_code}</td>
                  <td className="p-2">{e.tariff_type}</td>
                  <td className="p-2">{e.origin_country}</td>
                  <td className="p-2">{e.effective_from}</td>
                  <td className="p-2">{e.effective_to ?? "—"}</td>
                  <td className="p-2 truncate max-w-[200px]">{e.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// FX Rates Tab
// =============================================================================

function FXRatesTab() {
  const [items, setItems] = useState<FXRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    try { setItems(await listFXRates()); } catch {}
    setLoading(false);
  };

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const fd = new FormData(e.currentTarget);
    try {
      await createFXRate({
        from_currency: fd.get("from_currency") as string || "CNY",
        to_currency: fd.get("to_currency") as string || "USD",
        rate: parseFloat(fd.get("rate") as string),
        date: fd.get("date") as string,
      });
      setShowForm(false);
      load();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Failed to create");
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="font-code-sm text-code-sm text-on-surface-variant">{items.length} rates</p>
        <button onClick={() => setShowForm(!showForm)} className="bg-secondary text-on-secondary font-label-caps text-label-caps px-4 py-2 uppercase tracking-wider hover:bg-secondary/90 transition-colors">
          {showForm ? "Cancel" : "+ Add Rate"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="border border-steel-blue/20 p-4 mb-4 bg-surface-container-low/50 grid grid-cols-2 gap-3">
          <input name="from_currency" placeholder="From (CNY)" defaultValue="CNY" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="to_currency" placeholder="To (USD)" defaultValue="USD" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="rate" type="number" step="0.0001" placeholder="Rate (e.g. 0.1389)" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="date" type="date" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          {error && <p className="col-span-2 text-error text-[12px]">{error}</p>}
          <button type="submit" className="col-span-2 bg-ink-navy text-on-primary font-label-caps text-label-caps py-2 uppercase tracking-wider">Add Rate</button>
        </form>
      )}

      {loading ? <p className="text-center py-8 animate-pulse font-label-caps text-label-caps">Loading...</p> : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px] font-code-sm">
            <thead>
              <tr className="bg-ink-navy text-on-primary text-left">
                <th className="p-2">From</th><th className="p-2">To</th><th className="p-2">Rate</th><th className="p-2">Date</th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.id} className="border-b border-steel-blue/10 hover:bg-surface-container-high/30">
                  <td className="p-2">{r.from_currency}</td>
                  <td className="p-2">{r.to_currency}</td>
                  <td className="p-2 font-bold">{r.rate}</td>
                  <td className="p-2">{r.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// HTS Codes Tab
// =============================================================================

function HTSCodesTab() {
  const [items, setItems] = useState<HTSCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    try { setItems(await searchHTSCodes("")); } catch {}
    setLoading(false);
  };

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    const fd = new FormData(e.currentTarget);
    try {
      await createHTSCode({
        code: fd.get("code") as string,
        description: fd.get("description") as string,
        parent_code: (fd.get("parent_code") as string) || undefined,
      });
      setShowForm(false);
      load();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Failed to create");
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="font-code-sm text-code-sm text-on-surface-variant">{items.length} codes</p>
        <button onClick={() => setShowForm(!showForm)} className="bg-secondary text-on-secondary font-label-caps text-label-caps px-4 py-2 uppercase tracking-wider hover:bg-secondary/90 transition-colors">
          {showForm ? "Cancel" : "+ Add Code"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="border border-steel-blue/20 p-4 mb-4 bg-surface-container-low/50 grid grid-cols-2 gap-3">
          <input name="code" placeholder="Code (e.g. 8483.40)" required className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="parent_code" placeholder="Parent code (e.g. 8483)" className="border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          <input name="description" placeholder="Description" required className="col-span-2 border border-steel-blue/40 p-2 font-code-sm text-code-sm bg-transparent" />
          {error && <p className="col-span-2 text-error text-[12px]">{error}</p>}
          <button type="submit" className="col-span-2 bg-ink-navy text-on-primary font-label-caps text-label-caps py-2 uppercase tracking-wider">Add HTS Code</button>
        </form>
      )}

      {loading ? <p className="text-center py-8 animate-pulse font-label-caps text-label-caps">Loading...</p> : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px] font-code-sm">
            <thead>
              <tr className="bg-ink-navy text-on-primary text-left">
                <th className="p-2">Code</th><th className="p-2">Level</th><th className="p-2">Description</th><th className="p-2">Parent</th>
              </tr>
            </thead>
            <tbody>
              {items.map((c) => (
                <tr key={c.id} className="border-b border-steel-blue/10 hover:bg-surface-container-high/30">
                  <td className="p-2 font-bold">{c.code}</td>
                  <td className="p-2"><span className="bg-steel-blue/10 px-1.5 py-0.5 text-[10px] uppercase">{c.level}</span></td>
                  <td className="p-2 truncate max-w-[300px]">{c.description}</td>
                  <td className="p-2">{c.parent_code ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
