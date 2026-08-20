import "server-only";
import { getPool } from "./client";
import { grantSlug, slugify } from "../slug";
import type { FundRef, GrantDetail, GrantSummary, OrganizationRef, SearchFilters, SearchResult, TaxonomyRef } from "./types";

const PAGE_SIZE = 20;

const jsonTaxonomy = (table: string, relation: string, id: string, label = "x.description") =>
  `(SELECT COALESCE(json_agg(json_build_object('key', x.source_key, 'code', x.code, 'label', ${label}) ORDER BY ${label}), '[]'::json) FROM core.${relation} rel JOIN core.${table} x ON x.id = rel.${id} WHERE rel.grant_call_id = g.id)`;
const jsonOrganizations = `(SELECT COALESCE(json_agg(json_build_object('key', o.source_key, 'label', COALESCE(NULLIF(o.level3, ''), NULLIF(o.level2, ''), NULLIF(o.level1, ''), o.source_key)) ORDER BY COALESCE(NULLIF(o.level3, ''), NULLIF(o.level2, ''), NULLIF(o.level1, ''), o.source_key)), '[]'::json) FROM core.grant_call_organizations rel JOIN core.organizations o ON o.id = rel.organization_id WHERE rel.grant_call_id = g.id)`;
const jsonFunds = `(SELECT COALESCE(json_agg(json_build_object('key', f.source_key, 'label', f.description) ORDER BY f.description), '[]'::json) FROM core.grant_call_funds rel JOIN core.funds f ON f.id = rel.fund_id WHERE rel.grant_call_id = g.id)`;

function whereFor(filters: SearchFilters) {
  const clauses: string[] = [];
  const values: Array<string | number> = [];
  const add = (sql: string, items: Array<string | number>) => {
    clauses.push(sql.replace(/\?/g, () => { values.push(items.shift() as string | number); return `$${values.length}`; }));
  };
  if (filters.q?.trim()) add("(g.title ILIKE ? OR g.description ILIKE ? OR g.purpose_description ILIKE ?)", [`%${filters.q.trim()}%`, `%${filters.q.trim()}%`, `%${filters.q.trim()}%`]);
  if (filters.region) add("EXISTS (SELECT 1 FROM core.grant_call_regions rel JOIN core.regions x ON x.id = rel.region_id WHERE rel.grant_call_id = g.id AND (x.code = ? OR x.description = ? OR x.source_key = ?))", [filters.region, filters.region, filters.region]);
  if (filters.sector) add("EXISTS (SELECT 1 FROM core.grant_call_sectors rel JOIN core.sectors x ON x.id = rel.sector_id WHERE rel.grant_call_id = g.id AND (x.code = ? OR x.description = ? OR x.source_key = ?))", [filters.sector, filters.sector, filters.sector]);
  if (filters.beneficiary) add("EXISTS (SELECT 1 FROM core.grant_call_beneficiary_types rel JOIN core.beneficiary_types x ON x.id = rel.beneficiary_type_id WHERE rel.grant_call_id = g.id AND (x.code = ? OR x.description = ? OR x.source_key = ?))", [filters.beneficiary, filters.beneficiary, filters.beneficiary]);
  if (filters.organization) add("EXISTS (SELECT 1 FROM core.grant_call_organizations rel JOIN core.organizations x ON x.id = rel.organization_id WHERE rel.grant_call_id = g.id AND x.source_key = ?)", [filters.organization]);
  if (filters.organization) add("EXISTS (SELECT 1 FROM core.grant_call_organizations rel JOIN core.organizations x ON x.id = rel.organization_id WHERE rel.grant_call_id = g.id AND x.source_key = ?)", [filters.organization]);
  if (filters.status === "open") clauses.push("g.is_open IS TRUE");
  if (filters.minBudget !== undefined) add("g.total_budget >= ?", [filters.minBudget]);
  return { sql: clauses.length ? `WHERE ${clauses.join(" AND ")}` : "", values };
}

const selectFields = `g.bdns_code, g.title, g.call_type, g.total_budget::text AS total_budget, g.is_open, g.application_start_date::text AS application_start_date, g.application_end_date::text AS application_end_date, g.source_received_date::text AS source_received_date, ${jsonOrganizations} AS organizations, ${jsonTaxonomy("regions", "grant_call_regions", "region_id")} AS regions, ${jsonTaxonomy("sectors", "grant_call_sectors", "sector_id")} AS sectors, ${jsonTaxonomy("beneficiary_types", "grant_call_beneficiary_types", "beneficiary_type_id")} AS beneficiary_types`;

