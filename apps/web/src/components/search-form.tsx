export function SearchForm({ initialValue = "", compact = false }: { initialValue?: string; compact?: boolean }) {
  return <form action="/subvenciones" className={`flex w-full gap-2 ${compact ? "flex-col sm:flex-row" : "flex-col sm:flex-row"}`}>
    <label htmlFor={compact ? "catalog-search" : "hero-search"} className="sr-only">Buscar oportunidades públicas</label>
    <input id={compact ? "catalog-search" : "hero-search"} name="q" defaultValue={initialValue} placeholder="Buscar digitalización, empleo, energía..." className={`focus-ring min-w-0 flex-1 border border-[var(--border-strong)] bg-white px-4 text-[var(--foreground)] shadow-[0_1px_2px_rgba(23,32,29,.04)] placeholder:text-[var(--subtle)] ${compact ? "min-h-11 rounded-lg text-sm" : "min-h-14 rounded-xl text-base sm:min-h-16 sm:px-5 sm:text-lg"}`} />
    <button className={`focus-ring shrink-0 bg-[var(--accent)] font-semibold text-white transition-colors hover:bg-[var(--accent-hover)] ${compact ? "min-h-11 rounded-lg px-5 text-sm" : "min-h-14 rounded-xl px-6 sm:min-h-16"}`} type="submit">Buscar oportunidades</button>
  </form>;
}

export function SearchHero() { return <SearchForm/>; }
