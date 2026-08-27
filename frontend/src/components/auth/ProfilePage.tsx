import { useEffect, useState } from "react";
import { useAuth } from "./AuthContext";
import { supabase } from "../../lib/supabase";

interface Profile {
  id: string;
  auth_user_id: string;
  full_name: string;
  email: string;
  phone: string;
  avatar_url: string;
  role: string;
  created_at: string;
  updated_at: string;
}

export default function ProfilePage() {
  const { user, signOut } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      fetchProfile();
    }
  }, [user]);

  const fetchProfile = async () => {
    if (!user) return;
    const { data, error } = await supabase
      .from("profiles")
      .select("*")
      .eq("auth_user_id", user.id)
      .single();

    if (data) {
      setProfile(data);
      setFullName(data.full_name || "");
    } else if (error && error.code === "PGRST116") {
      // Profile doesn't exist, create it
      const newProfile = {
        auth_user_id: user.id,
        full_name: user.user_metadata?.full_name || user.user_metadata?.name || "",
        email: user.email || "",
        phone: user.phone || "",
        avatar_url: user.user_metadata?.avatar_url || "",
        role: "user",
      };
      const { data: created } = await supabase
        .from("profiles")
        .insert(newProfile)
        .select()
        .single();
      if (created) {
        setProfile(created);
        setFullName(created.full_name || "");
      }
    }
  };

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    await supabase
      .from("profiles")
      .update({ full_name: fullName, updated_at: new Date().toISOString() })
      .eq("id", profile.id);
    setProfile({ ...profile, full_name: fullName });
    setEditing(false);
    setSaving(false);
  };

  if (!user) return null;

  const provider = user.app_metadata?.provider;
  const avatarUrl = user.user_metadata?.avatar_url;

  return (
    <div className="profile-page">
      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            {avatarUrl ? (
              <img src={avatarUrl} alt="Avatar" />
            ) : (
              <div className="profile-avatar-placeholder">
                {(profile?.full_name || user.email || "U")[0].toUpperCase()}
              </div>
            )}
          </div>
          <div className="profile-info">
            <h2>{profile?.full_name || "User"}</h2>
            <p>{user.email || user.phone}</p>
            <span className="profile-provider">
              Signed in with {provider === "google" ? "Google" : "Mobile OTP"}
            </span>
          </div>
        </div>

        <div className="profile-details">
          <div className="profile-field">
            <label>Full Name</label>
            {editing ? (
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="profile-input"
              />
            ) : (
              <span>{profile?.full_name || "Not set"}</span>
            )}
          </div>
          <div className="profile-field">
            <label>Email</label>
            <span>{user.email || "Not available"}</span>
          </div>
          <div className="profile-field">
            <label>Phone</label>
            <span>{user.phone || "Not available"}</span>
          </div>
          <div className="profile-field">
            <label>Role</label>
            <span className="profile-role">{profile?.role || "user"}</span>
          </div>
        </div>

        <div className="profile-actions">
          {editing ? (
            <>
              <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? "Saving..." : "Save Changes"}
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  setEditing(false);
                  setFullName(profile?.full_name || "");
                }}
              >
                Cancel
              </button>
            </>
          ) : (
            <button className="btn btn-primary" onClick={() => setEditing(true)}>
              Edit Profile
            </button>
          )}
          <button className="btn btn-ghost" onClick={signOut}>
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
