import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { TaxonomyDetail } from "../../../../components/taxonomy-pages";
import { searchGrants } from "../../../../lib/db/grants";
import { getRegionBySlug } from "../../../../lib/db/regions";
import { parseSearchParams } from "../../../../lib/db/query-params";
type Props = { params: Promise<{ slug: string }>; searchParams: Promise<Record<string, string | string[] | undefined>> };
export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> { const region = await getRegionBySlug((await params).slug); return region ? { title: `Subvenciones en ${region.label}`, description: `Convocatorias de ${region.label} en el catálogo local de Opportunity Intel.`, alternates: { canonical: `/subvenciones/region/${region.slug}` } } : {}; }
export default async function RegionPage({ params, searchParams }: Props) { const entity = await getRegionBySlug((await params).slug); if (!entity) notFound(); const raw = await searchParams; const filters = parseSearchParams(raw); const result = await searchGrants({ ...filters, region: entity.key }); const query = new URLSearchParams(); Object.entries(raw).forEach(([key, value]) => { const item = Array.isArray(value) ? value[0] : value; if (item) query.set(key, item); }); return <TaxonomyDetail entity={entity} sectionLabel="Regiones" indexPath="/subvenciones/region" result={result} query={query} titlePrefix="Subvenciones en"/>; }
