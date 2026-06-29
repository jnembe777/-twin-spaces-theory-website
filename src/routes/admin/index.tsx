import { useEffect, useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useAdminAuth } from "@/lib/auth-admin";
import { supabase, isSupabaseConfigured } from "@/lib/supabase";
import { NATURE_LABELS, SEED_RESOURCES, type Resource, type ResourceNature } from "@/lib/resources";

export const Route = createFileRoute("/admin/")({
  head: () => ({
    meta: [{ title: "Administration — Twin Spaces Theory" }],
  }),
  component: AdminDashboardPage,
});

const natures = Object.keys(NATURE_LABELS) as ResourceNature[];

function emptyForm() {
  return {
    title: "",
    slug: "",
    nature: "rapport" as ResourceNature,
    summary: "",
    vulgarisation: "",
    illustration_notes: "",
    downloadable: false,
    pdfFile: null as File | null,
  };
}

function AdminDashboardPage() {
  const { user, loading, signOut } = useAdminAuth();
  const navigate = useNavigate();
  const [resources, setResources] = useState<Resource[]>(SEED_RESOURCES);
  const [form, setForm] = useState(emptyForm());
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      void navigate({ to: "/admin/login" });
    }
  }, [loading, user, navigate]);

  async function loadResources() {
    if (!supabase) return;
    const { data } = await supabase
      .from("resources")
      .select("*")
      .order("published_at", { ascending: false });
    if (data) setResources(data as Resource[]);
  }

  useEffect(() => {
    void loadResources();
  }, []);

  async function handleDelete(resource: Resource) {
    if (!supabase) return;
    if (!confirm(`Supprimer « ${resource.title} » ?`)) return;
    await supabase.from("resources").delete().eq("id", resource.id);
    void loadResources();
  }

  async function handleToggleDownloadable(resource: Resource) {
    if (!supabase) return;
    await supabase
      .from("resources")
      .update({ downloadable: !resource.downloadable })
      .eq("id", resource.id);
    void loadResources();
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!supabase) return;
    setSubmitting(true);
    setFormError(null);

    let pdf_url: string | null = null;
    if (form.pdfFile) {
      const path = `${form.slug}-${Date.now()}.pdf`;
      const { error: uploadError } = await supabase.storage
        .from("resources-pdfs")
        .upload(path, form.pdfFile);
      if (uploadError) {
        setFormError(uploadError.message);
        setSubmitting(false);
        return;
      }
      const { data } = supabase.storage.from("resources-pdfs").getPublicUrl(path);
      pdf_url = data.publicUrl;
    }

    const { error } = await supabase.from("resources").insert({
      title: form.title,
      slug: form.slug,
      nature: form.nature,
      summary: form.summary,
      vulgarisation: form.vulgarisation,
      illustration_notes: form.illustration_notes || null,
      illustration_url: null,
      pdf_url,
      downloadable: form.downloadable,
      published_at: new Date().toISOString(),
    });

    setSubmitting(false);
    if (error) {
      setFormError(error.message);
      return;
    }
    setForm(emptyForm());
    void loadResources();
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <p className="text-sm text-muted-foreground">Chargement...</p>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <header className="border-b border-border">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <h1 className="text-base font-semibold">Administration des publications</h1>
          <button
            type="button"
            onClick={() => signOut()}
            className="rounded-md border border-input px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
          >
            Se déconnecter
          </button>
        </div>
      </header>

      <main className="flex-1 px-6 py-12">
        <div className="mx-auto max-w-5xl">
          {!isSupabaseConfigured && (
            <p className="mb-8 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
              Supabase n'est pas configuré — les actions d'administration sont désactivées.
            </p>
          )}

          <section>
            <h2 className="text-lg font-semibold">Importer une ressource</h2>
            <form onSubmit={handleSubmit} className="mt-4 grid gap-4 sm:grid-cols-2">
              <input
                required
                placeholder="Titre"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <input
                required
                placeholder="Slug (url)"
                value={form.slug}
                onChange={(e) => setForm({ ...form, slug: e.target.value })}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <select
                value={form.nature}
                onChange={(e) => setForm({ ...form, nature: e.target.value as ResourceNature })}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {natures.map((n) => (
                  <option key={n} value={n}>
                    {NATURE_LABELS[n]}
                  </option>
                ))}
              </select>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.downloadable}
                  onChange={(e) => setForm({ ...form, downloadable: e.target.checked })}
                />
                Téléchargeable
              </label>
              <textarea
                required
                placeholder="Résumé"
                value={form.summary}
                onChange={(e) => setForm({ ...form, summary: e.target.value })}
                className="col-span-full min-h-24 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <textarea
                required
                placeholder="Vulgarisation (langage familier)"
                value={form.vulgarisation}
                onChange={(e) => setForm({ ...form, vulgarisation: e.target.value })}
                className="col-span-full min-h-24 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <textarea
                placeholder="Notes d'illustration"
                value={form.illustration_notes}
                onChange={(e) => setForm({ ...form, illustration_notes: e.target.value })}
                className="col-span-full min-h-20 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setForm({ ...form, pdfFile: e.target.files?.[0] ?? null })}
                className="col-span-full text-sm"
              />
              {formError && <p className="col-span-full text-sm text-destructive">{formError}</p>}
              <button
                type="submit"
                disabled={submitting || !isSupabaseConfigured}
                className="col-span-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
              >
                {submitting ? "Import en cours..." : "Importer"}
              </button>
            </form>
          </section>

          <section className="mt-12">
            <h2 className="text-lg font-semibold">Publications existantes</h2>
            <div className="mt-4 divide-y divide-border rounded-md border border-border">
              {resources.map((r) => (
                <div key={r.id} className="flex items-center justify-between gap-4 p-4">
                  <div>
                    <p className="text-sm font-medium">{r.title}</p>
                    <p className="text-xs text-muted-foreground">{NATURE_LABELS[r.nature]}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleToggleDownloadable(r)}
                      className="rounded-md border border-input px-3 py-1.5 text-xs font-medium transition-colors hover:bg-accent"
                    >
                      {r.downloadable ? "Rendre non-téléchargeable" : "Rendre téléchargeable"}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(r)}
                      className="rounded-md border border-destructive/30 px-3 py-1.5 text-xs font-medium text-destructive transition-colors hover:bg-destructive/10"
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
