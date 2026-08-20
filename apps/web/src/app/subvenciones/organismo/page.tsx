import type { Metadata } from "next";
import { TaxonomyIndex } from "../../../components/taxonomy-pages";
import { getOrganizations } from "../../../lib/db/regions";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Ayudas y subvenciones por organismo", description: "Explora convocatorias por organismo en el catálogo local de Opportunity Intel.", alternates: { canonical: "/subvenciones/organismo" } };
export default async function OrganizationsPage() { return <TaxonomyIndex title="Convocatorias por organismo" description="Organismos con presencia real en el catálogo local." basePath="/subvenciones/organismo" items={await getOrganizations()}/>; }
