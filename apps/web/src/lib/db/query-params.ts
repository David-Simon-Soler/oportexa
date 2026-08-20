import type { SearchFilters, SortOption } from "./types";

export const SORT_OPTIONS: readonly SortOption[] = ["recent", "budget-desc", "budget-asc"];
const MAX_MIN_BUDGET = 1_000_000_000_000_000;

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

export function parseMinBudget(value: string | undefined): number | undefined {
  if (!value?.trim()) return undefined;
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 0 || parsed > MAX_MIN_BUDGET) return undefined;
  return parsed;
}

export function parsePage(value: string | undefined): number {
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) && parsed >= 1 ? parsed : 1;
}

export function parseSort(value: string | undefined): SortOption {
  return SORT_OPTIONS.includes(value as SortOption) ? value as SortOption : "recent";
}

export function parseSearchParams(params: Record<string, string | string[] | undefined>): SearchFilters {
  const status = first(params.status) === "open" ? "open" : undefined;
  return {
    q: first(params.q)?.trim() || undefined,
    region: first(params.region)?.trim() || undefined,
    sector: first(params.sector)?.trim() || undefined,
    beneficiary: first(params.beneficiary)?.trim() || undefined,
    status,
    minBudget: parseMinBudget(first(params.minBudget)),
    sort: parseSort(first(params.sort)),
    page: parsePage(first(params.page)),
  };
}
