import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { Session, SupabaseClient, User } from "@supabase/supabase-js";

export type AuthContextValue = {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signUp: (email: string, password: string) => Promise<{ error: string | null }>;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
};

export function createAuthContext(client: SupabaseClient | null) {
  const AuthContext = createContext<AuthContextValue | null>(null);

  function AuthProvider({ children }: { children: ReactNode }) {
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(Boolean(client));

    useEffect(() => {
      if (!client) return;

      client.auth.getSession().then(({ data }) => {
        setSession(data.session);
        setLoading(false);
      });

      const { data: subscription } = client.auth.onAuthStateChange((_event, newSession) => {
        setSession(newSession);
      });

      return () => subscription.subscription.unsubscribe();
    }, []);

    async function signUp(email: string, password: string) {
      if (!client) return { error: "Supabase n'est pas configuré." };
      const { error } = await client.auth.signUp({ email, password });
      return { error: error?.message ?? null };
    }

    async function signIn(email: string, password: string) {
      if (!client) return { error: "Supabase n'est pas configuré." };
      const { error } = await client.auth.signInWithPassword({ email, password });
      return { error: error?.message ?? null };
    }

    async function signOut() {
      if (!client) return;
      await client.auth.signOut();
    }

    return (
      <AuthContext.Provider
        value={{ user: session?.user ?? null, session, loading, signUp, signIn, signOut }}
      >
        {children}
      </AuthContext.Provider>
    );
  }

  function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within its matching AuthProvider");
    return ctx;
  }

  return { AuthProvider, useAuth };
}
