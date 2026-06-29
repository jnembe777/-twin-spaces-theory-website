import { createFileRoute, Link } from "@tanstack/react-router";
import { SiteHeader } from "@/components/site/SiteHeader";
import { SiteFooter } from "@/components/site/SiteFooter";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [{ title: "Twin Spaces Theory — Accueil" }],
  }),
  component: HomePage,
});

const interests = [
  "Algèbre structurelle et théorie des déformations",
  "Actions de groupe et homogénéité algébrique",
  "Cohomologie de Hochschild et structures opéradiques",
  "Algèbre quantique et catégorification",
  "Applications : transformée de Fourier, transport optimal, hiérarchies d'opérations",
];

export function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <SiteHeader />
      <main className="flex-1">
        <section className="border-b border-border px-6 py-20">
          <div className="mx-auto max-w-4xl text-center">
            <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Roots-Insights Collection
            </p>
            <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
              Twin Spaces Theory
            </h1>
            <p className="mt-6 text-lg text-muted-foreground">
              Une théorie de la déformation algébrique par actions de groupe : comment une opération
              binaire se transforme en une famille entière d'opérations "jumelles", toutes liées par
              une seule action de groupe.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Link
                to="/theorie"
                className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                Découvrir la théorie
              </Link>
              <Link
                to="/ressources"
                className="inline-flex items-center justify-center rounded-md border border-input px-5 py-2.5 text-sm font-medium transition-colors hover:bg-accent"
              >
                Parcourir les publications
              </Link>
            </div>
          </div>
        </section>

        <section className="px-6 py-20">
          <div className="mx-auto grid max-w-5xl gap-12 lg:grid-cols-[1fr_1.4fr]">
            <div>
              <h2 className="text-2xl font-semibold">L'auteur</h2>
              <p className="mt-4 text-muted-foreground">
                <strong className="text-foreground">Jocelyn Nembé</strong> est chercheur en
                mathématiques structurelles, rattaché au{" "}
                <em>National Institute of Management Sciences</em> de Libreville et au programme{" "}
                <em>Roots-Insights</em> de Singapour.
              </p>
              <p className="mt-4 text-muted-foreground">
                Il est l'initiateur de la théorie des espaces jumeaux (Twin Spaces Theory) et le
                fondateur de la collection Roots-Insights, un programme éditorial de 31 volumes
                consacré aux structures mathématiques transversales et à leurs applications en
                physique et en calcul.
              </p>
            </div>
            <div>
              <h2 className="text-2xl font-semibold">Sujets d'intérêt scientifique</h2>
              <ul className="mt-4 space-y-3">
                {interests.map((item) => (
                  <li key={item} className="flex gap-3 text-muted-foreground">
                    <span className="mt-2 h-1.5 w-1.5 flex-none rounded-full bg-primary" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className="border-t border-border bg-muted/30 px-6 py-20">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="text-2xl font-semibold">La collection Roots-Insights</h2>
            <p className="mt-4 text-muted-foreground">
              Le Volume 1, <em>Foundations</em>, pose les bases de la théorie des espaces jumeaux.
              Il inaugure un programme de 31 volumes répartis en six séries — Fondations,
              Structures, Logique &amp; Information, Physique &amp; Calcul, et des volumes
              d'application — publié conjointement à Singapour et à Libreville.
            </p>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
