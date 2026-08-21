import { describe, expect, it } from "vitest";
import { safeJsonLd } from "./seo";

describe("SEO JSON-LD", () => {
  it("escapes script-breaking characters from data labels", () => {
    const value = safeJsonLd({ name: "</script><script>alert(1)</script>&" });
    expect(value).not.toContain("</script>");
    expect(value).toContain("\\u003c/script\\u003e");
    expect(value).toContain("\\u0026");
  });
});
