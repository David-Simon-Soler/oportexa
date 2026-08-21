import type { Metadata } from "next";
import { LegalPage } from "../../components/legal-page";

export const metadata: Metadata = {
  title: "Aviso legal",
  description: "Información legal y condiciones de uso de Oportexa.",
  alternates: { canonical: "/aviso-legal" },
};

export default function LegalNoticePage() {
  return (
    <LegalPage
      title="Aviso legal"
      intro="Información sobre el titular, el alcance de Oportexa y las condiciones generales de uso del sitio."
    >
      <section>
        <h2>Identificación del sitio</h2>
        <p>
          Oportexa es un sitio web informativo dedicado a facilitar la consulta y exploración de
          información pública sobre subvenciones y convocatorias en España.
        </p>
        <dl className="mt-5 grid gap-3 rounded-xl border border-[var(--border)] bg-white p-5 text-sm sm:grid-cols-[auto_1fr] sm:gap-x-6">
          <dt className="font-semibold text-[var(--muted)]">Titular</dt>
          <dd>David José Simón Soler</dd>
          <dt className="font-semibold text-[var(--muted)]">País</dt>
          <dd>España</dd>
          <dt className="font-semibold text-[var(--muted)]">Contacto</dt>
          <dd><a className="text-[var(--accent)] underline underline-offset-4" href="mailto:davidsimonsoler2002@gmail.com">davidsimonsoler2002@gmail.com</a></dd>
          <dt className="font-semibold text-[var(--muted)]">Sitio</dt>
          <dd>Oportexa</dd>
        </dl>
      </section>
      <section>
        <h2>Finalidad y carácter informativo</h2>
        <p>
          Oportexa organiza y presenta información pública para ayudar a descubrir y entender
          oportunidades. No es un organismo oficial, no representa a una Administración Pública,
          no concede subvenciones y no tramita solicitudes.
        </p>
        <p>
          El sitio no garantiza la concesión de ninguna ayuda ni sustituye la información,
          instrucciones o asesoramiento del organismo competente.
        </p>
      </section>
      <section>
        <h2>Fuentes y exactitud de la información</h2>
        <p>
          La información procede principalmente del Sistema Nacional de Publicidad de
          Subvenciones y Ayudas Públicas y de la Base de Datos Nacional de Subvenciones
          (SNPSAP/BDNS). Oportexa puede enlazar a convocatorias, bases reguladoras, sedes
          electrónicas y otros recursos oficiales.
        </p>
        <p>
          La información puede cambiar, contener errores de origen o mostrar un retraso respecto
          de la fuente. Ante cualquier discrepancia, prevalece siempre la información publicada
          por el organismo competente en la fuente oficial.
        </p>
      </section>
      <section>
        <h2>Enlaces externos</h2>
        <p>
          Los enlaces a sitios de terceros se ofrecen para facilitar el acceso a información
          relacionada. Esos sitios tienen sus propias condiciones y políticas, y Oportexa no
          controla su contenido, disponibilidad ni cambios posteriores.
        </p>
      </section>
      <section>
        <h2>Propiedad intelectual y reutilización</h2>
        <p>
          La estructura, selección, presentación y elementos propios de Oportexa están protegidos
          por la normativa aplicable. Los datos y contenidos públicos conservan la titularidad y
          condiciones que correspondan a sus fuentes. Su reutilización debe respetar la normativa
          aplicable, la procedencia y cualquier condición indicada por la fuente oficial.
        </p>
      </section>
      <section>
        <h2>Condiciones generales de uso</h2>
        <p>
          El uso del sitio debe realizarse de forma lícita, diligente y compatible con su
          finalidad informativa. No debe utilizarse para perjudicar el funcionamiento del sitio,
          acceder sin autorización a sistemas o presentar la información de Oportexa como
          certificación oficial.
        </p>
        <p>
          Estas condiciones se interpretan conforme a la legislación española aplicable, sin
          perjuicio de las normas imperativas que correspondan.
        </p>
      </section>
    </LegalPage>
  );
}
