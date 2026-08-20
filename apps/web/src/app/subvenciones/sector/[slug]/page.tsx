import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { TaxonomyDetail } from "../../../../components/taxonomy-pages";
import { searchGrants } from "../../../../lib/db/grants";
import { getSectorBySlug } from "../../../../lib/db/regions";
import { parseSearchParams } from "../../../../lib/db/query-params";
type Props = { params: Promise<{ slug: string }>; searchParams: Promise<Record<string, string | string[] | undefined>> };
export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: Props): Promise<Metadata> { const entity = await getSectorBySlug((await params).slug); return entity ? { title: `Subvenciones de ${entity.label}`, description: `Convocatorias del sector ${entity.label} en el catálogo local de Opportunity Intel.`, alternates: { canonical: `/subvenciones/sector/${entity.slug}` } } : {}; }
export default async function SectorPage({ params, searchParams }: Props) { const entity = await getSectorBySlug((await params).slug); if (!entity) notFound(); const raw = await searchParams; const filters = parseSearchParams(raw); const result = await searchGrants({ ...filters, sector: entity.key }); const query = new URLSearchParams(); Object.entries(raw).forEach(([key, value]) => { const item = Array.isArray(value) ? value[0] : value; if (item) query.set(key, item); }); return <TaxonomyDetail entity={entity} sectionLabel="Sectores" indexPath="/subvenciones/sector" result={result} query={query}/>; }
