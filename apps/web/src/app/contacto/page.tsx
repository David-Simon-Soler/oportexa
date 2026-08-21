import type { Metadata } from "next";
import { LegalPage } from "../../components/legal-page";

export const metadata: Metadata = {
  title: "Contacto",
  description: "Canal de contacto de Oportexa para consultas, errores y cuestiones de privacidad.",
  alternates: { canonical: "/contacto" },
};

export default function ContactPage() {
  return (
    <LegalPage
      eyebrow="Estamos aquí para ayudarte"
      title="Contacto"
      intro="Puedes escribirnos para consultas sobre el sitio, errores o cuestiones relacionadas con la información publicada."
    >
      <section className="rounded-2xl border border-[var(--border)] bg-white p-6 sm:p-8">
        <h2 className="mt-0">Email de contacto</h2>
        <p className="mt-4">
          <a
            className="break-words text-xl font-semibold text-[var(--accent)] underline underline-offset-4 sm:text-2xl"
            href="mailto:davidsimonsoler2002@gmail.com"
          >
            davidsimonsoler2002@gmail.com
          </a>
        </p>
        <p className="mt-4">
          Este canal puede utilizarse para consultas sobre Oportexa, comunicar errores, plantear
          cuestiones de privacidad, solicitar aclaraciones sobre información publicada o tratar
          cuestiones legales.
        </p>
      </section>
      <section>
        <h2>Trámites de subvenciones</h2>
        <p>
          Oportexa no tramita solicitudes ni representa a los organismos convocantes. Para
          presentar una solicitud o resolver dudas sobre requisitos y plazos, consulta siempre el
          organismo competente y la fuente oficial de la convocatoria.
        </p>
      </section>
    </LegalPage>
  );
}
