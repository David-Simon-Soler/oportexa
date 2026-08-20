import Link from "next/link";
import { SiteFooter } from "../components/discovery";
import { SiteHeader } from "../components/site-header";

export default function NotFound() {
  return <><SiteHeader/><main id="main-content" className="container-shell py-24 text-center"><p className="eyebrow">404 · Página no encontrada</p><h1 className="mt-3 text-3xl font-semibold tracking-[-.04em]">No encontramos esta página</h1><p className="mx-auto mt-4 max-w-md text-[var(--muted)]">Puede que la dirección haya cambiado o que todavía no esté disponible en los datos incorporados.</p><div className="mt-7 flex flex-wrap justify-center gap-3"><Link href="/" className="focus-ring rounded-lg border border-[var(--border-strong)] px-5 py-3 text-sm font-semibold text-[var(--foreground)] hover:bg-white">Volver al inicio</Link><Link href="/subvenciones" className="focus-ring rounded-lg bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white hover:bg-[var(--accent-hover)]">Explorar subvenciones</Link></div></main><SiteFooter/></>;
}
