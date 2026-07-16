export type MockMember = {
  name: string;
  role: string;
  department: string;
  projects: number;
  updatedAt: string;
  id: string;
  tone: string;
};

const initialMembers: MockMember[] = [
  {
    name: "鈴木 恒一",
    role: "Senior Product Designer",
    department: "Fintech事業部",
    projects: 4,
    updatedAt: "2026/07/15",
    id: "suzuki",
    tone: "teal",
  },
  {
    name: "山本 美咲",
    role: "Frontend Engineer",
    department: "Platform部",
    projects: 6,
    updatedAt: "2026/07/14",
    id: "yamamoto",
    tone: "gold",
  },
  {
    name: "佐藤 健",
    role: "Product Manager",
    department: "新規事業部",
    projects: 3,
    updatedAt: "2026/07/12",
    id: "sato",
    tone: "coral",
  },
  {
    name: "高橋 里奈",
    role: "UX Researcher",
    department: "Fintech事業部",
    projects: 2,
    updatedAt: "2026/07/10",
    id: "takahashi",
    tone: "blue",
  },
  {
    name: "伊藤 智也",
    role: "Backend Engineer",
    department: "Platform部",
    projects: 5,
    updatedAt: "2026/07/08",
    id: "ito",
    tone: "green",
  },
  {
    name: "渡辺 彩",
    role: "Business Designer",
    department: "新規事業部",
    projects: 2,
    updatedAt: "2026/07/04",
    id: "watanabe",
    tone: "rose",
  },
];

export function useMembersMock() {
  return useState<MockMember[]>("mock-members", () =>
    structuredClone(initialMembers),
  );
}
