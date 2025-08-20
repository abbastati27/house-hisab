"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { formatPaiseINR } from "@/lib/money";
import Link from "next/link";
import { SwipeableRow } from "@/components/swipeable-row";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(process.env.NEXT_PUBLIC_API_URL + url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}

type Txn = {
  id: string;
  date: string;
  txn_type: string;
  amount_paise: number;
  fund_from?: string | null;
  fund_to?: string | null;
  person_id?: string | null;
  category_id?: string | null;
  party?: string | null;
  notes?: string | null;
  posting: boolean;
};

type SortKey = keyof Txn;

export default function TransactionsPage() {
  const qc = useQueryClient();
  const [type, setType] = useState<string>("");
  const [fund, setFund] = useState<string>("");
  const [q, setQ] = useState<string>("");
  const [posting, setPosting] = useState<boolean | "">("");

  // sorting
  const [sortKey, setSortKey] = useState<SortKey>("category_id");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const params = new URLSearchParams();
  if (type) params.set("type", type);
  if (fund) params.set("fund", fund);
  if (q) params.set("q", q);
  if (posting !== "") params.set("posting", String(posting));

  const { data } = useQuery({
    queryKey: ["txns", params.toString()],
    queryFn: () => fetchJSON<Txn[]>(`/api/v1/transactions?${params.toString()}`),
  });

  const del = useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + `/api/v1/transactions/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed");
      return res.json();
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["txns"] }),
  });

  const sorted = useMemo(() => {
    const arr = (data || []).slice();
    const dir = sortDir === "asc" ? 1 : -1;
    arr.sort((a, b) => {
      const va = getValue(a, sortKey);
      const vb = getValue(b, sortKey);
      if (typeof va === "number" && typeof vb === "number") return (va - vb) * dir;
      const sa = String(va ?? "");
      const sb = String(vb ?? "");
      return sa.localeCompare(sb) * dir;
    });
    return arr;
  }, [data, sortKey, sortDir]);

  function onSort(key: SortKey) {
    if (key === sortKey) setSortDir(sortDir === "asc" ? "desc" : "asc");
    else { setSortKey(key); setSortDir("asc"); }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Transactions</h1>
      <div className="flex flex-wrap gap-2 items-end">
        <Select label="Type" value={type} onChange={setType} options={["", "CONTRIBUTION", "INCOME", "EXPENSE", "TRANSFER"]} />
        <Select label="Fund" value={fund} onChange={setFund} options={["", "CASH", "ONLINE_A", "ONLINE_Y"]} />
        <Select label="Posting" value={posting === "" ? "" : String(posting)} onChange={(v)=> setPosting(v===""?"": v==="true")} options={["", "true", "false"]} />
        <div className="flex-1 min-w-[160px]">
          <label className="block text-xs text-slate-600">Search</label>
          <input value={q} onChange={(e)=> setQ(e.target.value)} className="w-full border rounded px-3 py-2" placeholder="notes/party" />
        </div>
      </div>

      {/* Mobile list */}
      <div className="md:hidden divide-y rounded border bg-white">
        {sorted.map((t) => (
          <SwipeableRow
            key={t.id}
            rightActions={
              <div className="flex gap-2">
                <Link href={`/transactions/edit?id=${encodeURIComponent(t.id)}`} className="bg-blue-600 text-white px-3 py-2 rounded self-center">Edit</Link>
                <button onClick={()=> del.mutate(t.id)} className="bg-red-600 text-white px-3 py-2 rounded self-center">Delete</button>
              </div>
            }
          >
            <Link href={`/transactions/edit?id=${encodeURIComponent(t.id)}`} className="block p-3">
              <div className="flex justify-between text-sm">
                <div className="font-medium">{t.txn_type} • {t.category_id || t.person_id || t.party || "—"}</div>
                <div>{formatPaiseINR(t.amount_paise)}</div>
              </div>
              <div className="text-xs text-slate-600">{t.date} • {t.fund_from || ""}{t.fund_from && t.fund_to ? " → " : ""}{t.fund_to || ""}</div>
              {t.notes && <div className="text-xs mt-1">{t.notes}</div>}
            </Link>
          </SwipeableRow>
        ))}
      </div>

      {/* Desktop table */}
      <div className="hidden md:block rounded border bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-left">
              <SortableTh active={sortKey==="date"} dir={sortDir} onClick={()=> onSort("date")}>Date</SortableTh>
              <SortableTh active={sortKey==="txn_type"} dir={sortDir} onClick={()=> onSort("txn_type")}>Type</SortableTh>
              <SortableTh active={sortKey==="amount_paise"} dir={sortDir} onClick={()=> onSort("amount_paise")}>Amount</SortableTh>
              <SortableTh active={sortKey==="fund_from"} dir={sortDir} onClick={()=> onSort("fund_from")}>From</SortableTh>
              <SortableTh active={sortKey==="fund_to"} dir={sortDir} onClick={()=> onSort("fund_to")}>To</SortableTh>
              <SortableTh active={sortKey==="person_id"} dir={sortDir} onClick={()=> onSort("person_id")}>Person</SortableTh>
              <SortableTh active={sortKey==="category_id"} dir={sortDir} onClick={()=> onSort("category_id")}>Category</SortableTh>
              <SortableTh active={sortKey==="party"} dir={sortDir} onClick={()=> onSort("party")}>Party</SortableTh>
              <SortableTh active={sortKey==="notes"} dir={sortDir} onClick={()=> onSort("notes")}>Notes</SortableTh>
              <SortableTh active={sortKey==="posting"} dir={sortDir} onClick={()=> onSort("posting")}>Posting</SortableTh>
              <th className="p-2"></th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((t) => (
              <tr key={t.id} className="border-t">
                <td className="p-2">{t.date}</td>
                <td className="p-2">{t.txn_type}</td>
                <td className="p-2">{formatPaiseINR(t.amount_paise)}</td>
                <td className="p-2">{t.fund_from ?? ""}</td>
                <td className="p-2">{t.fund_to ?? ""}</td>
                <td className="p-2">{t.person_id ?? ""}</td>
                <td className="p-2">{t.category_id ?? ""}</td>
                <td className="p-2">{t.party ?? ""}</td>
                <td className="p-2">{t.notes ?? ""}</td>
                <td className="p-2">{String(t.posting)}</td>
                <td className="p-2 text-right">
                  <div className="flex gap-2 justify-end">
                    <Link href={`/transactions/edit?id=${encodeURIComponent(t.id)}`} className="text-blue-600 hover:underline">Edit</Link>
                    <button onClick={()=> del.mutate(t.id)} className="text-red-600 hover:underline">Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function getValue(t: Txn, key: SortKey): string | number | boolean | null | undefined {
  if (key === "amount_paise") return t.amount_paise;
  if (key === "posting") return t.posting ? 1 : 0;
  return (t as any)[key];
}

function SortableTh({ children, onClick, active, dir }:{children: React.ReactNode; onClick: ()=>void; active: boolean; dir: "asc" | "desc"}){
  return (
    <th className="p-2 select-none">
      <button onClick={onClick} className={`inline-flex items-center gap-1 ${active ? "underline" : ""}`}>
        {children}
        {active && (dir === "asc" ? "▲" : "▼")}
      </button>
    </th>
  );
}

function Select({ label, value, onChange, options }:{label:string; value:any; onChange:(v:any)=>void; options:string[]}){
  return (
    <div>
      <label className="block text-xs text-slate-600">{label}</label>
      <select value={value as any} onChange={(e)=> onChange(e.target.value)} className="border rounded px-2 py-1">
        {options.map((opt)=> <option key={opt} value={opt}>{opt === "" ? "Any" : opt}</option>)}
      </select>
    </div>
  );
}
