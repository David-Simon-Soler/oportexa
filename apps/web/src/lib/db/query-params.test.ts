import { describe, expect, it } from "vitest";
import { parseMinBudget, parsePage, parseSearchParams, parseSort } from "./query-params";

describe("V0.3 query parameters", () => {
  it("keeps the supported contract and normalizes values", () => {
    expect(parseSearchParams({ q: " energía ", status: "open", minBudget: "1000", sort: "budget-desc", page: "2", ignored: "x" })).toEqual({ q: "energía", region: undefined, sector: undefined, beneficiary: undefined, status: "open", minBudget: 1000, sort: "budget-desc", page: 2 });
  });

  it("rejects unsafe budgets and normalizes pages and sorting", () => {
    expect(parseMinBudget("-1")).toBeUndefined();
    expect(parseMinBudget("NaN")).toBeUndefined();
    expect(parseMinBudget("Infinity")).toBeUndefined();
    expect(parseMinBudget("999999999999999999999")).toBeUndefined();
    expect(parseMinBudget("")).toBeUndefined();
    expect(parsePage("0")).toBe(1);
    expect(parsePage("not-a-page")).toBe(1);
    expect(parsePage("999999999999999999999")).toBe(1);
    expect(parseSort("relevance")).toBe("recent");
  });
});
