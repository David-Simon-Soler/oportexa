import type { ReactNode } from "react";
import { SiteFooter } from "./discovery";
import { SiteHeader } from "./site-header";

export function LegalPage({
  eyebrow = "Información del sitio",
  title,
  intro,
  children,
}: {
  eyebrow?: string;
  title: string;
  intro: string;
  children: ReactNode;
}) {
  return (
    <>
      <SiteHeader />
      <main id="main-content" className="container-shell py-10 sm:py-14">
        <header className="max-w-3xl border-b border-[var(--border)] pb-8">
          <p className="eyebrow">{eyebrow}</p>
          <h1 className="section-title mt-2">{title}</h1>
          <p className="body-copy mt-4 text-base">{intro}</p>
        </header>
        <article className="legal-copy mt-10 max-w-3xl">{children}</article>
      </main>
      <SiteFooter />
    </>
  );
}
