import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { metadataBase: new URL(process.env.SITE_URL ?? "http://localhost:3000"), title: { default: "Opportunity Intel", template: "%s | Opportunity Intel" }, description: "Descubre, entiende y analiza oportunidades públicas en España." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="es"><body className="min-h-screen bg-slate-50 text-slate-900">{children}</body></html>; }
