import { createContext, useContext, useEffect, useState, useRef, type ReactNode } from "react";
import type { Session, User } from "@supabase/supabase-js";
import { supabase } from "../../lib/supabase";

interface AuthContextType {
  session: Session | null;
  user: User | null;
  loading: boolean;
  profileComplete: boolean;
  signInWithGoogle: () => Promise<void>;
  signInWithOtp: (phone: string) => Promise<{ error?: string }>;
  verifyOtp: (phone: string, token: string) => Promise<{ error?: string }>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [profileComplete, setProfileComplete] = useState(false);
  const initialSessionChecked = useRef(false);

  const checkProfile = async (userId: string) => {
    try {
      const { data } = await supabase
        .from("profiles")
        .select("full_name")
        .eq("auth_user_id", userId)
        .single();
      setProfileComplete(!!data?.full_name);
    } catch {
      setProfileComplete(false);
    }
  };

  useEffect(() => {
    // Get session first, but don't mark loading=false yet
    // onAuthStateChange with INITIAL_SESSION will do that
    supabase.auth.getSession().then(({ data: { session: s } }) => {
      setSession(s);
      setUser(s?.user ?? null);
      if (s?.user) checkProfile(s.user.id);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event: string, s: Session | null) => {
      if (!initialSessionChecked.current && event === "SIGNED_OUT") {
        return;
      }
      setSession(s);
      setUser(s?.user ?? null);
      if (s?.user) checkProfile(s.user.id);
      else setProfileComplete(false);
      if (!initialSessionChecked.current) {
        initialSessionChecked.current = true;
        setLoading(false);
      }
    });

    // Fallback: if onAuthStateChange never fires within 2s, stop loading
    const fallback = setTimeout(() => {
      if (!initialSessionChecked.current) {
        initialSessionChecked.current = true;
        setLoading(false);
      }
    }, 2000);

    return () => {
      subscription.unsubscribe();
      clearTimeout(fallback);
    };
  }, []);

  const signInWithGoogle = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) throw error;
  };

  const signInWithOtp = async (phone: string) => {
    const { error } = await supabase.auth.signInWithOtp({
      phone,
      options: { channel: "sms" },
    });
    if (error) return { error: error.message };
    return {};
  };

  const verifyOtp = async (phone: string, token: string) => {
    const { error } = await supabase.auth.verifyOtp({
      phone,
      token,
      type: "sms",
    });
    if (error) return { error: error.message };
    return {};
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    setSession(null);
    setUser(null);
    setProfileComplete(false);
  };

  const refreshProfile = async () => {
    if (user) await checkProfile(user.id);
  };

  return (
    <AuthContext.Provider
      value={{
        session,
        user,
        loading,
        profileComplete,
        signInWithGoogle,
        signInWithOtp,
        verifyOtp,
        signOut,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
