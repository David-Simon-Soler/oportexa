const fallbackSiteUrl = "http://localhost:3000";

export function getSiteUrl(): string {
  return (process.env.SITE_URL ?? fallbackSiteUrl).replace(/\/+$/, "");
}

export function absoluteSiteUrl(path = "/"): string {
  return new URL(path, `${getSiteUrl()}/`).toString();
}
