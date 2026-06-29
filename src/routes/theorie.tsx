import { createFileRoute } from "@tanstack/react-router";
import { SiteHeader } from "@/components/site/SiteHeader";
import { SiteFooter } from "@/components/site/SiteFooter";

export const Route = createFileRoute("/theorie")({
  head: () => ({
    meta: [{ title: "La théorie des espaces jumeaux" }],
  }),
  component: TheoryPage,
});

const theorems = [
  {
    name: "Théorème de structure",
    statement:
      "L'espace 𝒪 des opérations jumelles associées à (E, α, G) est isomorphe à l'espace " +
      "homogène L\\G, où L est le sous-groupe α-linéaire de G. C'est un groupe si et seulement si " +
      "L est distingué dans G.",
  },
  {
    name: "Caractérisation du noyau",
    statement: "g préserve α si et seulement si g est α-linéaire (g ∈ L).",
  },
  {
    name: "Théorème de classification",
    statement: "⊙_g = ⊙_h si et seulement si Lg = Lh.",
  },
  {
    name: "Principe d'équivariance",
    statement:
      "Toute propriété algébrique de α (associativité, commutativité, existence d'un élément " +
      "neutre, etc.) se transfère à l'opération jumelle ⊙_g.",
  },
];

const examples = [
  {
    title: "Transformée de Fourier",
    text: "La convolution et la multiplication ponctuelle sont deux opérations jumelles l'une de l'autre, liées par la transformée de Fourier comme action de groupe.",
  },
  {
    title: "Hiérarchie d'exponentiation",
    text: "Addition, multiplication, exponentiation et tétration apparaissent comme une chaîne d'opérations jumelles successives.",
  },
  {
    title: "Similitude matricielle",
    text: "La conjugaison de matrices par un groupe de changement de base produit des opérations jumelles correspondant aux différentes représentations d'un même opérateur.",
  },
  {
    title: "Transport optimal",
    text: "Les coûts de transport sous différents plans de couplage se comportent comme des opérations jumelles d'une opération de référence.",
  },
];

function TheoryPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <SiteHeader />
      <main className="flex-1">
        <section className="border-b border-border px-6 py-16">
          <div className="mx-auto max-w-3xl">
            <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Roots-Insights Collection · Volume 1
            </p>
            <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
              La théorie des espaces jumeaux
            </h1>
            <p className="mt-6 text-muted-foreground">
              La théorie des espaces jumeaux (Twin Spaces Theory) étudie comment une opération
              algébrique se déforme sous l'action d'un groupe, en engendrant toute une famille
              d'opérations "jumelles" structurellement liées à l'opération de départ.
            </p>
          </div>
        </section>

        <section className="border-b border-border bg-muted/30 px-6 py-16">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-semibold">La formule centrale</h2>
            <p className="mt-4 text-muted-foreground">
              Soit un magma muni d'une action de groupe (E, α, G) : un ensemble E muni d'une
              opération binaire α, et un groupe G agissant sur E. L'opération jumelle associée à g ∈
              G est définie par :
            </p>
            <div className="mt-6 rounded-md border border-border bg-background p-6 text-center font-mono text-lg">
              x ⊙<sub>g</sub> y := g⁻¹(g·x α g·y)
            </div>
            <p className="mt-6 text-muted-foreground">
              Cette construction est animée par le{" "}
              <strong className="text-foreground">principe de relativité opérationnelle</strong> :
              une opération algébrique n'a de sens absolu qu'à un point de vue (un g ∈ G) près.
            </p>
          </div>
        </section>

        <section className="border-b border-border px-6 py-16">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-semibold">Théorèmes clés</h2>
            <div className="mt-6 space-y-6">
              {theorems.map((t) => (
                <div key={t.name} className="rounded-md border border-border p-5">
                  <h3 className="font-semibold">{t.name}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{t.statement}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="px-6 py-16">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-2xl font-semibold">Exemples canoniques</h2>
            <div className="mt-6 grid gap-6 sm:grid-cols-2">
              {examples.map((ex) => (
                <div key={ex.title} className="rounded-md border border-border p-5">
                  <h3 className="font-semibold">{ex.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{ex.text}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
