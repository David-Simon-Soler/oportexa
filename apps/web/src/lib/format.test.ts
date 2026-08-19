import { describe, expect, it } from "vitest";
import { formatDate, formatMoney, statusLabel } from "./format";
import { grantSlug, slugify } from "./slug";

describe("formatters", () => {
  it("formats euros and preserves unknown values", () => { expect(formatMoney("1234.5")).toBe("1234,50 €"); expect(formatMoney(null)).toBe("Importe no especificado"); });
  it("formats dates without inventing missing dates", () => { expect(formatDate("2026-08-19")).toContain("19"); expect(formatDate(null)).toBe("Fecha no especificada"); });
  it("explains an open call without a closing date", () => { expect(statusLabel(true, null)).toContain("no especifica fecha de cierre"); });
  it("creates stable Spanish slugs", () => { expect(slugify("Ayudas para I+D+i en Aragón")).toBe("ayudas-para-i-d-i-en-aragon"); expect(grantSlug("925621", "Ayuda pública")).toBe("925621-ayuda-publica"); });
});
