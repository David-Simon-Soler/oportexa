import Link from "next/link";
import { formatDate, formatMoney } from "../lib/format";
import type { GrantSummary, TaxonomyRef } from "../lib/db/types";

function relationLine(items: TaxonomyRef[], limit = 2) { if (!items.length) return "Información no disponible en la fuente"; const labels = items.slice(0, limit).map((item) => item.label); const extra = items.length - labels.length; return `${labels.join(" · ")}${extra > 0 ? ` · +${extra}` : ""}`; }

export function GrantStatus({ isOpen, endDate }: { isOpen: boolean | null; endDate: string | null }) { const open = isOpen === true; return <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${open ? "text-[var(--open)]" : "text-[var(--muted)]"}`}><span aria-hidden="true" className={`h-1.5 w-1.5 rounded-full ${open ? "bg-[var(--open)]" : "bg-[var(--subtle)]"}`} />{open ? (endDate ? "Abierta según BDNS" : "Abierta según BDNS · sin fecha límite indicada") : "No marcada como abierta"}</span>; }

export function BudgetDisplay({ value }: { value: string | null }) { return <>{formatMoney(value)}</>; }
export function DateDisplay({ start, end, isOpen }: { start: string | null; end: string | null; isOpen: boolean | null }) { if (isOpen === true && !end) return <>Abierta según BDNS · sin fecha límite indicada</>; if (start && end) return <>{formatDate(start)} – {formatDate(end)}</>; if (start) return <>Desde {formatDate(start)}</>; if (end) return <>Hasta {formatDate(end)}</>; return <>Fecha no indicada</>; }

export function GrantCard({ grant }: { grant: GrantSummary }) {
  return <article className="group border-b border-[var(--border)] py-6 first:border-t">
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_13rem] lg:gap-8">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2"><GrantStatus isOpen={grant.isOpen} endDate={grant.applicationEndDate}/><span className="text-xs text-[var(--subtle)]">BDNS {grant.bdnsCode}</span></div>
        <h2 className="mt-2 text-xl font-semibold leading-tight tracking-[-.025em] text-[var(--foreground)] sm:text-[1.4rem]"><Link href={`/subvenciones/${grant.slug}`} className="focus-ring rounded-sm transition-colors hover:text-[var(--accent)]">{grant.title ?? "Convocatoria sin título"}</Link></h2>
        <p className="mt-3 text-sm text-[var(--muted)]">{relationLine(grant.organizations.map((item) => ({ ...item, code: null })), 1)}</p>
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-[var(--subtle)]"><span>{relationLine(grant.regions)}</span><span>{relationLine(grant.sectors)}</span><span>{relationLine(grant.beneficiaryTypes)}</span></div>
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm lg:block lg:space-y-3">
        <div><dt className="text-xs text-[var(--subtle)]">Presupuesto publicado</dt><dd className="mt-1 font-semibold text-[var(--foreground)]"><BudgetDisplay value={grant.totalBudget}/></dd></div>
        <div><dt className="text-xs text-[var(--subtle)]">Plazo de solicitud</dt><dd className="mt-1 text-[var(--muted)]"><DateDisplay start={grant.applicationStartDate} end={grant.applicationEndDate} isOpen={grant.isOpen}/></dd></div>
      </dl>
    </div>
  </article>;
}
