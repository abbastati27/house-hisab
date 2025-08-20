import "../styles/globals.css";
import { ReactQueryClientProvider } from "@/components/rq-provider";
import Link from "next/link";

export const metadata = {
  title: "House Hisab",
  description: "Three‑Fund Ledger",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <ReactQueryClientProvider>
          <nav className="bg-white border-b">
            <div className="max-w-5xl mx-auto p-3 flex gap-4">
              <Link href="/" className="font-semibold">Dashboard</Link>
              <Link href="/transactions">Transactions</Link>
              <Link href="/add" className="ml-auto">Add</Link>
            </div>
          </nav>
          <div className="max-w-5xl mx-auto p-4 relative">
            {children}
            <Link href="/add" className="fixed bottom-6 right-6 bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-2xl shadow-lg">+</Link>
          </div>
        </ReactQueryClientProvider>
      </body>
    </html>
  );
}
