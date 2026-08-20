import type { Metadata } from "next";
import Link from "next/link";
import { DatasetStats, ExplorationSection, OpenOpportunitySection, SiteFooter, SourceTrustSection } from "../components/discovery";
import { SearchHero } from "../components/search-form";
import { SiteHeader } from "../components/site-header";
import { ErrorState } from "../components/discovery";
import { getHomepageData } from "../lib/db/homepage";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Encuentra oportunidades públicas | Oportexa", description: "Busca y explora subvenciones y ayudas públicas a partir de información publicada por la BDNS." };

export default async function Home() {
  let data;
  try { data = await getHomepageData(); } catch { return <><SiteHeader/><main id="main-content" className="container-shell py-20"><ErrorState message="No hemos podido cargar las oportunidades. Inténtalo de nuevo en unos instantes."/></main><SiteFooter/></>; }
  return <><SiteHeader/><main id="main-content">
    <section className="container-shell grid gap-10 pb-16 pt-16 sm:pb-24 sm:pt-24 lg:grid-cols-[1.1fr_.9fr] lg:items-end lg:gap-16">
      <div><p className="eyebrow">Oportunidades públicas en España</p><h1 className="display-title mt-5 max-w-4xl">Encuentra oportunidades públicas <span className="text-[var(--accent)]">que encajen contigo</span></h1><p className="body-copy mt-6 max-w-xl text-base sm:text-lg">Busca y explora subvenciones y ayudas públicas a partir de información publicada por la BDNS.</p></div>
      <div className="lg:pb-1"><SearchHero/><p className="mt-3 text-sm text-[var(--muted)]">Busca por actividad, sector, territorio, organismo o palabras clave.</p><p className="mt-2 text-xs text-[var(--subtle)]">Prueba con <Link href="/subvenciones?q=digitalizacion" className="underline underline-offset-4 hover:text-[var(--accent)]">digitalización</Link>, <Link href="/subvenciones?q=empleo" className="underline underline-offset-4 hover:text-[var(--accent)]">empleo</Link> o <Link href="/subvenciones?q=energia" className="underline underline-offset-4 hover:text-[var(--accent)]">energía</Link>.</p></div>
    </section>
    <section className="container-shell border-t border-[var(--border)] py-8"><div className="flex flex-wrap items-center gap-x-7 gap-y-3 text-sm"><span className="font-semibold text-[var(--foreground)]">Explora directamente</span><Link href="/subvenciones" className="text-[var(--muted)] underline underline-offset-4 hover:text-[var(--accent)]">Convocatorias</Link><Link href="/subvenciones/region" className="text-[var(--muted)] underline underline-offset-4 hover:text-[var(--accent)]">Regiones</Link><Link href="/subvenciones/sector" className="text-[var(--muted)] underline underline-offset-4 hover:text-[var(--accent)]">Sectores</Link><Link href="/subvenciones/beneficiario" className="text-[var(--muted)] underline underline-offset-4 hover:text-[var(--accent)]">Beneficiarios</Link></div></section>
    <section className="container-shell border-y border-[var(--border)] py-8 sm:py-10" aria-labelledby="how-it-works"><h2 id="how-it-works" className="sr-only">Qué puedes hacer con Oportexa</h2><div className="grid gap-6 sm:grid-cols-3 sm:gap-8"><div><p className="eyebrow">01 · Buscar</p><p className="mt-2 text-sm leading-6 text-[var(--muted)]">Encuentra ayudas y subvenciones por actividad, territorio, sector o beneficiario.</p></div><div><p className="eyebrow">02 · Explorar</p><p className="mt-2 text-sm leading-6 text-[var(--muted)]">Descubre oportunidades publicadas por organismos públicos.</p></div><div><p className="eyebrow">03 · Verificar</p><p className="mt-2 text-sm leading-6 text-[var(--muted)]">Consulta cada convocatoria y accede directamente a su fuente oficial.</p></div></div></section>
    <OpenOpportunitySection grants={data.open.items}/>
    <ExplorationSection sectors={data.topSectors} regions={data.topRegions} beneficiaries={data.topBeneficiaries}/>
    <DatasetStats total={data.stats.totalGrants} open={data.stats.openGrants} sectors={data.stats.sectorCount} regions={data.stats.regionCount}/>
    <SourceTrustSection/>
  </main><SiteFooter/></>;
}
