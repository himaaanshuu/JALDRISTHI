import { useEffect, useState } from "react";
import IndiaLeafletMap from "../IndiaLeafletMap";
import { fetchJson } from "../../lib/api";
import { statusColor, statusLabel, type StateData } from "../../data/states";

const suggestions = [
  "Which districts are over-exploited?",
  "Compare Haryana between 2020 and 2024",
  "What changed in Uttar Pradesh?",
  "Show groundwater stress near Delhi",
];

interface StateSummary {
  state: string;
  districts: number;
  blocks: number;
  latest_assessment_year: number;
  avg_extraction_stage: number;
}

interface CoverageSummary {
  total_records: number;
  official_records: number;
  demo_records: number;
  assessment_years: number[];
  states_covered: number;
  districts_covered: number;
  blocks_covered: number;
}

interface KpiCardData {
  label: string;
  value: string;
  description: string;
  source: string;
  tone?: "default" | "water" | "demand" | "warning";
}

function splitValue(rawValue: string) {
  const trimmed = rawValue.trim();
  const match = trimmed.match(/^([\d.,]+)(.*)$/);

  if (!match) {
    return { amount: trimmed, unit: "" };
  }

  return {
    amount: match[1].trim(),
    unit: match[2].trim(),
  };
}

function MetricValue({ value }: { value: string }) {
  const { amount, unit } = splitValue(value);

  return (
    <span className="metric-value">
      <span className="metric-amount">{amount}</span>
      {unit ? <span className="metric-unit-inline">{unit}</span> : null}
    </span>
  );
}

