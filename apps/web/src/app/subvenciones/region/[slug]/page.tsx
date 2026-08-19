import { notFound } from "next/navigation";
import { GrantCard } from "../../../../components/grant-card";
import { SiteHeader } from "../../../../components/site-header";
import { searchGrants } from "../../../../lib/db/grants";
import { getRegions, regionMatchesSlug } from "../../../../lib/db/regions";
export const dynamic = "force-dynamic";
export default async function RegionPage({ params }: { params: Promise<{ slug: string }> }) { const { slug } = await params; const region = (await getRegions()).find((item) => regionMatchesSlug(item, slug)); if (!region) notFound(); const result = await searchGrants({ region: region.code ?? region.description }); return <><SiteHeader/><main className="mx-auto max-w-6xl px-4 py-10 sm:px-6"><p className="text-sm font-semibold uppercase tracking-[0.18em] text-amber-700">Región</p><h1 className="mt-2 text-3xl font-semibold">Convocatorias en {region.description}</h1><p className="mt-3 text-slate-600">{result.total} resultados en el dataset local.</p><section className="mt-8 grid gap-4">{result.items.map((grant) => <GrantCard grant={grant} key={grant.bdnsCode}/>)}</section></main></>; }
