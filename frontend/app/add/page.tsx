"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { formatPaiseINR, parseIndianToPaise } from "@/lib/money";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(process.env.NEXT_PUBLIC_API_URL + url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}

async function postJSON<T>(url: string, body: any): Promise<T> {
  const res = await fetch(process.env.NEXT_PUBLIC_API_URL + url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export default function AddPage(){
  const qc = useQueryClient();
  const [txnType, setTxnType] = useState("CONTRIBUTION");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState<string>(new Date().toISOString().slice(0,10));
  const [posting, setPosting] = useState(true);
  const [fundFrom, setFundFrom] = useState("");
  const [fundTo, setFundTo] = useState("");
  const [personId, setPersonId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [party, setParty] = useState("");
  const [notes, setNotes] = useState("");

  const { data: people } = useQuery({ queryKey: ["people"], queryFn: ()=> fetchJSON<any[]>("/api/v1/people")});
  const { data: categories } = useQuery({ queryKey: ["categories"], queryFn: ()=> fetchJSON<any[]>("/api/v1/categories")});

  const create = useMutation({
    mutationFn: (body: any) => postJSON("/api/v1/transactions", body),
    onSuccess: ()=> {
      qc.invalidateQueries({ queryKey: ["funds"]});
      qc.invalidateQueries({ queryKey: ["summary"]});
      qc.invalidateQueries({ queryKey: ["txns"]});
      setAmount(""); setParty(""); setNotes("");
    }
  });

  const submit = () => {
    const payload: any = {
      txn_type: txnType,
      amount_paise: parseIndianToPaise(amount),
      date,
      posting,
      fund_from: fundFrom || null,
      fund_to: fundTo || null,
      person_id: personId || null,
      category_id: categoryId || null,
      party: party || null,
      notes: notes || null,
    };
    create.mutate(payload);
  };

  const needsFundTo = posting && (txnType === "CONTRIBUTION" || txnType === "INCOME" || txnType === "TRANSFER");
  const needsFundFrom = posting && (txnType === "EXPENSE" || txnType === "TRANSFER");
  const needsPerson = posting && txnType === "CONTRIBUTION";
  const needsCategory = posting && txnType === "EXPENSE";

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Add Entry</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Field label="Type">
          <select value={txnType} onChange={(e)=> setTxnType(e.target.value)} className="border rounded px-2 py-1">
            {['CONTRIBUTION','INCOME','EXPENSE','TRANSFER'].map(t=> <option key={t} value={t}>{t}</option>)}
          </select>
        </Field>
        <Field label="Amount (₹)"><input value={amount} onChange={(e)=> setAmount(e.target.value)} placeholder="1,50,000" className="border rounded px-2 py-1" /></Field>
        <Field label="Date"><input type="date" value={date} onChange={(e)=> setDate(e.target.value)} className="border rounded px-2 py-1" /></Field>
        <Field label="Posting"><input type="checkbox" checked={posting} onChange={(e)=> setPosting(e.target.checked)} /> <span className="ml-2">posting</span></Field>
        {needsPerson && (
          <Field label="Person">
            <select value={personId} onChange={(e)=> setPersonId(e.target.value)} className="border rounded px-2 py-1">
              <option value="">Select person</option>
              {(people || []).map((p:any)=> <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </Field>
        )}
        {needsCategory && (
          <Field label="Category">
            <select value={categoryId} onChange={(e)=> setCategoryId(e.target.value)} className="border rounded px-2 py-1">
              <option value="">Select category</option>
              {(categories || []).map((c:any)=> <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </Field>
        )}
        {needsFundFrom && (
          <Field label="Fund From">
            <select value={fundFrom} onChange={(e)=> setFundFrom(e.target.value)} className="border rounded px-2 py-1">
              <option value="">Select fund</option>
              {['CASH','ONLINE_A','ONLINE_Y'].map(f=> <option key={f} value={f}>{f}</option>)}
            </select>
          </Field>
        )}
        {needsFundTo && (
          <Field label="Fund To">
            <select value={fundTo} onChange={(e)=> setFundTo(e.target.value)} className="border rounded px-2 py-1">
              <option value="">Select fund</option>
              {['CASH','ONLINE_A','ONLINE_Y'].map(f=> <option key={f} value={f}>{f}</option>)}
            </select>
          </Field>
        )}
        <Field label="Party/Vendor (optional)"><input value={party} onChange={(e)=> setParty(e.target.value)} className="border rounded px-2 py-1" /></Field>
        <Field label="Notes"><input value={notes} onChange={(e)=> setNotes(e.target.value)} className="border rounded px-2 py-1" /></Field>
      </div>
      <button onClick={submit} className="bg-blue-600 text-white px-4 py-2 rounded">Create</button>
    </div>
  );
}

function Field({ label, children }:{label:string; children: React.ReactNode}){
  return (
    <div>
      <label className="block text-xs text-slate-600 mb-1">{label}</label>
      {children}
    </div>
  );
}
