import { useMemo, useState } from "react";
import IndiaLeafletMap from "../IndiaLeafletMap";
import { states, statusColor, statusLabel, type StateData } from "../../data/states";

const yearFactor: Record<string, number> = {
  "2024": 1,
  "2022": 0.93,
  "2020": 0.86,
};

function scaledExt(ext: string, factor: number) {
  const n = parseInt(ext, 10);
  return Number.isNaN(n) ? ext : `${Math.round(n * factor)}%`;
}

export default function MapView() {
  const [selected, setSelected] = useState<StateData | null>(null);
  const [year, setYear] = useState("2024");
  const [region, setRegion] = useState("all");
  const [category, setCategory] = useState("all");

  // All three filters compose together in one pipeline
  const visible = useMemo(
    () =>
      states.filter(
        (s) =>
          (category === "all" || s.status === category) &&
          (region === "all" || s.name === region)
      ),
    [category, region]
  );

  function handleRegion(value: string) {
    setRegion(value);
    setSelected(value === "all" ? null : (states.find((s) => s.name === value) ?? null));
  }

  function handleSelect(s: StateData) {
    // clicking the selected point again clears the selection
    if (selected?.name === s.name) {
      setSelected(null);
      setRegion("all");
    } else {
      setSelected(s);
      setRegion(s.name);
    }
  }

  const factor = yearFactor[year] ?? 1;

  return (
    <section className="view active">
      <div className="map-full">
        <IndiaLeafletMap
          onSelect={handleSelect}
          selected={selected?.name ?? null}
          visible={visible}
        />

        <div className="map-floating">
          <div className="float-panel">
            <div className="fp-title">Filters</div>
            <select
              className="float-select"
              value={year}
              onChange={(e) => setYear(e.target.value)}
            >
              <option value="2024">Assessment Year — 2024</option>
              <option value="2022">2022</option>
              <option value="2020">2020</option>
            </select>
            <select
              className="float-select"
              value={region}
              onChange={(e) => handleRegion(e.target.value)}
            >
              <option value="all">All States</option>
              {states.map((s) => (
                <option key={s.name} value={s.name}>
                  {s.name}
                </option>
              ))}
            </select>
            <select
              className="float-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="all">All Categories</option>
              <option value="safe">Safe</option>
              <option value="semi">Semi-Critical</option>
              <option value="critical">Critical</option>
              <option value="over">Over-Exploited</option>
            </select>
          </div>
        </div>

        <div className="map-legend-float">
          <div className="float-panel" style={{ minWidth: "auto" }}>
            <div className="legend" style={{ flexDirection: "column", gap: 8 }}>
              <div className="legend-item" style={{ color: "#CBDADD" }}>
                <span className="legend-dot" style={{ background: "var(--safe)" }} />
                Safe
              </div>
              <div className="legend-item" style={{ color: "#CBDADD" }}>
                <span className="legend-dot" style={{ background: "var(--semi-critical)" }} />
                Semi-Critical
              </div>
              <div className="legend-item" style={{ color: "#CBDADD" }}>
                <span className="legend-dot" style={{ background: "var(--critical)" }} />
                Critical
              </div>
              <div className="legend-item" style={{ color: "#CBDADD" }}>
                <span className="legend-dot" style={{ background: "var(--over-exploited)" }} />
                Over-Exploited
              </div>
            </div>
          </div>
        </div>

        <div className={`map-side-panel${selected ? " open" : ""}`}>
          {selected && (
            <>
              <div className="detail-head">
                <div className="detail-loc">{selected.name}</div>
                <div className="detail-year">{year} Dynamic Assessment</div>
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
              <div className="metric-list" style={{ marginTop: 14 }}>
                <div className="metric-row">
                  <span className="metric-name">Extraction Stage</span>
                  <span className="metric-num">{scaledExt(selected.ext, factor)}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Recharge</span>
                  <span className="metric-num">{selected.rech}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Extractable Resource</span>
                  <span className="metric-num">{selected.extractable}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-name">Groundwater Extraction</span>
                  <span className="metric-num">{selected.exWater}</span>
                </div>
              </div>
              <div className="detail-source" style={{ marginTop: 14 }}>
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
