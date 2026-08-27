import { useEffect, useState } from "react";
import { fetchJson } from "../../lib/api";

const datasets = [
  {
    name: "Dynamic Groundwater Resource Assessment",
    rows: [
      ["Source", "Original CGWB / State Board records"],
      ["Assessment Year", "2024"],
      ["Coverage", "7,089 units"],
      ["Last Updated", "Mar 2024"],
    ],
  },
  {
    name: "Historical Assessment Series",
    rows: [
      ["Source", "IN-GRES Archive"],
      ["Assessment Year", "2013–2024"],
      ["Coverage", "All States/UTs"],
      ["Last Updated", "Jan 2024"],
    ],
  },
  {
    name: "Rainfall & Recharge Estimates",
    rows: [
      ["Source", "IMD / CGWB"],
      ["Assessment Year", "2024"],
      ["Coverage", "District-level"],
      ["Last Updated", "Apr 2024"],
    ],
  },
];

interface CoverageSummary {
  total_records: number;
  official_records: number;
  demo_records: number;
  assessment_years: number[];
  states_covered: number;
  districts_covered: number;
  blocks_covered: number;
}

const ArrowIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
);

export default function DataSources() {
  const [coverage, setCoverage] = useState<CoverageSummary | null>(null);

  useEffect(() => {
    let active = true;

    fetchJson<CoverageSummary>("/api/data/coverage")
      .then((data) => {
        if (active) {
          setCoverage(data);
        }
      })
      .catch(() => {
        if (active) {
          setCoverage(null);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="view active">
      <div className="view-head">
        <div className="eyebrow">डेटा स्रोत · DATA SOURCES</div>
        <div className="view-title">Data &amp; Sources</div>
        <div className="view-sub">
          How official groundwater data flows into the intelligence layer.
        </div>
      </div>

      <div className="kpi-strip" style={{ marginTop: 18 }}>
        <div className="kpi">
          <div className="kpi-label">Live Records</div>
          <div className="kpi-value">{coverage?.total_records ?? "—"}</div>
          <div className="kpi-delta up">From /api/data/coverage</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">Official Records</div>
          <div className="kpi-value">{coverage?.official_records ?? "—"}</div>
          <div className="kpi-delta down">Synced from backend</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">States Covered</div>
          <div className="kpi-value">{coverage?.states_covered ?? "—"}</div>
          <div className="kpi-delta up">Live summary</div>
        </div>
        <div className="kpi">
          <div className="kpi-label">Latest Year</div>
          <div className="kpi-value">{coverage?.assessment_years.at(-1) ?? "—"}</div>
          <div className="kpi-delta up">Backend-driven</div>
        </div>
      </div>

      <div className="flow-row">
        <div className="flow-node">
          <div className="fn-name">CGWB</div>
          <div className="fn-desc">Central Ground Water Board field assessments</div>
        </div>
        <div className="flow-arrow">
          <ArrowIcon />
        </div>
        <div className="flow-node">
          <div className="fn-name">IN-GRES</div>
          <div className="fn-desc">National groundwater resource estimation system</div>
        </div>
        <div className="flow-arrow">
          <ArrowIcon />
        </div>
        <div className="flow-node">
          <div className="fn-name">जल DRISTHI</div>
          <div className="fn-desc">AI-powered spatial intelligence &amp; assistant layer</div>
        </div>
      </div>

      <div className="src-grid">
        {datasets.map((d) => (
          <div className="src-card" key={d.name}>
            <div className="sc-name">{d.name}</div>
            {d.rows.map(([k, v]) => (
              <div className="src-row" key={k}>
                <span>{k}</span>
                <span>{v}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="trust-split">
        <div className="trust-col official">
          <div className="trust-label">Official Data</div>
          <p>
            Sourced directly from original CGWB and IN-GRES assessment records. Figures
            such as recharge, extraction and category are reported exactly as published,
            with no modelling applied.
          </p>
        </div>
        <div className="trust-col derived">
          <div className="trust-label">AI-Derived Analytics</div>
          <p>
            Insights, trend narratives and comparisons generated from
            official data. Always labelled and shown with a confidence score and source
            trail.
          </p>
        </div>
      </div>
    </section>
  );
}
