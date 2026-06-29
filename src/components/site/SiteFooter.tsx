import { Link } from "@tanstack/react-router";

export function SiteFooter() {
  return (
    <footer className="border-t border-border px-6 py-10">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 text-sm text-muted-foreground sm:flex-row">
        <p>Roots-Insights · Singapour · Libreville</p>
        <div className="flex items-center gap-6">
          <Link to="/theorie" className="hover:text-foreground">
            La théorie
          </Link>
          <Link to="/ressources" className="hover:text-foreground">
            Publications
          </Link>
          <Link to="/admin/login" className="hover:text-foreground">
            Espace administrateur
          </Link>
        </div>
      </div>
    </footer>
  );
}
