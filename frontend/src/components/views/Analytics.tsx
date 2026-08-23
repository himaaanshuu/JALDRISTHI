const rankRows = [
  { rank: "01", name: "Karnal, HR", pct: 96, val: "196%", color: "var(--over-exploited)" },
  { rank: "02", name: "Sangrur, PB", pct: 90, val: "184%", color: "var(--over-exploited)" },
  { rank: "03", name: "Coimbatore, TN", pct: 78, val: "158%", color: "var(--critical)" },
  { rank: "04", name: "Mehsana, GJ", pct: 70, val: "142%", color: "var(--critical)" },
  { rank: "05", name: "Jaipur, RJ", pct: 63, val: "129%", color: "var(--semi-critical)" },
];

export default function Analytics() {
  return (
    <section className="view active">
      <div className="view-head">
        <div className="eyebrow">विश्लेषण · ANALYTICS</div>
        <div className="view-title">Analytics</div>
        <div className="view-sub">
          Trends, distribution and regional ranking across the national groundwater
          assessment.
        </div>
      </div>

      <div className="an-grid">
        <div className="an-card">
          <div className="an-card-title">Groundwater Trends</div>
          <div className="an-card-sub">National extraction vs. recharge, 2016–2024</div>
          <svg viewBox="0 0 560 200" width="100%" height="200">
            <line x1="0" y1="50" x2="560" y2="50" stroke="#E3E9E7" strokeWidth={1} />
            <line x1="0" y1="100" x2="560" y2="100" stroke="#E3E9E7" strokeWidth={1} />
            <line x1="0" y1="150" x2="560" y2="150" stroke="#E3E9E7" strokeWidth={1} />
            <polyline
              points="0,60 80,66 160,58 240,70 320,62 400,74 480,68 560,80"
              fill="none"
              stroke="var(--safe)"
              strokeWidth={2.2}
            />
            <polyline
              points="0,120 80,116 160,124 240,118 320,128 400,122 480,132 560,128"
              fill="none"
              stroke="var(--water-blue)"
              strokeWidth={2.2}
            />
          </svg>
          <div className="legend" style={{ marginTop: 6 }}>
            <div className="legend-item">
              <span className="legend-dot" style={{ background: "var(--water-blue)" }} />
              Extraction (BCM)
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ background: "var(--safe)" }} />
              Recharge (BCM)
            </div>
          </div>
        </div>

        <div className="an-card">
          <div className="an-card-title">Category Distribution</div>
          <div className="an-card-sub">Share of assessment units, 2024</div>
          <svg viewBox="0 0 200 200" width={180} height={180} style={{ display: "block", margin: "0 auto" }}>
            <circle r={70} cx={100} cy={100} fill="transparent" stroke="var(--safe)" strokeWidth={30} strokeDasharray="264 440" transform="rotate(-90 100 100)" />
            <circle r={70} cx={100} cy={100} fill="transparent" stroke="var(--semi-critical)" strokeWidth={30} strokeDasharray="70 440" strokeDashoffset={-264} transform="rotate(-90 100 100)" />
            <circle r={70} cx={100} cy={100} fill="transparent" stroke="var(--critical)" strokeWidth={30} strokeDasharray="44 440" strokeDashoffset={-334} transform="rotate(-90 100 100)" />
            <circle r={70} cx={100} cy={100} fill="transparent" stroke="var(--over-exploited)" strokeWidth={30} strokeDasharray="62 440" strokeDashoffset={-378} transform="rotate(-90 100 100)" />
          </svg>
        </div>

        <div className="an-card">
          <div className="an-card-title">Highest Extraction Regions</div>
          <div className="an-card-sub">Stage of extraction, top districts</div>
          {rankRows.map((r) => (
            <div className="rank-row" key={r.rank}>
              <span className="rank-num">{r.rank}</span>
              <span className="rank-name">{r.name}</span>
              <div className="rank-bar-track">
                <div className="rank-bar-fill" style={{ width: `${r.pct}%`, background: r.color }} />
              </div>
              <span className="rank-val">{r.val}</span>
            </div>
          ))}
        </div>

        <div className="an-card">
          <div className="an-card-title">Regional Comparison</div>
          <div className="an-card-sub">North vs. South zone extraction stage</div>
          <svg viewBox="0 0 300 150" width="100%" height={150}>
            <rect x={40} y={30} width={26} height={100} fill="var(--over-exploited)" />
            <rect x={90} y={55} width={26} height={75} fill="var(--critical)" />
            <rect x={140} y={70} width={26} height={60} fill="var(--semi-critical)" />
            <rect x={190} y={90} width={26} height={40} fill="var(--safe)" />
            <rect x={240} y={98} width={26} height={32} fill="var(--safe)" />
          </svg>
        </div>
      </div>
    </section>
  );
}
