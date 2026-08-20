import Link from "next/link";

export function SiteHeader() {
  return <header className="border-b border-[var(--border)] bg-[var(--background)]">
    <a href="#main-content" className="focus-ring absolute left-3 top-3 z-50 -translate-y-20 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white transition-transform focus:translate-y-0">Saltar al contenido</a>
    <div className="container-shell flex min-h-18 flex-wrap items-center justify-between gap-x-8 gap-y-3 py-4">
      <Link href="/" className="focus-ring text-base font-bold tracking-[-.04em] text-[var(--foreground)]">Opportunity Intel<span className="ml-1 text-[var(--accent)]">/</span></Link>
      <nav aria-label="Navegación principal" className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-[var(--muted)]">
        <Link href="/subvenciones" className="focus-ring transition-colors hover:text-[var(--foreground)]">Convocatorias</Link>
        <Link href="/subvenciones/region" className="focus-ring transition-colors hover:text-[var(--foreground)]">Regiones</Link>
        <Link href="/subvenciones/sector" className="focus-ring transition-colors hover:text-[var(--foreground)]">Sectores</Link>
        <Link href="/subvenciones/organismo" className="focus-ring transition-colors hover:text-[var(--foreground)]">Organismos</Link>
        <Link href="/subvenciones/beneficiario" className="focus-ring transition-colors hover:text-[var(--foreground)]">Beneficiarios</Link>
      </nav>
    </div>
  </header>;
}
