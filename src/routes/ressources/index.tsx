import { useEffect, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { SiteHeader } from "@/components/site/SiteHeader";
import { SiteFooter } from "@/components/site/SiteFooter";
import { supabase } from "@/lib/supabase";
import { NATURE_LABELS, SEED_RESOURCES, type Resource, type ResourceNature } from "@/lib/resources";

export const Route = createFileRoute("/ressources/")({
  head: () => ({
    meta: [{ title: "Publications — Twin Spaces Theory" }],
  }),
  component: ResourcesPage,
});

const natures = Object.keys(NATURE_LABELS) as ResourceNature[];

function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>(SEED_RESOURCES);
  const [filter, setFilter] = useState<ResourceNature | "all">("all");

  useEffect(() => {
    if (!supabase) return;
    supabase
      .from("resources")
      .select("*")
      .order("published_at", { ascending: false })
      .then(({ data }) => {
        if (data && data.length > 0) setResources(data as Resource[]);
      });
  }, []);

  const filtered = filter === "all" ? resources : resources.filter((r) => r.nature === filter);

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <SiteHeader />
      <main className="flex-1 px-6 py-16">
        <div className="mx-auto max-w-5xl">
          <h1 className="text-3xl font-bold tracking-tight">Publications</h1>
          <p className="mt-2 text-muted-foreground">
            Articles et livres présentés par nature de publication.
          </p>

          <div className="mt-8 flex flex-wrap gap-2">
            <button
              onClick={() => setFilter("all")}
              className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
                filter === "all"
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-input hover:bg-accent"
              }`}
            >
              Tout
            </button>
            {natures.map((n) => (
              <button
                key={n}
                onClick={() => setFilter(n)}
                className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
                  filter === n
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-input hover:bg-accent"
                }`}
              >
                {NATURE_LABELS[n]}
              </button>
            ))}
          </div>

          <div className="mt-10 grid gap-6 sm:grid-cols-2">
            {filtered.map((r) => (
              <Link
                key={r.id}
                to="/ressources/$slug"
                params={{ slug: r.slug }}
                className="block rounded-md border border-border p-6 transition-colors hover:bg-accent"
              >
                <span className="inline-flex rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
                  {NATURE_LABELS[r.nature]}
                </span>
                <h2 className="mt-3 text-lg font-semibold">{r.title}</h2>
                <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">{r.summary}</p>
              </Link>
            ))}
            {filtered.length === 0 && (
              <p className="text-muted-foreground">Aucune publication dans cette catégorie.</p>
            )}
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
