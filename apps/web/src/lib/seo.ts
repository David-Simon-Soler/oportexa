import type { Metadata } from "next";

export function hasQueryParams(params: Record<string, string | string[] | undefined>): boolean {
  return Object.values(params).some((value) => Array.isArray(value) ? value.some(Boolean) : Boolean(value));
}

export function noindexForQuery(params: Record<string, string | string[] | undefined>): Metadata["robots"] {
  return hasQueryParams(params) ? { index: false, follow: true } : undefined;
}

export function safeJsonLd(value: unknown): string {
  return JSON.stringify(value).replace(/</g, "\\u003c").replace(/>/g, "\\u003e").replace(/&/g, "\\u0026");
}
