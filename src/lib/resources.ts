export type ResourceNature = "rapport" | "soumis" | "depot" | "revue" | "livre";

export const NATURE_LABELS: Record<ResourceNature, string> = {
  rapport: "Rapport",
  soumis: "Soumis",
  depot: "Publié dans un dépôt",
  revue: "Publié dans une revue",
  livre: "Livre",
};

export type Resource = {
  id: string;
  slug: string;
  title: string;
  nature: ResourceNature;
  summary: string;
  vulgarisation: string;
  illustration_notes: string | null;
  illustration_url: string | null;
  pdf_url: string | null;
  downloadable: boolean;
  published_at: string | null;
};

// Seed entry shown when Supabase isn't configured yet, or as the first catalog entry.
export const SEED_RESOURCES: Resource[] = [
  {
    id: "seed-vol-1",
    slug: "twin-spaces-foundations",
    title: "Twin Spaces Foundations — Volume 1",
    nature: "livre",
    summary:
      "Premier tome de la collection Roots-Insights. Introduit la théorie des espaces jumeaux : " +
      "pour un magma muni d'une action de groupe (E, α, G), l'opération jumelle associée à g ∈ G " +
      "est x ⊙_g y := g⁻¹(g·x α g·y). Le livre établit le théorème de structure (l'espace des " +
      "opérations jumelles est l'espace homogène L\\G), la caractérisation du noyau, le théorème " +
      "de classification et le principe d'équivariance.",
    vulgarisation:
      "Imaginez une opération mathématique simple, comme l'addition. Si on la regarde à travers " +
      "un « filtre » différent à chaque fois (une action de groupe), on obtient toute une famille " +
      "de nouvelles opérations, toutes cousines de l'originale. Ce livre montre que cette famille " +
      "a toujours la même forme géométrique, quelle que soit l'opération de départ — un peu comme " +
      "un kaléidoscope qui produit des motifs différents à partir d'un même cristal.",
    illustration_notes:
      "Schéma du kaléidoscope algébrique : un magma central (E, α) entouré de ses opérations " +
      "jumelles ⊙_g, chacune reliée par une flèche représentant l'action de g ∈ G. Diagramme de " +
      "l'espace homogène L\\G illustrant la classification des opérations jumelles.",
    illustration_url: null,
    pdf_url: null,
    downloadable: false,
    published_at: "2026-01-01",
  },
];
