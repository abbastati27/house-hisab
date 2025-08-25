"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart } from "@/components/bar-chart";

function formatINR(paise: number): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(paise / 100);
}

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(process.env.NEXT_PUBLIC_API_URL + url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed");
  return res.json();
}

export default function Page() {
  const { data: funds } = useQuery({
    queryKey: ["funds"],
    queryFn: () => fetchJSON<{ cash: number; online_a: number; online_y: number; total: number }>("/api/v1/funds"),
  });
  const { data: summary } = useQuery({
    queryKey: ["summary", "posting=false"],
    queryFn: () => fetchJSON<{ total_contributions: number; total_income: number; total_expenses: number; stored_total_funds: number; discrepancy: number }>("/api/v1/reports/summary?posting=false"),
  });
  const { data: topCats } = useQuery({
    queryKey: ["top-categories", "posting=false"],
    queryFn: () => fetchJSON<Array<{ id: string | null; name: string | null; total_paise: number }>>("/api/v1/reports/top-categories?limit=8&posting=false"),
  });
  const { data: topPeople } = useQuery({
    queryKey: ["top-people", "posting=false"],
    queryFn: () => fetchJSON<Array<{ id: string | null; name: string | null; total_paise: number }>>("/api/v1/reports/top-people?limit=8&posting=false"),
  });

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card title="Cash" value={funds ? formatINR(funds.cash) : "—"} />
        <Card title="Online A" value={funds ? formatINR(funds.online_a) : "—"} />
        <Card title="Online Y" value={funds ? formatINR(funds.online_y) : "—"} />
        <Card title="Total Funds" value={funds ? formatINR(funds.total) : "—"} />
      </div>

      {summary && summary.discrepancy !== 0 && (
        <div className="p-3 rounded bg-amber-100 border border-amber-300 text-amber-900">
          Equation discrepancy detected: {formatINR(summary.discrepancy)}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Totals">
          <ul className="space-y-1">
            <li>Contributions: {summary ? formatINR(summary.total_contributions) : "—"}</li>
            <li>Income: {summary ? formatINR(summary.total_income) : "—"}</li>
            <li>Expenses: {summary ? formatINR(summary.total_expenses) : "—"}</li>
          </ul>
        </Card>
        <Card title="Top Categories">
          {topCats ? (
            <BarChart formatValue={(n)=> formatINR(n)} data={topCats.map(c => ({ label: c.name ?? "Unknown", value: c.total_paise }))} />
          ) : (
            <div>—</div>
          )}
        </Card>
        <Card title="Top People">
          {topPeople ? (
            <BarChart formatValue={(n)=> formatINR(n)} data={topPeople.map(p => ({ label: p.name ?? "Unknown", value: p.total_paise }))} />
          ) : (
            <div>—</div>
          )}
        </Card>
      </div>
    </div>
  );
}

function Card(props: { title: string; value?: string; children?: React.ReactNode }) {
  return (
    <div className="rounded border bg-white p-3 shadow-sm">
      <div className="text-sm text-slate-600">{props.title}</div>
      {props.value && <div className="text-xl font-semibold">{props.value}</div>}
      {props.children}
    </div>
  );
}
console.log("NEXT_PUBLIC_API_URL:", process.env.NEXT_PUBLIC_API_URL);