const orderBy: Record<NonNullable<SearchFilters["sort"]>, string> = {
  recent: "g.source_received_date DESC NULLS LAST, g.last_seen_at DESC, g.bdns_code DESC",
  "budget-desc": "g.total_budget DESC NULLS LAST, g.source_received_date DESC NULLS LAST, g.bdns_code DESC",
  "budget-asc": "g.total_budget ASC NULLS LAST, g.source_received_date DESC NULLS LAST, g.bdns_code DESC",
};

function mapRef(row: { key: string; code?: string | null; label: string }): TaxonomyRef { return { key: row.key, code: row.code ?? null, label: row.label, slug: slugify(row.label) }; }
function mapOrganization(row: { key: string; label: string }): OrganizationRef { return { key: row.key, label: row.label, slug: slugify(row.label) }; }

function mapRow(row: Record<string, unknown>): GrantSummary {
  const organizations = (row.organizations ?? []) as Array<{ key: string; label: string }>;
  const regions = (row.regions ?? []) as Array<{ key: string; code: string | null; label: string }>;
  const sectors = (row.sectors ?? []) as Array<{ key: string; code: string | null; label: string }>;
  const beneficiaryTypes = (row.beneficiary_types ?? []) as Array<{ key: string; code: string | null; label: string }>;
  const title = row.title as string | null;
  const bdnsCode = String(row.bdns_code);
  return { bdnsCode, slug: grantSlug(bdnsCode, title ?? "Convocatoria sin título"), title, callType: row.call_type as string | null, totalBudget: row.total_budget as string | null, isOpen: row.is_open as boolean | null, applicationStartDate: row.application_start_date as string | null, applicationEndDate: row.application_end_date as string | null, sourceReceivedDate: row.source_received_date as string | null, organizations: organizations.map(mapOrganization), regions: regions.map(mapRef), sectors: sectors.map(mapRef), beneficiaryTypes: beneficiaryTypes.map(mapRef) };
}

export async function searchGrants(filters: SearchFilters = {}): Promise<SearchResult> {
  const page = Number.isSafeInteger(filters.page) && (filters.page ?? 1) >= 1 ? filters.page as number : 1;
  const built = whereFor(filters);
  const offset = (page - 1) * PAGE_SIZE;
  const sort = orderBy[filters.sort ?? "recent"];
  const pool = getPool();
  const [items, count] = await Promise.all([
    pool.query(`SELECT ${selectFields} FROM core.grant_calls g ${built.sql} ORDER BY ${sort} LIMIT $${built.values.length + 1} OFFSET $${built.values.length + 2}`, [...built.values, PAGE_SIZE, offset]),
    pool.query(`SELECT COUNT(*)::int AS total FROM core.grant_calls g ${built.sql}`, built.values),
  ]);
  return { items: items.rows.map(mapRow), total: count.rows[0].total, page, pageSize: PAGE_SIZE };
}

export function getOpenGrants(filters: Omit<SearchFilters, "status"> = {}): Promise<SearchResult> { return searchGrants({ ...filters, status: "open" }); }

export async function getGrantByCode(code: string): Promise<GrantDetail | null> {
  const result = await getPool().query(`SELECT ${selectFields}, g.description, g.purpose_description, g.regulatory_bases_description, g.regulatory_bases_url, g.electronic_office_url, g.source_received_date::text AS detail_source_received_date, g.first_seen_at::text AS first_seen_at, g.last_seen_at::text AS last_seen_at, ${jsonFunds} AS funds FROM core.grant_calls g WHERE g.bdns_code = $1`, [code]);
  if (!result.rows[0]) return null;
  const row = result.rows[0];
  const summary = mapRow(row);
  const firstSeenAt = String(row.first_seen_at);
  const lastSeenAt = String(row.last_seen_at);
  return { ...summary, description: row.description as string | null, purposeDescription: row.purpose_description as string | null, regulatoryBasesDescription: row.regulatory_bases_description as string | null, regulatoryBasesUrl: row.regulatory_bases_url as string | null, electronicOfficeUrl: row.electronic_office_url as string | null, funds: (row.funds ?? []) as FundRef[], provenance: { source: "BDNS", sourceReceivedDate: row.detail_source_received_date as string | null, firstSeenAt, lastSeenAt }, firstSeenAt, lastSeenAt };
}

export async function getGrantCodes(): Promise<string[]> { const result = await getPool().query("SELECT bdns_code FROM core.grant_calls ORDER BY bdns_code"); return result.rows.map((row) => String(row.bdns_code)); }
