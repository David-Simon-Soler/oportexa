export function slugify(value: string): string {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export function grantSlug(code: string, title: string): string {
  return `${code}-${slugify(title || "convocatoria")}`;
}

export function taxonomySlug(label: string, key: string, collision = false): string {
  const base = slugify(label) || "taxonomy";
  return collision ? `${base}--${slugify(key) || "key"}` : base;
}
