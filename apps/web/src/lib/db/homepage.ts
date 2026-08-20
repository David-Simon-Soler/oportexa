import "server-only";
import { searchGrants } from "./grants";
import { getBeneficiaryTypes, getRegions, getSectors } from "./regions";
import { getPool } from "./client";
import type { HomepageData } from "./types";

export async function getHomepageData(): Promise<HomepageData> {
  const [stats, sectors, regions, beneficiaries, recent, open] = await Promise.all([
    getPool().query("SELECT COUNT(*)::int AS total_grants, COUNT(*) FILTER (WHERE is_open IS TRUE)::int AS open_grants FROM core.grant_calls"),
    getSectors(),
    getRegions(),
    getBeneficiaryTypes(),
    searchGrants({ sort: "recent", page: 1 }),
    searchGrants({ status: "open", sort: "recent", page: 1 }),
  ]);
  return { stats: { totalGrants: stats.rows[0].total_grants, openGrants: stats.rows[0].open_grants }, topSectors: sectors.sort((a, b) => b.totalGrants - a.totalGrants).slice(0, 8), topRegions: regions.sort((a, b) => b.totalGrants - a.totalGrants).slice(0, 8), topBeneficiaries: beneficiaries.sort((a, b) => b.totalGrants - a.totalGrants).slice(0, 8), recent, open };
}
