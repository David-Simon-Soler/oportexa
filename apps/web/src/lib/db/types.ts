export type TaxonomyRef = { key: string; code: string | null; label: string; slug: string };

export type OrganizationRef = { key: string; label: string; slug: string };

export type TaxonomySummary = {
  key: string;
  code: string | null;
  label: string;
  slug: string;
  totalGrants: number;
  openGrants: number;
};

export type RegionSummary = TaxonomySummary;
export type SectorSummary = TaxonomySummary;
export type BeneficiarySummary = TaxonomySummary;
export type OrganizationSummary = TaxonomySummary;

export type GrantSummary = {
  bdnsCode: string;
  slug: string;
  title: string | null;
  callType: string | null;
  totalBudget: string | null;
  isOpen: boolean | null;
  applicationStartDate: string | null;
  applicationEndDate: string | null;
  sourceReceivedDate: string | null;
  organizations: OrganizationRef[];
  regions: TaxonomyRef[];
  sectors: TaxonomyRef[];
  beneficiaryTypes: TaxonomyRef[];
};

export type FundRef = { key: string; label: string };

export type GrantDetail = GrantSummary & {
  description: string | null;
  purposeDescription: string | null;
  regulatoryBasesDescription: string | null;
  regulatoryBasesUrl: string | null;
  electronicOfficeUrl: string | null;
  funds: FundRef[];
  provenance: {
    source: "BDNS";
    sourceReceivedDate: string | null;
    firstSeenAt: string;
    lastSeenAt: string;
  };
  firstSeenAt: string;
  lastSeenAt: string;
};

export type SortOption = "recent" | "budget-desc" | "budget-asc";

export type SearchFilters = {
  q?: string;
  region?: string;
  sector?: string;
  beneficiary?: string;
  /** Internal taxonomy scope; not exposed as a public query parameter. */
  organization?: string;
  status?: "open";
  minBudget?: number;
  sort?: SortOption;
  page?: number;
};

export type SearchResult = { items: GrantSummary[]; total: number; page: number; pageSize: number };

export type HomepageData = {
  stats: { totalGrants: number; openGrants: number; sectorCount: number; regionCount: number };
  topSectors: SectorSummary[];
  topRegions: RegionSummary[];
  topBeneficiaries: BeneficiarySummary[];
  recent: SearchResult;
  open: SearchResult;
};
