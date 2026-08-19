import "server-only";
import { getPool } from "./client";
import { slugify } from "../slug";
import type { RegionSummary } from "./types";

export async function getRegions(): Promise<RegionSummary[]> {
  const result = await getPool().query(`SELECT r.code, r.description, COUNT(rel.grant_call_id)::int AS count FROM core.regions r LEFT JOIN core.grant_call_regions rel ON rel.region_id = r.id GROUP BY r.id ORDER BY r.description`);
  return result.rows.map((row) => ({ code: row.code, description: row.description, count: row.count }));
}

export function regionMatchesSlug(region: RegionSummary, slug: string): boolean { return slugify(region.description) === slug || (region.code ? slugify(region.code) === slug : false); }
