import { useEffect, useState } from "react";
import { fetchJson } from "../../lib/api";

interface StateSummary {
  state: string;
  districts: number;
  blocks: number;
  latest_assessment_year: number;
  avg_extraction_stage: number;
}

interface YearCompare {
  state: string;
  year1: number;
  year2: number;
  year1_data: { total_recharge: number; total_extraction: number; extraction_stage: number; category: string };
  year2_data: { total_recharge: number; total_extraction: number; extraction_stage: number; category: string };
  changes: {
    recharge_delta: number;
    extraction_delta: number;
    stage_delta: number;
    category_changed: boolean;
    blocks_improved: number;
    blocks_deteriorated: number;
  };
}

const years = [2020, 2022, 2024, 2025];

export default function Compare() {
  const [states, setStates] = useState<StateSummary[]>([]);
  const [stateA, setStateA] = useState("Haryana");
  const [stateB, setStateB] = useState("Punjab");
  const [yearA, setYearA] = useState(2020);
  const [yearB, setYearB] = useState(2024);
  const [compareA, setCompareA] = useState<YearCompare | null>(null);
  const [compareB, setCompareB] = useState<YearCompare | null>(null);

  useEffect(() => {
    fetchJson<StateSummary[]>("/api/states")
      .then((data) => setStates(data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (stateA && yearA && yearB) {
      fetchJson<YearCompare>(`/api/groundwater/year-compare?state=${encodeURIComponent(stateA)}&year1=${yearA}&year2=${yearB}`)
        .then(setCompareA)
        .catch(() => setCompareA(null));
    }
  }, [stateA, yearA, yearB]);

  useEffect(() => {
    if (stateB && yearA && yearB) {
      fetchJson<YearCompare>(`/api/groundwater/year-compare?state=${encodeURIComponent(stateB)}&year1=${yearA}&year2=${yearB}`)
        .then(setCompareB)
        .catch(() => setCompareB(null));
    }
  }, [stateB, yearA, yearB]);

  const getCategoryColor = (cat: string) => {
    const map: Record<string, string> = {
      Safe: "var(--safe)",
      "Semi-Critical": "var(--semi-critical)",
      Critical: "var(--critical)",
      "Over-Exploited": "var(--over-exploited)",
    };
    return map[cat] || "var(--text-secondary)";
  };

  return (
    <section className="view active">
      <div className="ov-hero">
        <div className="eyebrow">तुलना · COMPARE</div>
        <h1 className="hero-title">
          Year-over-Year
          <span className="hero-title-line2">Comparison</span>
        </h1>
        <p className="hero-sub">
          Compare groundwater conditions between two states across different assessment years.
          See how extraction, recharge, and categories have changed.
        </p>
        <p className="hero-sub-hindi">
          दो राज्यों की विभिन्न मूल्यांकन वर्षों में भूजल स्थितियों की तुलना करें।
        </p>
      </div>

      <div className="cmp-selectors">
        <div className="cmp-select-card">
          <div className="kpi-label">State A</div>
          <div className="cmp-select-row">
            <select value={stateA} onChange={(e) => setStateA(e.target.value)}>
              {states.map((s) => (
                <option key={s.state} value={s.state}>{s.state}</option>
              ))}
            </select>
            <select value={yearA} onChange={(e) => setYearA(Number(e.target.value))}>
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            <span className="cmp-vs">vs</span>
            <select value={yearB} onChange={(e) => setYearB(Number(e.target.value))}>
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="cmp-select-card b">
          <div className="kpi-label">State B</div>
          <div className="cmp-select-row">
            <select value={stateB} onChange={(e) => setStateB(e.target.value)}>
              {states.map((s) => (
                <option key={s.state} value={s.state}>{s.state}</option>
              ))}
            </select>
            <select value={yearA} onChange={(e) => setYearA(Number(e.target.value))}>
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            <span className="cmp-vs">vs</span>
            <select value={yearB} onChange={(e) => setYearB(Number(e.target.value))}>
              {years.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {(compareA || compareB) && (
        <div className="cmp-table-wrap">
          <div className="cmp-table">
            <div className="cmp-row head">
              <div className="cmp-cell label">Metric</div>
              <div className="cmp-cell" style={{ textAlign: "center" }}>
                {stateA} · {yearA}
              </div>
              <div className="cmp-cell" style={{ textAlign: "center" }}>
                {stateA} · {yearB}
              </div>
              <div className="cmp-cell" style={{ textAlign: "center" }}>
                {stateB} · {yearA}
              </div>
              <div className="cmp-cell" style={{ textAlign: "center" }}>
                {stateB} · {yearB}
              </div>
            </div>

            <div className="cmp-row">
              <div className="cmp-cell label">Recharge (BCM)</div>
              <div className="cmp-cell">{compareA?.year1_data.total_recharge.toFixed(1) ?? "—"}</div>
              <div className="cmp-cell">{compareA?.year2_data.total_recharge.toFixed(1) ?? "—"}</div>
              <div className="cmp-cell">{compareB?.year1_data.total_recharge.toFixed(1) ?? "—"}</div>
              <div className="cmp-cell">{compareB?.year2_data.total_recharge.toFixed(1) ?? "—"}</div>
            </div>

            <div className="cmp-row">
              <div className="cmp-cell label">Extraction (BCM)</div>
              <div className="cmp-cell">{compareA?.year1_data.total_extraction.toFixed(1) ?? "—"}</div>
              <div className="cmp-cell">{compareA?.year2_data.total_extraction.toFixed(1) ?? "—"}</div>
              <div className="cmp-cell">{compareB?.year1_data.total_extraction.toFixed(1) ?? "—"}</div>
              <div className="cmp-cell">{compareB?.year2_data.total_extraction.toFixed(1) ?? "—"}</div>
            </div>

            <div className="cmp-row">
              <div className="cmp-cell label">Extraction Stage</div>
              <div className="cmp-cell">
                <span style={{ color: getCategoryColor(compareA?.year1_data.category ?? "") }}>
                  {compareA?.year1_data.extraction_stage.toFixed(1) ?? "—"}%
                </span>
              </div>
              <div className="cmp-cell">
                <span style={{ color: getCategoryColor(compareA?.year2_data.category ?? "") }}>
                  {compareA?.year2_data.extraction_stage.toFixed(1) ?? "—"}%
                </span>
              </div>
              <div className="cmp-cell">
                <span style={{ color: getCategoryColor(compareB?.year1_data.category ?? "") }}>
                  {compareB?.year1_data.extraction_stage.toFixed(1) ?? "—"}%
                </span>
              </div>
              <div className="cmp-cell">
                <span style={{ color: getCategoryColor(compareB?.year2_data.category ?? "") }}>
                  {compareB?.year2_data.extraction_stage.toFixed(1) ?? "—"}%
                </span>
              </div>
            </div>

            <div className="cmp-row">
              <div className="cmp-cell label">Category</div>
              <div className="cmp-cell">
                <span className="status-pill" style={{ background: `${getCategoryColor(compareA?.year1_data.category ?? "")}15`, color: getCategoryColor(compareA?.year1_data.category ?? "") }}>
                  <span className="dot" style={{ background: getCategoryColor(compareA?.year1_data.category ?? "") }} />
                  {compareA?.year1_data.category ?? "—"}
                </span>
              </div>
              <div className="cmp-cell">
                <span className="status-pill" style={{ background: `${getCategoryColor(compareA?.year2_data.category ?? "")}15`, color: getCategoryColor(compareA?.year2_data.category ?? "") }}>
                  <span className="dot" style={{ background: getCategoryColor(compareA?.year2_data.category ?? "") }} />
                  {compareA?.year2_data.category ?? "—"}
                </span>
              </div>
              <div className="cmp-cell">
                <span className="status-pill" style={{ background: `${getCategoryColor(compareB?.year1_data.category ?? "")}15`, color: getCategoryColor(compareB?.year1_data.category ?? "") }}>
                  <span className="dot" style={{ background: getCategoryColor(compareB?.year1_data.category ?? "") }} />
                  {compareB?.year1_data.category ?? "—"}
                </span>
              </div>
              <div className="cmp-cell">
                <span className="status-pill" style={{ background: `${getCategoryColor(compareB?.year2_data.category ?? "")}15`, color: getCategoryColor(compareB?.year2_data.category ?? "") }}>
                  <span className="dot" style={{ background: getCategoryColor(compareB?.year2_data.category ?? "") }} />
                  {compareB?.year2_data.category ?? "—"}
                </span>
              </div>
            </div>

            <div className="cmp-row">
              <div className="cmp-cell label">Stage Change</div>
              <div className="cmp-cell" style={{ gridColumn: "span 2" }}>
                {compareA?.changes.stage_delta !== undefined ? (
                  <span style={{ color: compareA.changes.stage_delta > 0 ? "var(--over-exploited)" : compareA.changes.stage_delta < 0 ? "var(--safe)" : "var(--text-secondary)" }}>
                    {compareA.changes.stage_delta > 0 ? "+" : ""}{compareA.changes.stage_delta.toFixed(1)}%
                  </span>
                ) : "—"}
              </div>
              <div className="cmp-cell" style={{ gridColumn: "span 2" }}>
                {compareB?.changes.stage_delta !== undefined ? (
                  <span style={{ color: compareB.changes.stage_delta > 0 ? "var(--over-exploited)" : compareB.changes.stage_delta < 0 ? "var(--safe)" : "var(--text-secondary)" }}>
                    {compareB.changes.stage_delta > 0 ? "+" : ""}{compareB.changes.stage_delta.toFixed(1)}%
                  </span>
                ) : "—"}
              </div>
            </div>
          </div>

          <div className="cmp-diff">
            <div className="ai-insight" style={{ maxWidth: 1400 }}>
              <b>Key Differences</b>
              {compareA && compareB ? (
                <p>
                  Between {yearA} and {yearB}, {stateA} shows a stage change of{" "}
                  <span style={{ color: getCategoryColor(compareA.year2_data.category) }}>
                    {compareA.changes.stage_delta > 0 ? "+" : ""}{compareA.changes.stage_delta.toFixed(1)}%
                  </span>
                  , while {stateB} shows{" "}
                  <span style={{ color: getCategoryColor(compareB.year2_data.category) }}>
                    {compareB.changes.stage_delta > 0 ? "+" : ""}{compareB.changes.stage_delta.toFixed(1)}%
                  </span>
                  .{" "}
                  {compareA.changes.blocks_deteriorated > compareB.changes.blocks_deteriorated
                    ? `${stateA} had more blocks deteriorating in category.`
                    : `${stateB} had more blocks deteriorating in category.`}
                </p>
              ) : (
                <p>Select states and years to see a detailed comparison of groundwater conditions.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
