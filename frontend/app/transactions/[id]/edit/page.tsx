"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { parseIndianToPaise, formatPaiseINR } from "@/lib/money";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(process.env.NEXT_PUBLIC_API_URL + url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}

export default function EditTxnPage(){
  const params = useParams();
  const id = params?.id as string;
  const router = useRouter();
  const qc = useQueryClient();

  const { data: txn } = useQuery({ queryKey: ["txn", id], queryFn: ()=> fetchJSON<any>(`/api/v1/transactions/${id}`)});

  const [txnType, setTxnType] = useState("");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState("");
  const [posting, setPosting] = useState(true);
  const [fundFrom, setFundFrom] = useState("");
  const [fundTo, setFundTo] = useState("");
  const [personId, setPersonId] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [party, setParty] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(()=>{
    if (!txn) return;
    setTxnType(txn.txn_type);
    setAmount(String((txn.amount_paise||0)/100));
    setDate(txn.date);
    setPosting(Boolean(txn.posting));
    setFundFrom(txn.fund_from || "");
    setFundTo(txn.fund_to || "");
    setPersonId(txn.person_id || "");
    setCategoryId(txn.category_id || "");
    setParty(txn.party || "");
    setNotes(txn.notes || "");
  }, [txn]);

  const update = useMutation({
    mutationFn: async () => {
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
      const res = await fetch(process.env.NEXT_PUBLIC_API_URL + `/api/v1/transactions/${id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload)});
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    },
    onSuccess: ()=>{
      qc.invalidateQueries({ queryKey: ["txns"]});
      qc.invalidateQueries({ queryKey: ["funds"]});
      router.push("/transactions");
    }
  });

  if (!txn) return <div className="p-4">Loading…</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Edit Transaction</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Field label="Type">
          <select value={txnType} onChange={(e)=> setTxnType(e.target.value)} className="border rounded px-2 py-1">
            {['CONTRIBUTION','INCOME','EXPENSE','TRANSFER'].map(t=> <option key={t} value={t}>{t}</option>)}
          </select>
        </Field>
        <Field label="Amount (₹)"><input value={amount} onChange={(e)=> setAmount(e.target.value)} className="border rounded px-2 py-1" /></Field>
        <Field label="Date"><input type="date" value={date} onChange={(e)=> setDate(e.target.value)} className="border rounded px-2 py-1" /></Field>
        <Field label="Posting"><input type="checkbox" checked={posting} onChange={(e)=> setPosting(e.target.checked)} /> <span className="ml-2">posting</span></Field>
        <Field label="Fund From">
          <select value={fundFrom} onChange={(e)=> setFundFrom(e.target.value)} className="border rounded px-2 py-1">
            <option value="">—</option>
            {['CASH','ONLINE_A','ONLINE_Y'].map(f=> <option key={f} value={f}>{f}</option>)}
          </select>
        </Field>
        <Field label="Fund To">
          <select value={fundTo} onChange={(e)=> setFundTo(e.target.value)} className="border rounded px-2 py-1">
            <option value="">—</option>
            {['CASH','ONLINE_A','ONLINE_Y'].map(f=> <option key={f} value={f}>{f}</option>)}
          </select>
        </Field>
        <Field label="Person ID"><input value={personId} onChange={(e)=> setPersonId(e.target.value)} className="border rounded px-2 py-1" /></Field>
        <Field label="Category ID"><input value={categoryId} onChange={(e)=> setCategoryId(e.target.value)} className="border rounded px-2 py-1" /></Field>
        <Field label="Party"><input value={party} onChange={(e)=> setParty(e.target.value)} className="border rounded px-2 py-1" /></Field>
        <Field label="Notes"><input value={notes} onChange={(e)=> setNotes(e.target.value)} className="border rounded px-2 py-1" /></Field>
      </div>
      <button onClick={()=> update.mutate()} className="bg-blue-600 text-white px-4 py-2 rounded">Save</button>
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
