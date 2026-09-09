import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './LandingPage.css';

const routes = {
  overview: '/dashboard',
  aiAssistant: '/ai-assistant',
  map: '/groundwater-map',
  learning: '/learning-centre',
  analytics: '/analytics',
};

const FEATURES = [
  {
    title: 'AI-Powered Insights',
    desc: 'Ask natural-language questions about groundwater and get evidence-backed answers from official CGWB and IN-GRES data.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2a7 7 0 0 1 7 7c0 5-7 13-7 13S5 14 5 9a7 7 0 0 1 7-7z" />
        <circle cx="12" cy="9" r="2.5" />
      </svg>
    ),
  },
  {
    title: 'Interactive Choropleth',
    desc: 'Explore extraction stages, water quality, and stress patterns across all 36 states and districts.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.2} strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M3 9h18M9 3v18" />
      </svg>
    ),
  },
  {
    title: 'Year-on-Year Trends',
    desc: 'Track groundwater movement from 2020 to 2026 — see which blocks are improving and which are declining.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.2} strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    title: 'Water Quality Index',
    desc: 'Assess pH, TDS, fluoride, nitrate, and iron against BIS and CGWB standards with colour-coded severity.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2C12 2 4 12 4 17a8 8 0 0 0 16 0c0-5-8-15-8-15z" />
      </svg>
    ),
  },
];

