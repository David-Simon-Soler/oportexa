import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { TaxonomyDetail } from "../../../../components/taxonomy-pages";
import { searchGrants } from "../../../../lib/db/grants";
import { getRegionBySlug } from "../../../../lib/db/regions";
import { parseSearchParams } from "../../../../lib/db/query-params";
import { noindexForQuery } from "../../../../lib/seo";
type Props = { params: Promise<{ slug: string }>; searchParams: Promise<Record<string, string | string[] | undefined>> };
export const dynamic = "force-dynamic";
export async function generateMetadata({ params, searchParams }: Props): Promise<Metadata> { const region = await getRegionBySlug((await params).slug); const query = await searchParams; return region ? { title: `Subvenciones en ${region.label}`, description: `Convocatorias de ${region.label} en los datos actualmente incorporados por Oportexa.`, alternates: { canonical: `/subvenciones/region/${region.slug}` }, robots: region.totalGrants > 0 ? noindexForQuery(query) : { index: false, follow: true } } : { robots: { index: false, follow: true } }; }
export default async function RegionPage({ params, searchParams }: Props) { const entity = await getRegionBySlug((await params).slug); if (!entity) notFound(); const raw = await searchParams; const filters = parseSearchParams(raw); const result = await searchGrants({ ...filters, region: entity.key }); const query = new URLSearchParams(); Object.entries(raw).forEach(([key, value]) => { const item = Array.isArray(value) ? value[0] : value; if (item) query.set(key, item); }); return <TaxonomyDetail entity={entity} sectionLabel="Regiones" indexPath="/subvenciones/region" result={result} query={query} titlePrefix="Subvenciones en"/>; }
