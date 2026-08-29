import { useEffect, useRef, useState } from "react";
import "../../src/styles/fonts.css";
import "../../src/styles/theme.css";

const VIDEO_URL =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260328_083109_283f3553-e28f-428b-a723-d639c617eb2b.mp4";

const NAV_ITEMS = [
  { label: "Home", active: true },
  { label: "Studio", active: false },
  { label: "About", active: false },
  { label: "Journal", active: false },
  { label: "Reach Us", active: false },
];

export default function HeroSection() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [opacity, setOpacity] = useState(0);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const FADE_DURATION = 0.5;

    const tick = () => {
      if (video.paused || video.ended) return;

      const { currentTime, duration } = video;
      if (!duration) {
        animRef.current = requestAnimationFrame(tick);
        return;
      }

      const remaining = duration - currentTime;

      if (currentTime < FADE_DURATION) {
        setOpacity(currentTime / FADE_DURATION);
      } else if (remaining < FADE_DURATION) {
        setOpacity(remaining / FADE_DURATION);
      } else {
        setOpacity(1);
      }

      animRef.current = requestAnimationFrame(tick);
    };

    const onPlay = () => {
      animRef.current = requestAnimationFrame(tick);
    };

    const onEnded = () => {
      setOpacity(0);
      setTimeout(() => {
        video.currentTime = 0;
        video.play();
      }, 100);
    };

    video.addEventListener("play", onPlay);
    video.addEventListener("ended", onEnded);

    video.play().catch(() => {});

    return () => {
      cancelAnimationFrame(animRef.current);
      video.removeEventListener("play", onPlay);
      video.removeEventListener("ended", onEnded);
    };
  }, []);

  return (
    <div style={styles.container}>
      {/* Video Background */}
      <div style={styles.videoLayer}>
        <video
          ref={videoRef}
          style={{ ...styles.video, opacity }}
          src={VIDEO_URL}
          muted
          playsInline
          autoPlay
        />
        <div style={styles.gradientOverlay} />
      </div>

      {/* Navigation */}
      <nav style={styles.nav}>
        <div style={styles.navInner}>
          <div style={styles.logo}>
            Aethera<sup style={styles.trademark}>&reg;</sup>
          </div>

          <div style={styles.menuItems}>
            {NAV_ITEMS.map((item) => (
              <a
                key={item.label}
                href="#"
                style={{
                  ...styles.menuItem,
                  color: item.active ? "#000000" : "#6F6F6F",
                }}
                onMouseEnter={(e) => {
                  (e.target as HTMLElement).style.color = "#000000";
                }}
                onMouseLeave={(e) => {
                  (e.target as HTMLElement).style.color = item.active
                    ? "#000000"
                    : "#6F6F6F";
                }}
              >
                {item.label}
              </a>
            ))}
          </div>

          <button
            style={styles.ctaButton}
            onMouseEnter={(e) => {
              (e.target as HTMLElement).style.transform = "scale(1.03)";
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLElement).style.transform = "scale(1)";
            }}
          >
            Begin Journey
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div style={styles.hero}>
        <h1 style={styles.headline} className="animate-fade-rise">
          Beyond <span style={styles.italic}>silence,</span> we build{" "}
          <span style={styles.italic}>the eternal.</span>
        </h1>

        <p style={styles.description} className="animate-fade-rise-delay">
          Building platforms for brilliant minds, fearless makers, and
          thoughtful souls. Through the noise, we craft digital havens for deep
          work and pure flows.
        </p>

        <button
          style={styles.heroButton}
          className="animate-fade-rise-delay-2"
          onMouseEnter={(e) => {
            (e.target as HTMLElement).style.transform = "scale(1.03)";
          }}
          onMouseLeave={(e) => {
            (e.target as HTMLElement).style.transform = "scale(1)";
          }}
        >
          Begin Journey
        </button>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    position: "relative",
    minHeight: "100vh",
    width: "100%",
    overflow: "hidden",
    backgroundColor: "#FFFFFF",
    fontFamily: "'Inter', sans-serif",
  },
  videoLayer: {
    position: "absolute",
    inset: 0,
    zIndex: 0,
  },
  video: {
    position: "absolute",
    top: "300px",
    left: 0,
    right: 0,
    bottom: 0,
    width: "100%",
    height: "auto",
    minHeight: "100%",
    objectFit: "cover",
  },
  gradientOverlay: {
    position: "absolute",
    inset: 0,
    background:
      "linear-gradient(to bottom, #FFFFFF 0%, transparent 30%, transparent 70%, #FFFFFF 100%)",
    pointerEvents: "none",
  },
  nav: {
    position: "relative",
    zIndex: 10,
    padding: "24px 32px",
  },
  navInner: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    maxWidth: "1280px",
    margin: "0 auto",
  },
  logo: {
    fontSize: "30px",
    fontFamily: "'Instrument Serif', serif",
    letterSpacing: "-0.025em",
    color: "#000000",
    fontWeight: 400,
    lineHeight: 1,
  },
  trademark: {
    fontSize: "12px",
    verticalAlign: "super",
    fontFamily: "'Inter', sans-serif",
  },
  menuItems: {
    display: "flex",
    gap: "32px",
    alignItems: "center",
  },
  menuItem: {
    fontSize: "14px",
    fontFamily: "'Inter', sans-serif",
    textDecoration: "none",
    transition: "color 0.2s ease",
    cursor: "pointer",
    fontWeight: 400,
  },
  ctaButton: {
    backgroundColor: "#000000",
    color: "#FFFFFF",
    border: "none",
    borderRadius: "9999px",
    padding: "10px 24px",
    fontSize: "14px",
    fontFamily: "'Inter', sans-serif",
    fontWeight: 500,
    cursor: "pointer",
    transition: "transform 0.2s ease",
  },
  hero: {
    position: "relative",
    zIndex: 10,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    textAlign: "center",
    paddingTop: "calc(8rem - 75px)",
    paddingBottom: "10rem",
    paddingLeft: "24px",
    paddingRight: "24px",
  },
  headline: {
    fontSize: "clamp(2.5rem, 8vw, 6rem)",
    fontFamily: "'Instrument Serif', serif",
    fontWeight: 400,
    lineHeight: 0.95,
    letterSpacing: "-2.46px",
    color: "#000000",
    maxWidth: "1280px",
    margin: 0,
  },
  italic: {
    color: "#6F6F6F",
    fontStyle: "italic",
  },
  description: {
    fontSize: "clamp(1rem, 2vw, 1.125rem)",
    fontFamily: "'Inter', sans-serif",
    fontWeight: 400,
    lineHeight: 1.625,
    color: "#6F6F6F",
    maxWidth: "640px",
    marginTop: "32px",
  },
  heroButton: {
    backgroundColor: "#000000",
    color: "#FFFFFF",
    border: "none",
    borderRadius: "9999px",
    padding: "20px 56px",
    fontSize: "16px",
    fontFamily: "'Inter', sans-serif",
    fontWeight: 500,
    cursor: "pointer",
    marginTop: "48px",
    transition: "transform 0.2s ease",
  },
};
