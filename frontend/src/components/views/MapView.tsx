import { useState } from "react";
import IndiaMap from "../IndiaMap";
import { statusColor, statusLabel, type StateData } from "../../data/states";

export default function MapView() {
  const [selected, setSelected] = useState<StateData | null>(null);

  return (
    <section className="view active">
      <div className="map-full">
        <IndiaMap dark onSelect={setSelected} selected={selected?.name ?? null} />

        <div className="map-floating">
          <div className="float-panel">
            <div className="fp-title">Filters</div>
            <select className="float-select" defaultValue="2024">
              <option value="2024">Assessment Year — 2024</option>
              <option value="2022">2022</option>
              <option value="2020">2020</option>
            </select>
            <select className="float-select" defaultValue="all">
              <option value="all">All States</option>
              <option value="haryana">Haryana</option>
              <option value="punjab">Punjab</option>
              <option value="tn">Tamil Nadu</option>
            </select>
            <select className="float-select" defaultValue="all">
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
              <div className="metric-list" style={{ marginTop: 14 }}>
                <div className="metric-row">
                  <span className="metric-name">Extraction Stage</span>
                  <span className="metric-num">{selected.ext}</span>
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
