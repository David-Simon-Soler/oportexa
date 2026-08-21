import type { MetadataRoute } from "next";
import { getGrantSitemapEntries } from "../lib/db/grants";
import { getRegions } from "../lib/db/regions";
import { getSiteUrl } from "../lib/site";
import { grantSlug } from "../lib/slug";
export const dynamic = "force-dynamic";
export default async function sitemap(): Promise<MetadataRoute.Sitemap> { const site = getSiteUrl(); const grants = await getGrantSitemapEntries(); const regions = await getRegions(); return [{ url: site, lastModified: new Date() }, { url: `${site}/subvenciones`, lastModified: new Date() }, { url: `${site}/subvenciones/region`, lastModified: new Date() }, ...grants.map((grant) => ({ url: `${site}/subvenciones/${grantSlug(grant.bdnsCode, grant.title ?? "Convocatoria sin título")}`, lastModified: grant.lastSeenAt ?? new Date() })), ...regions.filter((item) => item.totalGrants > 0).map((item) => ({ url: `${site}/subvenciones/region/${item.slug}`, lastModified: new Date() }))]; }
