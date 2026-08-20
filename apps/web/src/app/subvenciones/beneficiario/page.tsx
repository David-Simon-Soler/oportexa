import type { Metadata } from "next";
import { TaxonomyIndex } from "../../../components/taxonomy-pages";
import { getBeneficiaryTypes } from "../../../lib/db/regions";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Subvenciones por beneficiario", description: "Explora convocatorias por tipo de beneficiario en los datos actualmente incorporados por Oportexa.", alternates: { canonical: "/subvenciones/beneficiario" } };
export default async function BeneficiariesPage() { return <TaxonomyIndex title="Convocatorias por beneficiario" description="Consulta oportunidades según el tipo de beneficiario indicado en BDNS." basePath="/subvenciones/beneficiario" items={await getBeneficiaryTypes()}/>; }
