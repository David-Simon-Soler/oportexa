import type { Metadata } from "next";
import { SiteHeader } from "../../../components/site-header";
import { getRegions } from "../../../lib/db/regions";
import Link from "next/link";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Subvenciones por región", description: "Explora convocatorias por región en el catálogo local de Opportunity Intel.", alternates: { canonical: "/subvenciones/region" } };
export default async function RegionsPage() { const regions = await getRegions(); return <><SiteHeader/><main className="mx-auto max-w-6xl px-4 py-10 sm:px-6"><h1 className="text-3xl font-semibold">Convocatorias por región</h1><p className="mt-3 text-slate-600">Regiones con presencia real en el catálogo local.</p><div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{regions.map((region) => <Link key={region.key} href={`/subvenciones/region/${region.slug}`} className="rounded-xl border border-slate-200 bg-white p-5 hover:border-amber-400"><span className="font-medium">{region.label}</span><span className="mt-2 block text-sm text-slate-500">{region.totalGrants} convocatorias · {region.openGrants} abiertas</span></Link>)}</div></main></>; }
