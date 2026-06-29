import { useEffect, useState } from "react";
import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { SiteHeader } from "@/components/site/SiteHeader";
import { SiteFooter } from "@/components/site/SiteFooter";
import { supabase } from "@/lib/supabase";
import { NATURE_LABELS, SEED_RESOURCES, type Resource } from "@/lib/resources";

export const Route = createFileRoute("/ressources/$slug")({
  head: () => ({
    meta: [{ title: "Publication — Twin Spaces Theory" }],
  }),
  component: ResourceDetailPage,
});

function ResourceDetailPage() {
  const { slug } = Route.useParams();
  const seed = SEED_RESOURCES.find((r) => r.slug === slug) ?? null;
  const [resource, setResource] = useState<Resource | null>(seed);

  useEffect(() => {
    if (!supabase) return;
    supabase
      .from("resources")
      .select("*")
      .eq("slug", slug)
      .maybeSingle()
      .then(({ data }) => {
        if (data) setResource(data as Resource);
      });
  }, [slug]);

  if (!resource) {
    throw notFound();
  }

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <SiteHeader />
      <main className="flex-1 px-6 py-16">
        <div className="mx-auto max-w-3xl">
          <Link to="/ressources" className="text-sm text-muted-foreground hover:text-foreground">
            ← Retour aux publications
          </Link>

          <span className="mt-6 inline-flex rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
            {NATURE_LABELS[resource.nature]}
          </span>
          <h1 className="mt-3 text-3xl font-bold tracking-tight">{resource.title}</h1>

          <section className="mt-8">
            <h2 className="text-lg font-semibold">Résumé</h2>
            <p className="mt-2 text-muted-foreground">{resource.summary}</p>
          </section>

          <section className="mt-8">
            <h2 className="text-lg font-semibold">En langage familier</h2>
            <p className="mt-2 text-muted-foreground">{resource.vulgarisation}</p>
          </section>

          {resource.illustration_notes && (
            <section className="mt-8">
              <h2 className="text-lg font-semibold">Illustration</h2>
              <p className="mt-2 text-muted-foreground">{resource.illustration_notes}</p>
              {resource.illustration_url && (
                <img
                  src={resource.illustration_url}
                  alt={resource.title}
                  className="mt-4 rounded-md border border-border"
                />
              )}
            </section>
          )}

          <section className="mt-10">
            {resource.downloadable && resource.pdf_url ? (
              <a
                href={resource.pdf_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                Télécharger le PDF
              </a>
            ) : (
              <p className="text-sm text-muted-foreground">
                Le PDF de cette publication n'est pas disponible au téléchargement.
              </p>
            )}
          </section>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
