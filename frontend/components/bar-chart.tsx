export function BarChart({ data, formatValue }: { data: { label: string; value: number }[]; formatValue?: (n:number)=>string }) {
  const max = Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="space-y-2">
      {data.map((d) => (
        <div key={d.label} className="flex items-center gap-2 overflow-hidden">
          <div className="min-w-0 flex-1 truncate text-sm">{d.label}</div>
          <div className="flex-1 bg-slate-200 h-3 rounded overflow-hidden">
            <div className="bg-blue-600 h-3" style={{ width: `${(d.value / max) * 100}%` }} />
          </div>
          <div className="shrink-0 text-right text-sm tabular-nums whitespace-nowrap">
            {formatValue ? formatValue(d.value) : d.value}
          </div>
        </div>
      ))}
    </div>
  );
}
