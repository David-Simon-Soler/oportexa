import type { Metadata } from "next";
import { LegalPage } from "../../components/legal-page";

export const metadata: Metadata = {
  title: "Política de cookies",
  description: "Información sobre el uso actual de cookies en Oportexa.",
  alternates: { canonical: "/cookies" },
};

export default function CookiesPage() {
  return (
    <LegalPage
      title="Política de cookies"
      intro="Información clara sobre las tecnologías de almacenamiento y acceso utilizadas actualmente por Oportexa."
    >
      <section>
        <h2>Qué son las cookies</h2>
        <p>
          Las cookies son pequeños archivos o identificadores que un sitio puede guardar o
          consultar en el dispositivo para recordar información o permitir determinadas
          funciones.
        </p>
      </section>
      <section>
        <h2>Estado actual de Oportexa</h2>
        <p>
          Oportexa no utiliza actualmente cookies publicitarias ni cookies propias de servicios
          de analítica. No utiliza Google Analytics, Google Tag Manager ni Google AdSense, y no
          realiza seguimiento publicitario.
        </p>
        <p>
          El funcionamiento técnico del navegador, Next.js o la infraestructura podría requerir
          mecanismos estrictamente técnicos. Esta página no afirma que ningún mecanismo técnico
          pueda existir en todos los entornos.
        </p>
      </section>
      <section>
        <h2>Cambios futuros</h2>
        <p>
          Si se incorporan tecnologías que requieran información adicional o consentimiento,
          esta política se actualizará y se habilitarán las medidas informativas y de elección que
          correspondan.
        </p>
      </section>
    </LegalPage>
  );
}
