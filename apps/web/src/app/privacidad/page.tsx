import type { Metadata } from "next";
import { LegalPage } from "../../components/legal-page";

export const metadata: Metadata = {
  title: "Política de privacidad",
  description: "Información sobre privacidad y protección de datos en Oportexa.",
  alternates: { canonical: "/privacidad" },
};

export default function PrivacyPage() {
  return (
    <LegalPage
      title="Política de privacidad"
      intro="Esta especificación describe el tratamiento de datos en la versión actual de Oportexa."
    >
      <section>
        <h2>Responsable y contacto</h2>
        <p>
          El responsable del sitio es David José Simón Soler, en España. Para cualquier cuestión
          relacionada con privacidad puedes escribir a{" "}
          <a className="text-[var(--accent)] underline underline-offset-4" href="mailto:davidsimonsoler2002@gmail.com">davidsimonsoler2002@gmail.com</a>.
        </p>
      </section>
      <section>
        <h2>Qué ocurre actualmente</h2>
        <p>
          Oportexa no ofrece cuentas de usuario, autenticación, newsletter ni formularios para
          recoger nombre, email u otros datos personales. Las búsquedas y filtros se realizan
          mediante parámetros GET.
        </p>
        <p>
          El sitio no utiliza actualmente Google Analytics, Google Tag Manager, Vercel Analytics,
          Meta Pixel, publicidad personalizada ni otros trackers de usuario.
        </p>
      </section>
      <section>
        <h2>Funcionamiento técnico</h2>
        <p>
          El funcionamiento de una aplicación web puede implicar el tratamiento técnico de
          información como direcciones IP, solicitudes HTTP, datos del navegador o registros
          técnicos por parte de la infraestructura y los proveedores que intervienen en la
          prestación del servicio.
        </p>
        <p>
          Oportexa utiliza Vercel como proveedor de infraestructura y PostgreSQL en servidor para
          la aplicación. No se establecen aquí periodos de conservación o ubicaciones concretas
          que no hayan sido verificados para cada servicio.
        </p>
      </section>
      <section>
        <h2>Minimización y seguridad</h2>
        <p>
          La versión actual no solicita ni almacena datos privados de usuario para personalizar
          el servicio. Se aplican medidas técnicas y organizativas razonables para proteger el
          funcionamiento y la información bajo control del proyecto.
        </p>
      </section>
      <section>
        <h2>Derechos y actualizaciones</h2>
        <p>
          Si consideras que existe un tratamiento de datos personales relacionado con Oportexa,
          puedes contactar por email para plantear una consulta o ejercer los derechos que
          correspondan conforme a la normativa aplicable. También puedes acudir a la autoridad de
          protección de datos competente.
        </p>
        <p>
          Esta política se actualizará si el sitio incorpora cuentas, formularios, alertas,
          analítica u otras funcionalidades que cambien el tratamiento de datos.
        </p>
      </section>
    </LegalPage>
  );
}
