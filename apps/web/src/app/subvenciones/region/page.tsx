import type { Metadata } from "next";
import { TaxonomyIndex } from "../../../components/taxonomy-pages";
import { getRegions } from "../../../lib/db/regions";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Subvenciones por región", description: "Explora convocatorias por región en el catálogo local de Opportunity Intel.", alternates: { canonical: "/subvenciones/region" } };
export default async function RegionsPage() { return <TaxonomyIndex title="Convocatorias por región" description="Explora las convocatorias asociadas a cada territorio dentro de los datos actualmente incorporados." basePath="/subvenciones/region" items={await getRegions()}/>; }
