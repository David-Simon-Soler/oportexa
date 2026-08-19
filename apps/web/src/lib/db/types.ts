export type TaxonomyItem = { code: string | null; description: string };

export type GrantSummary = {
  bdnsCode: string;
  slug: string;
  title: string;
  callType: string | null;
  totalBudget: string | null;
  isOpen: boolean | null;
  applicationStartDate: string | null;
  applicationEndDate: string | null;
  sourceReceivedDate: string | null;
  organization: string | null;
  regions: TaxonomyItem[];
  sectors: TaxonomyItem[];
  beneficiaryTypes: TaxonomyItem[];
};

export type GrantDetail = GrantSummary & {
  description: string | null;
  purposeDescription: string | null;
  regulatoryBasesDescription: string | null;
  regulatoryBasesUrl: string | null;
  electronicOfficeUrl: string | null;
  firstSeenAt: string;
  lastSeenAt: string;
};

export type RegionSummary = TaxonomyItem & { count: number };
export type SearchFilters = { q?: string; region?: string; sector?: string; beneficiary?: string; status?: string; page?: number };
export type SearchResult = { items: GrantSummary[]; total: number; page: number; pageSize: number };
