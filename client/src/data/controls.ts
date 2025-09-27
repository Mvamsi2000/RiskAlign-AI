export type Control = {
  id: string;
  description: string;
  category: string;
};

export const cisControls: Control[] = [
  {
    id: "CIS-01",
    description: "Inventory and control of enterprise assets",
    category: "Identify"
  },
  {
    id: "CIS-02",
    description: "Inventory and control of software assets",
    category: "Identify"
  },
  {
    id: "CIS-03",
    description: "Data protection",
    category: "Protect"
  }
];
