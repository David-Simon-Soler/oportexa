import Link from "next/link";

export function Pagination({ page, total, pageSize, query }: { page: number; total: number; pageSize: number; query: URLSearchParams }) {
  const pages = Math.ceil(total / pageSize); if (pages <= 1) return null;
  const href = (n: number) => { const next = new URLSearchParams(query); next.set("page", String(n)); return `/subvenciones?${next.toString()}`; };
  return <nav aria-label="Paginación de resultados" className="mt-8 flex items-center justify-between border-t border-[var(--border)] pt-5 text-sm"><span className="text-[var(--muted)]">Página {page} de {pages}</span><div className="flex gap-2">{page > 1 ? <Link className="focus-ring rounded-lg border border-[var(--border-strong)] px-3 py-2 text-[var(--foreground)] hover:bg-white" href={href(page - 1)}>Anterior</Link> : <span className="rounded-lg border border-[var(--border)] px-3 py-2 text-[var(--subtle)]">Anterior</span>}{page < pages ? <Link className="focus-ring rounded-lg border border-[var(--border-strong)] px-3 py-2 text-[var(--foreground)] hover:bg-white" href={href(page + 1)}>Siguiente</Link> : <span className="rounded-lg border border-[var(--border)] px-3 py-2 text-[var(--subtle)]">Siguiente</span>}</div></nav>;
}
