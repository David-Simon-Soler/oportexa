"use client";
import { SiteFooter } from "../components/discovery";
import { SiteHeader } from "../components/site-header";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) { return <><SiteHeader/><main id="main-content" className="container-shell py-24 text-center"><h1 className="text-2xl font-semibold">No hemos podido cargar esta página</h1><p className="mx-auto mt-4 max-w-md text-[var(--muted)]">Inténtalo de nuevo en unos instantes. No mostramos detalles internos del servidor.</p><button onClick={() => reset()} className="focus-ring mt-6 rounded-lg bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white hover:bg-[var(--accent-hover)]">Reintentar</button></main><SiteFooter/></>; }
