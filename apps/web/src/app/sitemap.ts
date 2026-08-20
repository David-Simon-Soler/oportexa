import type { MetadataRoute } from "next";
import { getGrantByCode, getGrantCodes } from "../lib/db/grants";
import { getRegions } from "../lib/db/regions";
export const dynamic = "force-dynamic";
export default async function sitemap(): Promise<MetadataRoute.Sitemap> { const site = process.env.SITE_URL ?? "http://localhost:3000"; const codes = await getGrantCodes(); const grants = await Promise.all(codes.map(async (code) => { const grant = await getGrantByCode(code); return grant ? { url: `${site}/subvenciones/${grant.slug}`, lastModified: grant.lastSeenAt } : null; })); const regions = await getRegions(); return [{ url: site, lastModified: new Date() }, { url: `${site}/subvenciones`, lastModified: new Date() }, { url: `${site}/subvenciones/region`, lastModified: new Date() }, ...grants.filter(Boolean).map((item) => item!), ...regions.filter((item) => item.totalGrants > 0).map((item) => ({ url: `${site}/subvenciones/region/${item.slug}`, lastModified: new Date() }))]; }
