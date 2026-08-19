import { SiteHeader } from "../../../components/site-header";
import { getRegions } from "../../../lib/db/regions";
import { slugify } from "../../../lib/slug";
import Link from "next/link";
export const dynamic = "force-dynamic";
export default async function RegionsPage() { const regions = await getRegions(); return <><SiteHeader/><main className="mx-auto max-w-6xl px-4 py-10 sm:px-6"><h1 className="text-3xl font-semibold">Convocatorias por región</h1><p className="mt-3 text-slate-600">Regiones con presencia real en el catálogo local.</p><div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{regions.map((region) => <Link key={`${region.code}-${region.description}`} href={`/subvenciones/region/${slugify(region.description)}`} className="rounded-xl border border-slate-200 bg-white p-5 hover:border-amber-400"><span className="font-medium">{region.description}</span><span className="mt-2 block text-sm text-slate-500">{region.count} convocatorias</span></Link>)}</div></main></>; }
