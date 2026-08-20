import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { TaxonomyDetail } from "../../../../components/taxonomy-pages";
import { searchGrants } from "../../../../lib/db/grants";
import { getBeneficiaryTypeBySlug } from "../../../../lib/db/regions";
import { parseSearchParams } from "../../../../lib/db/query-params";
type Props = { params: Promise<{ slug: string }>; searchParams: Promise<Record<string, string | string[] | undefined>> };
export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: Props): Promise<Metadata> { const entity = await getBeneficiaryTypeBySlug((await params).slug); return entity ? { title: `Subvenciones para ${entity.label}`, description: `Convocatorias para ${entity.label} en los datos actualmente incorporados por Oportexa.`, alternates: { canonical: `/subvenciones/beneficiario/${entity.slug}` } } : {}; }
export default async function BeneficiaryPage({ params, searchParams }: Props) { const entity = await getBeneficiaryTypeBySlug((await params).slug); if (!entity) notFound(); const raw = await searchParams; const filters = parseSearchParams(raw); const result = await searchGrants({ ...filters, beneficiary: entity.key }); const query = new URLSearchParams(); Object.entries(raw).forEach(([key, value]) => { const item = Array.isArray(value) ? value[0] : value; if (item) query.set(key, item); }); return <TaxonomyDetail entity={entity} sectionLabel="Beneficiarios" indexPath="/subvenciones/beneficiario" result={result} query={query} titlePrefix="Subvenciones para"/>; }
