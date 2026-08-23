export default function Compare() {
  return (
    <section className="view active">
      <div className="view-head">
        <div className="eyebrow">तुलना · COMPARE</div>
        <div className="view-title">Compare Groundwater Conditions</div>
        <div className="view-sub">
          Select two regions and years to view a side-by-side comparison built from the
          original assessment records.
        </div>
      </div>

      <div className="cmp-selectors">
        <div className="cmp-select-card">
          <div className="kpi-label">Region A</div>
          <div className="cmp-select-row">
            <select defaultValue="Haryana">
              <option>Haryana</option>
              <option>Punjab</option>
            </select>
            <select defaultValue="2020">
              <option>2020</option>
              <option>2022</option>
              <option>2024</option>
            </select>
          </div>
        </div>
        <div className="cmp-select-card b">
          <div className="kpi-label">Region B</div>
          <div className="cmp-select-row">
            <select defaultValue="Punjab">
              <option>Haryana</option>
              <option>Punjab</option>
            </select>
            <select defaultValue="2024">
              <option>2020</option>
              <option>2022</option>
              <option>2024</option>
            </select>
          </div>
        </div>
      </div>

      <div className="cmp-table">
        <div className="cmp-row head">
          <div className="cmp-cell label">Metric</div>
          <div className="cmp-cell">Haryana · 2020</div>
          <div className="cmp-cell" style={{ color: "var(--water-blue)" }}>
            Punjab · 2024
          </div>
        </div>
        <div className="cmp-row">
          <div className="cmp-cell label">Recharge</div>
          <div className="cmp-cell">
            <span className="cv">10.8</span> BCM
          </div>
          <div className="cmp-cell">
            <span className="cv">18.2</span> BCM
          </div>
        </div>
        <div className="cmp-row">
          <div className="cmp-cell label">Extraction</div>
          <div className="cmp-cell">
            <span className="cv">13.4</span> BCM
          </div>
          <div className="cmp-cell">
            <span className="cv">31.6</span> BCM
          </div>
        </div>
        <div className="cmp-row">
          <div className="cmp-cell label">Extraction Stage</div>
          <div className="cmp-cell">
            <span className="cv">124%</span>
          </div>
          <div className="cmp-cell">
            <span className="cv" style={{ color: "var(--over-exploited)" }}>
              174%
            </span>
          </div>
        </div>
        <div className="cmp-row">
          <div className="cmp-cell label">Category</div>
          <div className="cmp-cell">
            <span className="status-pill" style={{ background: "rgba(201,122,61,0.12)", color: "var(--critical)" }}>
              <span className="dot" style={{ background: "var(--critical)" }} />
              Critical
            </span>
          </div>
          <div className="cmp-cell">
            <span className="status-pill" style={{ background: "rgba(154,62,62,0.12)", color: "var(--over-exploited)" }}>
              <span className="dot" style={{ background: "var(--over-exploited)" }} />
              Over-Exploited
            </span>
          </div>
        </div>
      </div>

      <div className="cmp-diff">
        <div className="ai-insight" style={{ maxWidth: 1400 }}>
          <b>Key Differences</b>
          <p>
            Punjab&apos;s extraction stage runs 50 points higher than Haryana&apos;s 2020
            baseline, driven by intensive paddy cultivation and a denser tube-well network
            across the central districts.
          </p>
        </div>
      </div>
    </section>
  );
}
