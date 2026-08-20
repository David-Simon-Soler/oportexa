import type { Metadata } from "next";
import { TaxonomyIndex } from "../../../components/taxonomy-pages";
import { getSectors } from "../../../lib/db/regions";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Subvenciones por sector", description: "Explora convocatorias por sector en los datos actualmente incorporados por Oportexa.", alternates: { canonical: "/subvenciones/sector" } };
export default async function SectorsPage() { return <TaxonomyIndex title="Convocatorias por sector" description="Consulta ayudas y subvenciones clasificadas por sector de actividad." basePath="/subvenciones/sector" items={await getSectors()}/>; }
