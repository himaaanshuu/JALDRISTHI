const sections = [
  "Executive Summary",
  "Groundwater Status",
  "Historical Analysis",
  "Critical Areas",
  "Key Changes",
  "Data Sources",
];

export default function Reports() {
  return (
    <section className="view active">
      <div className="view-head">
        <div className="eyebrow">रिपोर्ट्स · REPORTS</div>
        <div className="view-title">Reports</div>
        <div className="view-sub">
          Assemble a groundwater intelligence report from official assessment data.
        </div>
      </div>

      <div className="rep-shell">
        <div className="rep-side">
          <div className="col-title">Include Sections</div>
          {sections.map((s) => (
            <label className="rep-check" key={s}>
              <input type="checkbox" defaultChecked={s !== "Key Changes"} />
              {s}
            </label>
          ))}
          <div className="rep-actions">
            <button className="btn btn-primary">Generate Report</button>
            <button className="btn btn-ghost">Export</button>
          </div>
        </div>

        <div className="rep-preview">
          <h2>Groundwater Intelligence Report — Haryana</h2>
          <div className="rp-meta">
            Assessment Year 2024 · Generated from CGWB / IN-GRES · Prepared by जलदृष्टि DRISTI
          </div>
          <div className="rep-sec">
            <h4>Executive Summary</h4>
            <p>
              Haryana&apos;s groundwater balance remains under sustained pressure, with
              extraction exceeding recharge across 71% of assessed blocks in 2024.
            </p>
          </div>
          <div className="rep-sec">
            <h4>Groundwater Status</h4>
            <p>
              Of 143 assessment units, 61 are classified Over-Exploited, 24 Critical, 19
              Semi-Critical and 39 Safe.
            </p>
          </div>
          <div className="rep-sec">
            <h4>Historical Analysis</h4>
            <p>
              Extraction stage has risen steadily since 2013, with the sharpest increase
              recorded between 2020 and 2022.
            </p>
          </div>
          <div className="rep-sec">
            <h4>Critical Areas</h4>
            <p>Karnal, Kaithal and Kurukshetra continue to record extraction stages above 180%.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
