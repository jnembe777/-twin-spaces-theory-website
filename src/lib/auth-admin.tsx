import { createAuthContext } from "./createAuthContext";
import { supabase } from "./supabase";

// Single admin account, gated via Supabase Auth.
export const { AuthProvider: AdminAuthProvider, useAuth: useAdminAuth } =
  createAuthContext(supabase);
