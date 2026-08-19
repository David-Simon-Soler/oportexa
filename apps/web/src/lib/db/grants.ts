import "server-only";
import { getPool } from "./client";
import { grantSlug } from "../slug";
import type { GrantDetail, GrantSummary, SearchFilters, SearchResult } from "./types";

const PAGE_SIZE = 20;
const taxonomy = (table: string, relation: string, id: string) => `(SELECT COALESCE(json_agg(json_build_object('code', x.code, 'description', x.description) ORDER BY x.description), '[]'::json) FROM core.${relation} rel JOIN core.${table} x ON x.id = rel.${id} WHERE rel.grant_call_id = g.id)`;

function whereFor(filters: SearchFilters) {
  const clauses: string[] = [];
  const values: string[] = [];
  const addMany = (sql: string, items: string[]) => { const placeholders = items.map((item) => { values.push(item); return `$${values.length}`; }); clauses.push(sql.replace(/\?/g, () => placeholders.shift() as string)); };
  if (filters.q?.trim()) addMany("(g.title ILIKE ? OR g.description ILIKE ? OR g.purpose_description ILIKE ?)", [`%${filters.q.trim()}%`, `%${filters.q.trim()}%`, `%${filters.q.trim()}%`]);
  if (filters.region) addMany("EXISTS (SELECT 1 FROM core.grant_call_regions rel JOIN core.regions x ON x.id = rel.region_id WHERE rel.grant_call_id = g.id AND (x.code = ? OR x.description = ?))", [filters.region, filters.region]);
  if (filters.sector) addMany("EXISTS (SELECT 1 FROM core.grant_call_sectors rel JOIN core.sectors x ON x.id = rel.sector_id WHERE rel.grant_call_id = g.id AND (x.code = ? OR x.description = ?))", [filters.sector, filters.sector]);
  if (filters.beneficiary) addMany("EXISTS (SELECT 1 FROM core.grant_call_beneficiary_types rel JOIN core.beneficiary_types x ON x.id = rel.beneficiary_type_id WHERE rel.grant_call_id = g.id AND (x.code = ? OR x.description = ?))", [filters.beneficiary, filters.beneficiary]);
  if (filters.status === "open") clauses.push("g.is_open IS TRUE");
  return { sql: clauses.length ? `WHERE ${clauses.join(" AND ")}` : "", values };
}

const selectFields = `g.bdns_code, COALESCE(g.title, 'Convocatoria sin título') AS title, g.call_type, g.total_budget::text AS total_budget, g.is_open, g.application_start_date::text AS application_start_date, g.application_end_date::text AS application_end_date, g.source_received_date::text AS source_received_date, (SELECT COALESCE(NULLIF(o.level3, ''), NULLIF(o.level2, ''), NULLIF(o.level1, '')) FROM core.grant_call_organizations rel JOIN core.organizations o ON o.id = rel.organization_id WHERE rel.grant_call_id = g.id ORDER BY o.level3 NULLS LAST LIMIT 1) AS organization, ${taxonomy("regions", "grant_call_regions", "region_id")} AS regions, ${taxonomy("sectors", "grant_call_sectors", "sector_id")} AS sectors, ${taxonomy("beneficiary_types", "grant_call_beneficiary_types", "beneficiary_type_id")} AS beneficiary_types`;

function mapRow(row: Record<string, unknown>): GrantSummary {
  return { bdnsCode: String(row.bdns_code), slug: grantSlug(String(row.bdns_code), String(row.title)), title: String(row.title), callType: row.call_type as string | null, totalBudget: row.total_budget as string | null, isOpen: row.is_open as boolean | null, applicationStartDate: row.application_start_date as string | null, applicationEndDate: row.application_end_date as string | null, sourceReceivedDate: row.source_received_date as string | null, organization: row.organization as string | null, regions: (row.regions ?? []) as GrantSummary["regions"], sectors: (row.sectors ?? []) as GrantSummary["sectors"], beneficiaryTypes: (row.beneficiary_types ?? []) as GrantSummary["beneficiaryTypes"] };
}

export async function searchGrants(filters: SearchFilters = {}): Promise<SearchResult> {
  const page = Math.max(1, filters.page ?? 1); const built = whereFor(filters); const offset = (page - 1) * PAGE_SIZE;
  const order = "ORDER BY CASE WHEN g.is_open IS TRUE THEN 0 ELSE 1 END, CASE WHEN g.application_end_date IS NULL THEN 1 ELSE 0 END, g.application_end_date ASC NULLS LAST, g.source_received_date DESC NULLS LAST, g.bdns_code DESC";
  const pool = getPool();
  const [items, count] = await Promise.all([
    pool.query(`SELECT ${selectFields} FROM core.grant_calls g ${built.sql} ${order} LIMIT $${built.values.length + 1} OFFSET $${built.values.length + 2}`, [...built.values, PAGE_SIZE, offset]),
    pool.query(`SELECT COUNT(*)::int AS total FROM core.grant_calls g ${built.sql}`, built.values),
  ]);
  return { items: items.rows.map(mapRow), total: count.rows[0].total, page, pageSize: PAGE_SIZE };
}

export async function getGrantByCode(code: string): Promise<GrantDetail | null> {
  const result = await getPool().query(`SELECT ${selectFields}, g.description, g.purpose_description, g.regulatory_bases_description, g.regulatory_bases_url, g.electronic_office_url, g.first_seen_at::text AS first_seen_at, g.last_seen_at::text AS last_seen_at FROM core.grant_calls g WHERE g.bdns_code = $1`, [code]);
  if (!result.rows[0]) return null;
  const row = mapRow(result.rows[0]);
  return { ...row, description: result.rows[0].description, purposeDescription: result.rows[0].purpose_description, regulatoryBasesDescription: result.rows[0].regulatory_bases_description, regulatoryBasesUrl: result.rows[0].regulatory_bases_url, electronicOfficeUrl: result.rows[0].electronic_office_url, firstSeenAt: result.rows[0].first_seen_at, lastSeenAt: result.rows[0].last_seen_at };
}

export async function getGrantCodes(): Promise<string[]> { const result = await getPool().query("SELECT bdns_code FROM core.grant_calls ORDER BY bdns_code"); return result.rows.map((row) => String(row.bdns_code)); }
