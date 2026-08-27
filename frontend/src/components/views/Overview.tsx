import { useEffect, useState, useMemo } from "react";
import IndiaLeafletMap, { GroundwaterRecord } from "../IndiaLeafletMap";
import { fetchJson } from "../../lib/api";
import { STATUS_COLORS } from "../../data/stateMap";

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
  const [selectedState, setSelectedState] = useState<string | null>(null);
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

  const groundwaterMap = useMemo(() => {
    const map = new Map<string, GroundwaterRecord>();
    for (const s of statesSummary) {
      map.set(s.state, {
        state: s.state,
        assessment_year: s.latest_assessment_year,
        extraction_stage: s.avg_extraction_stage,
        category: s.avg_extraction_stage >= 100 ? 'Over-Exploited' :
                  s.avg_extraction_stage >= 90 ? 'Critical' :
                  s.avg_extraction_stage >= 70 ? 'Semi-Critical' : 'Safe',
      });
    }
    return map;
  }, [statesSummary]);

  const selectedSummary = selectedState ? statesSummary.find(s => s.state === selectedState) : null;

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
        <h1 className="hero-title">
          <span className="brand-hindi">जल</span>
          <span className="hero-title-line2">DRISTI</span>
        </h1>
        <p className="hero-sub">
          INGRES AI-powered groundwater intelligence platform for India
        </p>
        <p className="hero-sub-hindi">
          भारत के लिए INGRES AI संचालित भूजल बुद्धिमत्ता मंच। AI, स्थानिक विश्लेषण और ऐतिहासिक डेटा के माध्यम से भूजल का अन्वेषण करें।
        </p>
        <div className="hero-meta">
          <div className="hero-meta-item">
            <span className="hero-meta-label">States / UTs</span>
            <span className="hero-meta-value">{coverage?.states_covered ?? 0}</span>
          </div>
          <div className="hero-meta-item">
            <span className="hero-meta-label">Districts</span>
            <span className="hero-meta-value">{coverage?.districts_covered ?? 0}</span>
          </div>
          <div className="hero-meta-item">
            <span className="hero-meta-label">Assessment Units</span>
            <span className="hero-meta-value">{assessmentUnits}</span>
          </div>
          <div className="hero-meta-item">
            <span className="hero-meta-label">Data Source</span>
            <span className="hero-meta-value">CGWB / IN-GRES</span>
          </div>
          <div className="hero-meta-item">
            <span className="hero-meta-label">Total Records</span>
            <span className="hero-meta-value">{coverage?.total_records ?? 0}</span>
          </div>
        </div>
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
              <IndiaLeafletMap
                groundwaterData={groundwaterMap}
                selectedState={selectedState}
                onSelectState={setSelectedState}
              />
            </div>
          </div>
        </div>

        <div className="detail-panel">
          {!selectedState ? (
            <div className="detail-empty">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.4}>
                <path d="M9 4 3 6.5v14L9 18l6 2.5 6-2.5v-14L15 6.5 9 4Z" />
              </svg>
              Select a state on the map to open its groundwater intelligence card.
            </div>
          ) : selectedSummary ? (
            <>
              <div className="detail-head">
                <div className="detail-loc">{selectedState}</div>
                <div className="detail-year">{selectedSummary.latest_assessment_year} Dynamic Assessment</div>
                <span
                  className="status-pill"
                  style={{
                    background: `${STATUS_COLORS[selectedSummary.avg_extraction_stage >= 100 ? 'Over-Exploited' : selectedSummary.avg_extraction_stage >= 90 ? 'Critical' : selectedSummary.avg_extraction_stage >= 70 ? 'Semi-Critical' : 'Safe']}22`,
                    color: STATUS_COLORS[selectedSummary.avg_extraction_stage >= 100 ? 'Over-Exploited' : selectedSummary.avg_extraction_stage >= 90 ? 'Critical' : selectedSummary.avg_extraction_stage >= 70 ? 'Semi-Critical' : 'Safe'],
                  }}
                >
                  <span className="dot" style={{ background: STATUS_COLORS[selectedSummary.avg_extraction_stage >= 100 ? 'Over-Exploited' : selectedSummary.avg_extraction_stage >= 90 ? 'Critical' : selectedSummary.avg_extraction_stage >= 70 ? 'Semi-Critical' : 'Safe'] }} />
                  {selectedSummary.avg_extraction_stage >= 100 ? 'Over-Exploited' : selectedSummary.avg_extraction_stage >= 90 ? 'Critical' : selectedSummary.avg_extraction_stage >= 70 ? 'Semi-Critical' : 'Safe'}
                </span>
              </div>
              <div className="metric-list">
                <div className="metric-row">
                  <span className="metric-name metric-name-critical">Extraction Stage</span>
                  <span className="metric-num metric-num-critical">
                    {selectedSummary.avg_extraction_stage.toFixed(1)}%
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Districts</span>
                  <span className="metric-num">
                    {selectedSummary.districts}
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Blocks</span>
                  <span className="metric-num">
                    {selectedSummary.blocks}
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Category</span>
                  <span className="metric-num" style={{ color: STATUS_COLORS[selectedSummary.avg_extraction_stage >= 100 ? 'Over-Exploited' : selectedSummary.avg_extraction_stage >= 90 ? 'Critical' : selectedSummary.avg_extraction_stage >= 70 ? 'Semi-Critical' : 'Safe'] }}>
                    {selectedSummary.avg_extraction_stage >= 100 ? 'Over-Exploited' : selectedSummary.avg_extraction_stage >= 90 ? 'Critical' : selectedSummary.avg_extraction_stage >= 70 ? 'Semi-Critical' : 'Safe'}
                  </span>
                </div>
              </div>
              <div>
                <div className="trend-title">Historical Trend</div>
                <svg className="trend-chart" viewBox="0 0 260 60" width="100%" height="60">
                  <polyline
                    points="0,45 40,40 80,36 120,30 160,22 200,16 260,8"
                    fill="none"
                    stroke={STATUS_COLORS[selectedSummary.avg_extraction_stage >= 100 ? 'Over-Exploited' : selectedSummary.avg_extraction_stage >= 90 ? 'Critical' : selectedSummary.avg_extraction_stage >= 70 ? 'Semi-Critical' : 'Safe']}
                    strokeWidth={2}
                  />
                </svg>
              </div>
              <div className="detail-source">
                <span>Data Source</span>
                <b>CGWB / IN-GRES</b>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </section>
  );
}
