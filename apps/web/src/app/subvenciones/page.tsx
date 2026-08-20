import type { Metadata } from "next";
import { ActiveFilters, Breadcrumbs, ErrorState, FilterPanel, GrantList, SiteFooter } from "../../components/discovery";
import { Pagination } from "../../components/pagination";
import { SearchForm } from "../../components/search-form";
import { SiteHeader } from "../../components/site-header";
import { searchGrants } from "../../lib/db/grants";
import { getBeneficiaryTypes, getRegions, getSectors } from "../../lib/db/regions";
import { parseSearchParams } from "../../lib/db/query-params";
export const dynamic = "force-dynamic";
type Params = Promise<Record<string, string | string[] | undefined>>;
function one(value: string | string[] | undefined) { return Array.isArray(value) ? value[0] : value; }
export async function generateMetadata({ searchParams }: { searchParams: Params }): Promise<Metadata> { const params = await searchParams; const hasQuery = Object.values(params).some((value) => Array.isArray(value) ? value.some(Boolean) : Boolean(value)); return { title: "Subvenciones y ayudas públicas", description: "Explora convocatorias públicas procedentes de la BDNS/SNPSAP.", alternates: { canonical: "/subvenciones" }, robots: hasQuery ? { index: false, follow: true } : undefined }; }

export default async function GrantsPage({ searchParams }: { searchParams: Params }) {
  const params = await searchParams; const filters = parseSearchParams(params);
  let result; let regions; let sectors; let beneficiaries;
  try { [result, regions, sectors, beneficiaries] = await Promise.all([searchGrants(filters), getRegions(), getSectors(), getBeneficiaryTypes()]); } catch { return <><SiteHeader/><main id="main-content" className="container-shell py-16"><Breadcrumbs items={[{ label: "Subvenciones" }]}/><h1 className="section-title mt-6">Subvenciones y ayudas públicas</h1><div className="mt-8"><ErrorState message="No hemos podido cargar las convocatorias. Inténtalo de nuevo en unos instantes."/></div></main><SiteFooter/></>; }
  const query = new URLSearchParams(); Object.entries(params).forEach(([key, value]) => { const item = one(value); if (item) query.set(key, item); });
  return <><SiteHeader/><main className="container-shell py-10 sm:py-14"><Breadcrumbs items={[{ label: "Subvenciones" }]}/><div className="mt-8 flex flex-wrap items-end justify-between gap-6 border-b border-[var(--border)] pb-8"><div><p className="eyebrow">Discovery</p><h1 className="section-title mt-2">Subvenciones y ayudas públicas</h1><p className="body-copy mt-3 max-w-xl text-sm">Explora oportunidades públicas a partir de información publicada por la BDNS.</p></div><div className="w-full max-w-md"><SearchForm initialValue={filters.q} compact/></div></div><div className="mt-7"><FilterPanel filters={filters} regions={regions} sectors={sectors} beneficiaries={beneficiaries}/></div><div className="mt-6"><ActiveFilters filters={filters}/></div><div className="mt-10"><GrantList items={result.items} total={result.total} emptyQuery={Object.keys(params).length > 0}/><Pagination page={result.page} total={result.total} pageSize={result.pageSize} query={query}/></div></main><SiteFooter/></>;
}
