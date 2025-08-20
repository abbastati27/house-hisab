export function parseIndianToPaise(input: string): number {
  const cleaned = input.replace(/[,\s₹]/g, "");
  if (!cleaned) return 0;
  const value = Number(cleaned);
  if (Number.isNaN(value)) return 0;
  return Math.round(value * 100);
}

export function formatPaiseINR(paise: number): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format((paise || 0) / 100);
}