export default function Overview() {
  const [selected, setSelected] = useState<StateData | null>(null);
  const [statesSummary, setStatesSummary] = useState<StateSummary[]>([]);
  const [coverage, setCoverage] = useState<CoverageSummary | null>(null);

  useEffect(() => {
    let active = true;

    Promise.all([fetchJson<StateSummary[]>("/api/states"), fetchJson<CoverageSummary>("/api/data/coverage")])
      .then(([statesData, coverageData]) => {
        if (!active) {
          return;
        }
        setStatesSummary(statesData);
        setCoverage(coverageData);
      })
      .catch(() => {
        if (active) {
          setStatesSummary([]);
          setCoverage(null);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const assessmentUnits = coverage?.blocks_covered ?? 0;
  const overExploitedUnits = statesSummary.filter((item) => item.avg_extraction_stage >= 100).length;

  const kpiCards: KpiCardData[] = [
    {
      label: "Assessment Units",
      value: coverage ? String(assessmentUnits) : "—",
      description: "Live from /api/data/coverage",
      source: "",
      tone: "default",
    },
    {
      label: "Groundwater Recharge",
      value: coverage ? String(coverage.official_records) : "—",
      description: "Official records",
      source: "Live from /api/states",
      tone: "water",
    },
    {
      label: "Extraction",
      value: coverage ? String(coverage.total_records) : "—",
      description: "Total records",
      source: "Live from /api/data/coverage",
      tone: "demand",
    },
    {
      label: "Over-Exploited Units",
      value: coverage ? String(overExploitedUnits) : "—",
      description: "Derived from live-state summaries",
      source: "",
      tone: "warning",
    },
  ];

  return (
    <section className="view active">
      <div className="ov-hero">
        <div className="eyebrow">
          CGWB · IN-GRES · National Assessment {coverage?.assessment_years.at(-1) ?? 2024}
        </div>
        <h1 className="hero-title">India Groundwater Intelligence</h1>
        <p className="hero-sub">
          Explore groundwater through AI, spatial intelligence and historical analysis
          across {assessmentUnits || 0} assessment units.
        </p>

        <div className="ai-search">
          <div className="ai-search-inner">
            <div className="ai-search-row">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6}>
                <path d="M12 2 3 7l9 5 9-5-9-5Z" />
                <path d="M3 12l9 5 9-5M3 17l9 5 9-5" />
              </svg>
              <input type="text" placeholder="Ask about India's groundwater…" />
              <button className="ai-search-go">
                Ask
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path d="M5 12h14M13 6l6 6-6 6" />
                </svg>
              </button>
            </div>
            <div className="suggest-row">
              {suggestions.map((s) => (
                <span className="chip" key={s}>
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="kpi-strip">
        {kpiCards.map((card) => (
          <article className={`kpi kpi-${card.tone ?? "default"}`} key={card.label}>
            <div className="kpi-label">{card.label}</div>
            <div className="kpi-value" style={card.tone === "warning" ? { color: "var(--over-exploited)" } : undefined}>
              <MetricValue value={card.value} />
            </div>
            <div className="kpi-description">{card.description}</div>
            {card.source ? <div className="kpi-source">{card.source}</div> : <div className="kpi-source kpi-source-empty" />}
          </article>
        ))}
      </div>

      <div className="ov-main">
        <div className="map-panel">
          <div className="map-panel-head">
            <div className="map-panel-title">
              Groundwater Categorisation
              <span>
                {coverage?.assessment_years.at(-1) ?? 2024} Dynamic Assessment · All States
              </span>
            </div>
            <div className="legend">
              <div className="legend-item">
                <span className="legend-dot" style={{ background: "var(--safe)" }} />
                Safe
              </div>
              <div className="legend-item">
                <span className="legend-dot" style={{ background: "var(--semi-critical)" }} />
                Semi-Critical
              </div>
              <div className="legend-item">
                <span className="legend-dot" style={{ background: "var(--critical)" }} />
                Critical
              </div>
              <div className="legend-item">
                <span className="legend-dot" style={{ background: "var(--over-exploited)" }} />
                Over-Exploited
              </div>
            </div>
          </div>
          <div className="map-stage">
            <div className="map-scanline" />
            <div className="map-leaflet-wrap">
              <IndiaLeafletMap onSelect={setSelected} selected={selected?.name ?? null} />
            </div>
          </div>
        </div>

        <div className="detail-panel">
          {!selected ? (
            <div className="detail-empty">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.4}>
                <path d="M9 4 3 6.5v14L9 18l6 2.5 6-2.5v-14L15 6.5 9 4Z" />
              </svg>
              Select a state on the map to open its groundwater intelligence card.
            </div>
          ) : (
            <>
              <div className="detail-head">
                <div className="detail-loc">{selected.name}</div>
                <div className="detail-year">2024 Dynamic Assessment</div>
                <span
                  className="status-pill"
                  style={{
                    background: `${statusColor[selected.status]}22`,
                    color: statusColor[selected.status],
                  }}
                >
                  <span className="dot" style={{ background: statusColor[selected.status] }} />
                  {statusLabel[selected.status]}
                </span>
              </div>
              <div className="metric-list">
                <div className="metric-row">
                  <span className="metric-name metric-name-critical">Extraction Stage</span>
                  <span className="metric-num metric-num-critical">
                    <MetricValue value={selected.ext} />
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Recharge</span>
                  <span className="metric-num">
                    <MetricValue value={selected.rech} />
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Extractable Resource</span>
                  <span className="metric-num">
                    <MetricValue value={selected.extractable} />
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Groundwater Extraction</span>
                  <span className="metric-num">
                    <MetricValue value={selected.exWater} />
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Category</span>
                  <span className="metric-num" style={{ color: statusColor[selected.status] }}>
                    {statusLabel[selected.status]}
                  </span>
                </div>
              </div>
              <div>
                <div className="trend-title">Historical Trend</div>
                <svg className="trend-chart" viewBox="0 0 260 60" width="100%" height="60">
                  <polyline
                    points="0,45 40,40 80,36 120,30 160,22 200,16 260,8"
                    fill="none"
                    stroke={statusColor[selected.status]}
                    strokeWidth={2}
                  />
                </svg>
              </div>
              <div className="detail-source">
                <span>Data Source</span>
                <b>{coverage ? `${coverage.official_records} original records` : "CGWB / IN-GRES"}</b>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