export default function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [navOpen, setNavOpen] = useState(false);

  const setAuthIntent = (intent: 'signin' | 'signup', target?: string) => {
    localStorage.setItem('jd-auth-intent', intent);
    if (target) localStorage.setItem('jd-auth-target', target);
  };

  // ---- Nav shrink on scroll ------------------------------------------
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // ---- Reveal-on-scroll for [data-reveal] ----------------------------
  useEffect(() => {
    const els = Array.from(document.querySelectorAll('[data-reveal]'));
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('is-in-view');
        });
      },
      { threshold: 0.2, rootMargin: '0px 0px -6% 0px' }
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  // ---- Canvas: nature scene — trees, water, underground layers ------
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let w = 0, h = 0, raf = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    const resize = () => {
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw(0);
    };

    const draw = (time: number) => {
      const t = time / 1000;
      ctx.clearRect(0, 0, w, h);

      // ---- sky gradient (dark green-teal) ----
      const skyGrad = ctx.createLinearGradient(0, 0, 0, h * 0.55);
      skyGrad.addColorStop(0, '#071a12');
      skyGrad.addColorStop(0.5, '#0c2a1c');
      skyGrad.addColorStop(1, '#0f3525');
      ctx.fillStyle = skyGrad;
      ctx.fillRect(0, 0, w, h * 0.55);

      // ---- ground / surface ----
      const groundY = h * 0.52;
      const gndGrad = ctx.createLinearGradient(0, groundY, 0, h);
      gndGrad.addColorStop(0, '#1a4a35');
      gndGrad.addColorStop(0.15, '#153d2c');
      gndGrad.addColorStop(0.4, '#0e2a1e');
      gndGrad.addColorStop(0.7, '#091f16');
      gndGrad.addColorStop(1, '#050e0a');
      ctx.fillStyle = gndGrad;
      ctx.fillRect(0, groundY, w, h - groundY);

      // ---- underground layer lines ----
      const layers = [0.60, 0.70, 0.82, 0.92];
      layers.forEach((ly, i) => {
        const y = h * ly;
        ctx.beginPath();
        ctx.moveTo(0, y);
        for (let x = 0; x <= w; x += 6) {
          ctx.lineTo(x, y + Math.sin(x * 0.008 + i * 1.7) * (3 + i * 1.5));
        }
        ctx.strokeStyle = `rgba(100,180,140,${0.06 + i * 0.02})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      });

      // ---- distant trees (back row) ----
      const treeCount = Math.max(8, Math.round(w / 90));
      for (let i = 0; i < treeCount; i++) {
        const bx = (w / (treeCount - 1)) * i;
        const baseY = groundY + 2 + Math.sin(i * 0.9) * 6;
        const treeH = 50 + Math.sin(i * 1.3) * 20;
        const sway = Math.sin(t * 0.3 + i * 0.7) * 2;

        ctx.fillStyle = `rgba(15,45,28,${0.5 + Math.sin(i) * 0.15})`;
        ctx.beginPath();
        ctx.moveTo(bx - 18 + sway, baseY);
        ctx.quadraticCurveTo(bx - 6 + sway, baseY - treeH * 0.6, bx + sway, baseY - treeH);
        ctx.quadraticCurveTo(bx + 6 + sway, baseY - treeH * 0.6, bx + 18 + sway, baseY);
        ctx.fill();
      }

      // ---- closer trees (front row) ----
      const frontCount = Math.max(5, Math.round(w / 140));
      for (let i = 0; i < frontCount; i++) {
        const fx = (w / (frontCount - 1)) * i + 30;
        const baseY = groundY - 4 + Math.sin(i * 2.1) * 4;
        const treeH = 70 + Math.sin(i * 1.7) * 25;
        const sway = Math.sin(t * 0.25 + i * 1.1) * 3;

        // trunk
        ctx.fillStyle = 'rgba(20,38,26,0.7)';
        ctx.fillRect(fx - 2.5 + sway * 0.3, baseY - treeH * 0.3, 5, treeH * 0.35);

        // canopy layers
        for (let j = 0; j < 3; j++) {
          const cy = baseY - treeH * 0.3 - j * treeH * 0.22;
          const cr = 22 - j * 4 + Math.sin(t * 0.4 + i + j) * 1.5;
          const green = 30 + j * 12;
          ctx.fillStyle = `rgba(${10 + j * 5},${green + 10},${15 + j * 6},0.85)`;
          ctx.beginPath();
          ctx.ellipse(fx + sway, cy, cr, cr * 0.7, 0, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // ---- waterfall ----
      const fallX = w * 0.5;
      const fallTop = groundY - 8;
      const fallBot = groundY + 80;
      const fallW = 18;

      // water stream
      for (let y = fallTop; y < fallBot; y += 2) {
        const progress = (y - fallTop) / (fallBot - fallTop);
        const spread = fallW * (1 + progress * 0.6);
        const wobble = Math.sin(y * 0.06 + t * 2) * 2;
        const alpha = 0.35 - progress * 0.15;
        ctx.fillStyle = `rgba(120,210,200,${alpha})`;
        ctx.fillRect(fallX - spread / 2 + wobble, y, spread, 3);
      }

      // splash at base
      for (let i = 0; i < 6; i++) {
        const sx = fallX + Math.sin(t * 3 + i * 1.2) * 20;
        const sy = fallBot + Math.sin(t * 2 + i) * 6;
        const sr = 2 + Math.sin(t * 4 + i) * 1;
        ctx.fillStyle = `rgba(160,230,220,${0.2 + Math.sin(t + i) * 0.1})`;
        ctx.beginPath();
        ctx.arc(sx, sy, sr, 0, Math.PI * 2);
        ctx.fill();
      }

      // ---- pool / river at base ----
      const poolY = groundY + 75;
      const poolGrad = ctx.createRadialGradient(fallX, poolY, 10, fallX, poolY, w * 0.25);
      poolGrad.addColorStop(0, 'rgba(80,180,170,0.25)');
      poolGrad.addColorStop(0.5, 'rgba(40,120,100,0.12)');
      poolGrad.addColorStop(1, 'rgba(10,50,40,0)');
      ctx.fillStyle = poolGrad;
      ctx.fillRect(0, poolY - 20, w, 50);

      // ---- mist / fog ----
      for (let i = 0; i < 4; i++) {
        const mx = (w * (0.2 + i * 0.2)) + Math.sin(t * 0.15 + i) * 30;
        const my = groundY + 10 + i * 15;
        const mw = 80 + i * 20;
        const mGrad = ctx.createRadialGradient(mx, my, 0, mx, my, mw);
        mGrad.addColorStop(0, `rgba(180,220,210,${0.06 - i * 0.01})`);
        mGrad.addColorStop(1, 'rgba(180,220,210,0)');
        ctx.fillStyle = mGrad;
        ctx.fillRect(mx - mw, my - mw, mw * 2, mw * 2);
      }

      // ---- subtle water drops floating up (firefly-like) ----
      for (let i = 0; i < 12; i++) {
        const dx = ((i * 137.5 + t * 8) % w);
        const dy = ((i * 89.3 + t * (5 + i * 0.5)) % h);
        const da = 0.08 + Math.sin(t * 0.8 + i * 2.3) * 0.06;
        ctx.fillStyle = `rgba(140,220,200,${da})`;
        ctx.beginPath();
        ctx.arc(dx, dy, 1.2, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    const loop = (time: number) => {
      draw(time);
      raf = requestAnimationFrame(loop);
    };

    resize();
    window.addEventListener('resize', resize);

    if (reduceMotion) {
      draw(0);
    } else {
      raf = requestAnimationFrame(loop);
    }

    return () => {
      window.removeEventListener('resize', resize);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div className="jd-landing" ref={rootRef}>
      <canvas ref={canvasRef} className="jd-canvas" aria-hidden="true" />

      {/* -------- NAV -------- */}
      <header className={`jd-nav ${scrolled ? 'jd-nav--scrolled' : ''}`}>
        <Link to="/" className="jd-nav__brand">
          <span className="jd-brand-text">जलDRISTHI</span>
        </Link>

        <nav className={`jd-nav__center ${navOpen ? 'is-open' : ''}`}>
          <button onClick={() => { setAuthIntent('signin', routes.map); navigate('/dashboard'); setNavOpen(false); }}>Map</button>
          <button onClick={() => { setAuthIntent('signin', routes.aiAssistant); navigate('/dashboard'); setNavOpen(false); }}>AI Assistant</button>
          <button onClick={() => { setAuthIntent('signin', routes.learning); navigate('/dashboard'); setNavOpen(false); }}>Learning</button>
          <button onClick={() => { setAuthIntent('signin', routes.analytics); navigate('/dashboard'); setNavOpen(false); }}>Analytics</button>
        </nav>

        <div className={`jd-nav__right ${navOpen ? 'is-open' : ''}`}>
          <button
            className="jd-nav__login"
            onClick={() => { setAuthIntent('signin'); navigate('/dashboard'); setNavOpen(false); }}
          >
            Sign In
          </button>
          <button
            className="jd-nav__signup"
            onClick={() => { setAuthIntent('signup'); navigate('/dashboard'); setNavOpen(false); }}
          >
            Sign Up
          </button>
        </div>

        <button
          className="jd-nav__burger"
          aria-label="Toggle navigation"
          aria-expanded={navOpen}
          onClick={() => setNavOpen((v) => !v)}
        >
          <span /><span /><span />
        </button>
      </header>

      {/* -------- HERO -------- */}
      <section className="jd-hero">
        <div className="jd-hero__content" data-reveal>
          <h1 className="jd-hero__title">
            An AI that reads the ground<br />
            while you <em>read the future.</em>
          </h1>
          <p className="jd-hero__sub">
            Groundwater intelligence platform that turns official CGWB and IN-GRES data
            into actionable insight — for every block, every year, every question.
          </p>
          <div className="jd-hero__cta">
            <button
              className="jd-cta-btn"
              onClick={() => { setAuthIntent('signup', routes.overview); navigate('/dashboard'); }}
            >
              Get started
            </button>
          </div>
        </div>
      </section>

      {/* -------- FEATURES -------- */}
      <section className="jd-features">
        <div className="jd-features__grid">
          {FEATURES.map((f, i) => (
            <div className="jd-feature-card" data-reveal key={f.title} style={{ transitionDelay: `${i * 100}ms` }}>
              <div className="jd-feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* -------- BOTTOM CTA -------- */}
      <section className="jd-bottom" data-reveal>
        <h2>Water is beneath everything.<br /><em>JALDRISTHI helps you see it.</em></h2>
        <div className="jd-bottom__cta">
          <button
            className="jd-cta-btn"
            onClick={() => { setAuthIntent('signup', routes.overview); navigate('/dashboard'); }}
          >
            Get started
          </button>
          <button
            className="jd-cta-btn jd-cta-btn--outline"
            onClick={() => { setAuthIntent('signin', routes.overview); navigate('/dashboard'); }}
          >
            Sign in
          </button>
        </div>
      </section>

      {/* -------- FOOTER -------- */}
      <footer className="jd-footer">
        <span className="jd-footer__brand">जलDRISTHI</span>
        <span className="jd-footer__copy">Groundwater Intelligence for a Sustainable India</span>
      </footer>
    </div>
  );
}
