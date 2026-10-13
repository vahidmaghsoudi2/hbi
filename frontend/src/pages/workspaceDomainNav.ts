export type WorkspacePanel =
  | "consult"
  | "previous"
  | "profile"
  | "catalog"
  | "review"
  | "intake"
  | "results"
  | "sales"
  | "about";

export type DomainKey = "customer" | "sales" | "product" | "about";

export const workspaceDomainNav: Record<
  DomainKey,
  { title: string; tabs: [WorkspacePanel, string][] }
> = {
  customer: {
    title: "مشتری و مشاوره",
    tabs: [
      ["consult", "ثبت مراجعه و مشاوره"],
      ["previous", "سوابق مراجعه"],
      ["profile", "پرونده مشتری"],
      ["results", "نتایج و پیشنهاد"],
    ],
  },
  sales: {
    title: "فروش",
    tabs: [["sales", "ثبت فروش"]],
  },
  product: {
    title: "پرونده محصول",
    tabs: [
      ["catalog", "فهرست محصولات"],
      ["review", "بررسی محصول"],
      ["intake", "ورود محصول"],
    ],
  },
  about: {
    title: "درباره",
    tabs: [["about", "درباره HBI"]],
  },
};

export function domainForPanel(panel: WorkspacePanel): DomainKey {
  if (panel === "sales") return "sales";
  if (panel === "catalog" || panel === "review" || panel === "intake") return "product";
  if (panel === "about") return "about";
  return "customer";
}
