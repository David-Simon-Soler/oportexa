import type { Metadata, Viewport } from "next";
import "./globals.css";
import { getSiteUrl } from "../lib/site";

const siteUrl = getSiteUrl();

export const viewport: Viewport = { themeColor: "#F6F6F3", colorScheme: "light" };

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  applicationName: "Oportexa",
  title: { default: "Oportexa", template: "%s | Oportexa" },
  description: "Descubre, entiende y verifica ayudas y subvenciones públicas en España.",
  alternates: { canonical: "/" },
  manifest: "/manifest.webmanifest",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "16x16 32x32", type: "image/x-icon" },
      { url: "/logo-mark.svg", type: "image/svg+xml" },
    ],
    apple: "/apple-icon.png",
  },
  openGraph: {
    type: "website",
    siteName: "Oportexa",
    title: "Oportexa",
    description: "Descubre, entiende y verifica ayudas y subvenciones públicas en España.",
    url: "/",
    images: [{ url: "/opengraph-image.png", width: 1200, height: 630, alt: "Oportexa — ayudas y subvenciones públicas" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Oportexa",
    description: "Descubre, entiende y verifica ayudas y subvenciones públicas en España.",
    images: ["/opengraph-image.png"],
  },
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="es"><body className="min-h-screen bg-slate-50 text-slate-900">{children}</body></html>; }
