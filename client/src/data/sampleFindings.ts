export type Finding = {
  id: string;
  title: string;
  cve?: string | null;
  description: string;
  cvss: number;
  epss: number;
  kev: boolean;
  asset_criticality: number;
  exposure: "external" | "internal" | "partial";
  effort_hours: number;
  data_sensitivity: "internal" | "confidential" | "high" | "public";
  effort_bucket: "quick_win" | "moderate" | "intensive";
  business_owner?: string;
};

export const sampleFindings: Finding[] = [
  {
    id: "FND-001",
    title: "Outdated VPN gateway with critical CVE",
    cve: "CVE-2024-12345",
    description: "VPN concentrator running vulnerable firmware allows remote code execution.",
    cvss: 9.8,
    epss: 0.76,
    kev: true,
    asset_criticality: 5,
    exposure: "external",
    effort_hours: 14,
    data_sensitivity: "high",
    effort_bucket: "intensive",
    business_owner: "Network Engineering"
  },
  {
    id: "FND-002",
    title: "Workstation agents missing EDR coverage",
    description: "Twenty finance workstations are missing the mandatory endpoint detection agent.",
    cvss: 7.4,
    epss: 0.18,
    kev: false,
    asset_criticality: 4,
    exposure: "partial",
    effort_hours: 6,
    data_sensitivity: "confidential",
    effort_bucket: "moderate",
    business_owner: "Endpoint Engineering"
  },
  {
    id: "FND-003",
    title: "S3 bucket permits public list access",
    description: "Cloud storage bucket for marketing assets allows anonymous listing of objects.",
    cvss: 6.3,
    epss: 0.12,
    kev: false,
    asset_criticality: 3,
    exposure: "external",
    effort_hours: 2,
    data_sensitivity: "confidential",
    effort_bucket: "quick_win",
    business_owner: "Cloud Platform"
  },
  {
    id: "FND-004",
    title: "Database missing critical patches",
    cve: "CVE-2024-22222",
    description: "Production database cluster has not applied the latest vendor security update.",
    cvss: 8.6,
    epss: 0.4,
    kev: false,
    asset_criticality: 5,
    exposure: "internal",
    effort_hours: 10,
    data_sensitivity: "high",
    effort_bucket: "moderate",
    business_owner: "Data Services"
  },
  {
    id: "FND-005",
    title: "Legacy service with weak TLS configuration",
    description: "Customer portal legacy service allows TLS 1.0 and weak cipher suites.",
    cvss: 5.4,
    epss: 0.08,
    kev: false,
    asset_criticality: 2,
    exposure: "external",
    effort_hours: 4,
    data_sensitivity: "internal",
    effort_bucket: "quick_win",
    business_owner: "Application Platform"
  }
];
