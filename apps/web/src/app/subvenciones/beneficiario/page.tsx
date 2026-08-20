import type { Metadata } from "next";
import { TaxonomyIndex } from "../../../components/taxonomy-pages";
import { getBeneficiaryTypes } from "../../../lib/db/regions";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Subvenciones por beneficiario", description: "Explora convocatorias por tipo de beneficiario en el catálogo local de Opportunity Intel.", alternates: { canonical: "/subvenciones/beneficiario" } };
export default async function BeneficiariesPage() { return <TaxonomyIndex title="Convocatorias por beneficiario" description="Tipos de beneficiario con presencia real en el catálogo local." basePath="/subvenciones/beneficiario" items={await getBeneficiaryTypes()}/>; }
