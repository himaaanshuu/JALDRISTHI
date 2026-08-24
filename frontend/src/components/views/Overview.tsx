import { useEffect, useState } from "react";
import IndiaLeafletMap from "../IndiaLeafletMap";
import { fetchJson } from "../../lib/api";
import { statusColor, statusLabel, type StateData } from "../../data/states";

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
  total_recharge: number;
  total_extraction: number;
  avg_extraction_stage: number;
}

interface KpiCardData {
  label: string;
  value: string;
  unit: string;
  description: string;
  tone?: "default" | "water" | "demand" | "warning";
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2);
  if (n >= 1_000) return (n / 1_000).toFixed(1);
  return n.toFixed(1);
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
  const totalRecharge = coverage?.total_recharge ?? 0;
  const totalExtraction = coverage?.total_extraction ?? 0;
  const avgStage = coverage?.avg_extraction_stage ?? 0;

  const kpiCards: KpiCardData[] = [
    {
      label: "Assessment Units",
      value: assessmentUnits ? String(assessmentUnits) : "—",
      unit: "blocks",
      description: `${coverage?.states_covered ?? 0} states · ${coverage?.districts_covered ?? 0} districts`,
      tone: "default",
    },
    {
      label: "Groundwater Recharge",
      value: totalRecharge ? formatNumber(totalRecharge) : "—",
      unit: "MCM",
      description: "Annual groundwater recharge",
      tone: "water",
    },
    {
      label: "Groundwater Extraction",
      value: totalExtraction ? formatNumber(totalExtraction) : "—",
      unit: "MCM",
      description: "Total extraction volume",
      tone: "demand",
    },
    {
      label: "Avg Extraction Stage",
      value: avgStage ? avgStage.toFixed(1) : "—",
      unit: "%",
      description: `${overExploitedUnits} over-exploited units`,
      tone: avgStage > 90 ? "warning" : "default",
    },
  ];

  return (
    <section className="view active">
      <div className="ov-hero">
        <div className="eyebrow">
          CGWB · IN-GRES · National Assessment {coverage?.assessment_years.at(-1) ?? 2025}
        </div>
        <h1 className="hero-title">India Groundwater Intelligence</h1>
        <p className="hero-sub">
          Explore groundwater through AI, spatial intelligence and historical analysis
          across {assessmentUnits || 0} assessment units.
        </p>
      </div>

      <div className="kpi-strip">
        {kpiCards.map((card) => (
          <article className={`kpi kpi-${card.tone ?? "default"}`} key={card.label}>
            <div className="kpi-label">{card.label}</div>
            <div className="kpi-value">
              <span className="metric-amount">{card.value}</span>
              {card.unit && <span className="metric-unit-inline">{card.unit}</span>}
            </div>
            <div className="kpi-description">{card.description}</div>
          </article>
        ))}
      </div>

      <div className="ov-main">
        <div className="map-panel">
          <div className="map-panel-head">
            <div className="map-panel-title">
              Groundwater Categorisation
              <span>
                {coverage?.assessment_years.at(-1) ?? 2025} Dynamic Assessment · All States
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
                <div className="detail-year">2025 Dynamic Assessment</div>
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
                    {selected.ext}
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Recharge</span>
                  <span className="metric-num">
                    {selected.rech}
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Extractable Resource</span>
                  <span className="metric-num">
                    {selected.extractable}
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Groundwater Extraction</span>
                  <span className="metric-num">
                    {selected.exWater}
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
                <b>CGWB / IN-GRES</b>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
