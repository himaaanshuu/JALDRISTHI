import { useEffect, useState, useRef } from "react";
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

const AUTH_VIDEO_URL =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_083109_283f3553-e28f-428b-a723-d639c617eb2b.mp4";

export default function ProfilePage() {
  const { user, signOut } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const animFrameRef = useRef<number>(0);
  const [videoOpacity, setVideoOpacity] = useState(0);

  useEffect(() => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const video = videoRef.current;
    if (!video) return;

    const FADE_DURATION = 0.5;

    const tick = () => {
      if (video.paused || video.ended) return;
      const { currentTime, duration } = video;
      if (!duration) {
        animFrameRef.current = requestAnimationFrame(tick);
        return;
      }
      const remaining = duration - currentTime;
      if (currentTime < FADE_DURATION) {
        setVideoOpacity(currentTime / FADE_DURATION);
      } else if (remaining < FADE_DURATION) {
        setVideoOpacity(remaining / FADE_DURATION);
      } else {
        setVideoOpacity(1);
      }
      animFrameRef.current = requestAnimationFrame(tick);
    };

    const onPlay = () => {
      animFrameRef.current = requestAnimationFrame(tick);
    };

    const onEnded = () => {
      setVideoOpacity(0);
      setTimeout(() => {
        video.currentTime = 0;
        video.play();
      }, 100);
    };

    video.addEventListener("play", onPlay);
    video.addEventListener("ended", onEnded);
    video.play().catch(() => {});

    return () => {
      cancelAnimationFrame(animFrameRef.current);
      video.removeEventListener("play", onPlay);
      video.removeEventListener("ended", onEnded);
    };
  }, []);

  useEffect(() => {
    if (user) fetchProfile();
  }, [user]);

  const fetchProfile = async () => {
    if (!user) return;
    const { data } = await supabase
      .from("profiles")
      .select("*")
      .eq("auth_user_id", user.id)
      .single();
    if (data) {
      setProfile(data);
      setFullName(data.full_name || "");
      setEmail(data.email || "");
      setPhone(data.phone || "");
    }
  };

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    const { error } = await supabase
      .from("profiles")
      .update({
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phone.trim(),
        updated_at: new Date().toISOString(),
      })
      .eq("id", profile.id);
    setSaving(false);
    if (!error) {
      setProfile({ ...profile, full_name: fullName, email, phone });
      setEditing(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
  };

  if (!user) return null;

  const provider = user.app_metadata?.provider;
  const avatarUrl = user.user_metadata?.avatar_url;

  return (
    <div className="profile-page">
      <video
        ref={videoRef}
        className="auth-bg-video"
        style={{ opacity: videoOpacity }}
        src={AUTH_VIDEO_URL}
        muted
        playsInline
        loop={false}
      />
      <div className="auth-bg-overlay" />
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
            <p>{profile?.email || user.email || user.phone}</p>
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
            {editing ? (
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="profile-input"
                placeholder="your@email.com"
              />
            ) : (
              <span>{profile?.email || "Not set"}</span>
            )}
          </div>
          <div className="profile-field">
            <label>Mobile Number</label>
            {editing ? (
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="profile-input"
                placeholder="+91 9876543210"
              />
            ) : (
              <span>{profile?.phone || "Not set"}</span>
            )}
          </div>
          <div className="profile-field">
            <label>Role</label>
            <span className="profile-role">{profile?.role || "user"}</span>
          </div>
          <div className="profile-field">
            <label>Member Since</label>
            <span>{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : "N/A"}</span>
          </div>
        </div>

        <div className="profile-actions">
          {editing ? (
            <>
              <button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={saving || !fullName.trim()}
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  setEditing(false);
                  setFullName(profile?.full_name || "");
                  setEmail(profile?.email || "");
                  setPhone(profile?.phone || "");
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

        {saved && (
          <div style={{
            padding: "12px",
            textAlign: "center",
            color: "#27ae60",
            fontFamily: "var(--font-ui)",
            fontSize: 13,
            borderTop: "1px solid rgba(255,255,255,0.06)",
          }}>
            Profile updated successfully
          </div>
        )}
      </div>
    </div>
  );
}
