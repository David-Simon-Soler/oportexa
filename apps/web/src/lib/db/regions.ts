import "server-only";
import { getPool } from "./client";
import { slugify, taxonomySlug } from "../slug";
import type { BeneficiarySummary, OrganizationSummary, RegionSummary, SectorSummary, TaxonomySummary } from "./types";

type TaxonomyKind = "regions" | "sectors" | "beneficiary_types" | "organizations";
const config: Record<TaxonomyKind, { relation: string; table: string; id: string; key: string; code: string; label: string }> = {
  regions: { relation: "grant_call_regions", table: "regions", id: "region_id", key: "source_key", code: "code", label: "x.description" },
  sectors: { relation: "grant_call_sectors", table: "sectors", id: "sector_id", key: "source_key", code: "code", label: "x.description" },
  beneficiary_types: { relation: "grant_call_beneficiary_types", table: "beneficiary_types", id: "beneficiary_type_id", key: "source_key", code: "code", label: "x.description" },
  organizations: { relation: "grant_call_organizations", table: "organizations", id: "organization_id", key: "source_key", code: "source_key", label: "COALESCE(NULLIF(x.level3, ''), NULLIF(x.level2, ''), NULLIF(x.level1, ''), x.source_key)" },
};

function withCollisionSlugs<T extends { label: string; key: string }>(items: T[]): Array<T & { slug: string }> {
  const counts = new Map<string, number>();
  for (const item of items) counts.set(slugify(item.label), (counts.get(slugify(item.label)) ?? 0) + 1);
  return items.map((item) => ({ ...item, slug: taxonomySlug(item.label, item.key, (counts.get(slugify(item.label)) ?? 0) > 1) }));
}

async function getTaxonomy(kind: TaxonomyKind): Promise<TaxonomySummary[]> {
  const c = config[kind];
  const result = await getPool().query(`SELECT x.${c.key} AS key, ${c.code === "source_key" ? `x.${c.code}` : `x.${c.code}`} AS code, ${c.label} AS label, COUNT(DISTINCT rel.grant_call_id)::int AS total_grants, COUNT(DISTINCT rel.grant_call_id) FILTER (WHERE g.is_open IS TRUE)::int AS open_grants FROM core.${c.table} x LEFT JOIN core.${c.relation} rel ON rel.${c.id} = x.id LEFT JOIN core.grant_calls g ON g.id = rel.grant_call_id GROUP BY x.id ORDER BY label`);
  return withCollisionSlugs(result.rows.map((row) => ({ key: String(row.key), code: kind === "organizations" ? null : row.code as string | null, label: String(row.label), totalGrants: Number(row.total_grants), openGrants: Number(row.open_grants) })));
}

async function getBySlug(kind: TaxonomyKind, slug: string): Promise<TaxonomySummary | null> { return (await getTaxonomy(kind)).find((item) => item.slug === slug || (kind === "regions" && item.code && slugify(item.code) === slug)) ?? null; }

export async function getRegions(): Promise<RegionSummary[]> { return getTaxonomy("regions") as Promise<RegionSummary[]>; }
export async function getRegionBySlug(slug: string): Promise<RegionSummary | null> { return getBySlug("regions", slug) as Promise<RegionSummary | null>; }
export async function getSectors(): Promise<SectorSummary[]> { return getTaxonomy("sectors") as Promise<SectorSummary[]>; }
export async function getSectorBySlug(slug: string): Promise<SectorSummary | null> { return getBySlug("sectors", slug) as Promise<SectorSummary | null>; }
export async function getOrganizations(): Promise<OrganizationSummary[]> { return getTaxonomy("organizations") as Promise<OrganizationSummary[]>; }
export async function getOrganizationBySlug(slug: string): Promise<OrganizationSummary | null> { return getBySlug("organizations", slug) as Promise<OrganizationSummary | null>; }
export async function getBeneficiaryTypes(): Promise<BeneficiarySummary[]> { return getTaxonomy("beneficiary_types") as Promise<BeneficiarySummary[]>; }
export async function getBeneficiaryTypeBySlug(slug: string): Promise<BeneficiarySummary | null> { return getBySlug("beneficiary_types", slug) as Promise<BeneficiarySummary | null>; }

export function regionMatchesSlug(region: RegionSummary, slug: string): boolean { return region.slug === slug || (!!region.code && slugify(region.code) === slug); }
