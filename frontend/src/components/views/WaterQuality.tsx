import { useState, useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface QualityRecord {
  id: number;
  state: string;
  district: string;
  block: string;
  assessment_year: number;
  fluoride_mg_l: number | null;
  arsenic_ug_l: number | null;
  nitrate_mg_l: number | null;
  iron_mg_l: number | null;
  tds_mg_l: number | null;
  ec_umho_cm: number | null;
  ph: number | null;
  chloride_mg_l: number | null;
  sulphate_mg_l: number | null;
  hardness_mg_l: number | null;
  uranium_ug_l: number | null;
  latitude: number | null;
  longitude: number | null;
}

interface StateQualityResponse {
  state: string;
  total_samples: number;
  district_summary: {
    district: string;
    samples: number;
    safe_count: number;
    moderate_count: number;
    unsuitable_count: number;
    exceeded_parameters: string[];
  }[];
  records: QualityRecord[];
}

const STATUS_COLORS: Record<string, string> = {
  safe: "#4da8ff",
  moderate: "#f0b34f",
  exceeded: "#b53e3e",
  unknown: "#6b7b8d",
};

export default function WaterQuality() {
  const [standards, setStandards] = useState<Record<string, { max: number; param: string }>>({});
  const [states, setStates] = useState<string[]>([]);
  const [selectedState, setSelectedState] = useState<string>("");
  const [qualityData, setQualityData] = useState<StateQualityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedDistrict, setExpandedDistrict] = useState<string | null>(null);

  useEffect(() => {
    loadStandards();
    loadStates();
  }, []);

  useEffect(() => {
    if (selectedState) loadQualityData(selectedState);
  }, [selectedState]);

  const loadStandards = async () => {
    try {
      const resp = await fetch(`${API_URL}/api/water-quality/standards`);
      if (resp.ok) {
        const data = await resp.json();
        setStandards(data.standards || {});
      }
    } catch {
      // Use fallback standards
      setStandards({
        ph: { max: 8.5, param: "pH" },
        tds_mg_l: { max: 500, param: "TDS" },
        fluoride_mg_l: { max: 1.0, param: "Fluoride" },
        arsenic_ug_l: { max: 10, param: "Arsenic" },
        nitrate_mg_l: { max: 45, param: "Nitrate" },
        iron_mg_l: { max: 0.3, param: "Iron" },
      });
    }
  };

  const loadStates = async () => {
    try {
      const resp = await fetch(`${API_URL}/api/groundwater/states`);
      if (resp.ok) {
        const data = await resp.json();
        setStates(data.states || []);
      }
    } catch {
      // Fallback states
      setStates(["Gujarat", "Maharashtra", "Rajasthan", "Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Karnataka", "Tamil Nadu", "Andhra Pradesh"]);
    }
  };

  const loadQualityData = async (state: string) => {
    setLoading(true);
    setError("");
    try {
      const resp = await fetch(`${API_URL}/api/water-quality/state/${encodeURIComponent(state)}`);
      if (resp.ok) {
        const data = await resp.json();
        setQualityData(data);
      } else if (resp.status === 404) {
        setQualityData(null);
        setError(`No water quality data available for ${state}`);
      } else {
        setError("Failed to load quality data");
      }
    } catch {
      setError("Failed to connect to server");
    }
    setLoading(false);
  };

  const overallStatus = (district: { safe_count: number; moderate_count: number; unsuitable_count: number; samples: number }) => {
    if (district.unsuitable_count > 0) return "exceeded";
    if (district.moderate_count > 0) return "moderate";
    return "safe";
  };

  return (
    <div className="wq-page">
      <header className="wq-header">
        <div>
          <h1 className="wq-title">Water Quality Intelligence</h1>
          <p className="wq-subtitle">BIS/CGWB Drinking Water Quality Assessment</p>
        </div>
        <div className="wq-controls">
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="wq-select"
          >
            <option value="">Select State</option>
            {states.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </header>

      {loading && <div className="wq-loading">Loading water quality data...</div>}
      {error && <div className="wq-error">{error}</div>}

      {!loading && !error && !selectedState && (
        <div className="wq-empty">
          <div className="wq-empty-icon">
            <svg viewBox="0 0 48 48" fill="none" width="64" height="64">
              <path d="M24 4C24 4 8 18 8 26C8 34 15 42 24 42C33 42 40 34 40 26C40 18 24 4 24 4Z" fill="#1a5276" opacity="0.2" />
              <path d="M18 24c2-4 4-6 6-6s4 2 6 6" stroke="#1a5276" strokeWidth="2" fill="none" />
            </svg>
          </div>
          <h2>Select a State to Begin</h2>
          <p>Water quality data is collected from CGWB monitoring stations across India.</p>
          <div className="wq-standards-preview">
            <h3>BIS Drinking Water Standards (IS 10500:2012)</h3>
            <div className="wq-standards-grid">
              {Object.entries(standards).slice(0, 6).map(([key, std]) => (
                <div key={key} className="wq-standard-card">
                  <span className="wq-std-name">{std.param}</span>
                  <span className="wq-std-limit">≤ {std.max} {key.includes("ug") ? "μg/L" : key.includes("ec") ? "μS/cm" : "mg/L"}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {!loading && !error && qualityData && (
        <div className="wq-results">
          <div className="wq-summary">
            <h2>{qualityData.state}</h2>
            <div className="wq-summary-stats">
              <div className="wq-stat">
                <span className="wq-stat-value">{qualityData.total_samples}</span>
                <span className="wq-stat-label">Total Samples</span>
              </div>
              <div className="wq-stat">
                <span className="wq-stat-value" style={{ color: STATUS_COLORS.safe }}>
                  {qualityData.district_summary.reduce((s, d) => s + d.safe_count, 0)}
                </span>
                <span className="wq-stat-label">Safe</span>
              </div>
              <div className="wq-stat">
                <span className="wq-stat-value" style={{ color: STATUS_COLORS.moderate }}>
                  {qualityData.district_summary.reduce((s, d) => s + d.moderate_count, 0)}
                </span>
                <span className="wq-stat-label">Moderate</span>
              </div>
              <div className="wq-stat">
                <span className="wq-stat-value" style={{ color: STATUS_COLORS.exceeded }}>
                  {qualityData.district_summary.reduce((s, d) => s + d.unsuitable_count, 0)}
                </span>
                <span className="wq-stat-label">Exceeded</span>
              </div>
            </div>
          </div>

          <div className="wq-districts">
            <h3>District Breakdown</h3>
            {qualityData.district_summary.map((dist) => (
              <div key={dist.district} className="wq-district-card">
                <div
                  className="wq-district-header"
                  onClick={() => setExpandedDistrict(expandedDistrict === dist.district ? null : dist.district)}
                >
                  <div className="wq-district-info">
                    <span className="wq-district-name">{dist.district}</span>
                    <span className="wq-district-samples">{dist.samples} samples</span>
                  </div>
                  <div className="wq-district-status">
                    <span
                      className="wq-status-badge"
                      style={{ background: STATUS_COLORS[overallStatus(dist)] }}
                    >
                      {overallStatus(dist) === "safe" ? "Safe" : overallStatus(dist) === "moderate" ? "Moderate" : "Exceeded"}
                    </span>
                    {dist.exceeded_parameters.length > 0 && (
                      <span className="wq-exceeded-params">
                        {dist.exceeded_parameters.join(", ")}
                      </span>
                    )}
                  </div>
                </div>

                {expandedDistrict === dist.district && (
                  <div className="wq-district-detail">
                    <div className="wq-sample-bars">
                      <div className="wq-bar-row">
                        <span className="wq-bar-label">Safe</span>
                        <div className="wq-bar-track">
                          <div
                            className="wq-bar-fill"
                            style={{
                              width: `${(dist.safe_count / dist.samples) * 100}%`,
                              background: STATUS_COLORS.safe,
                            }}
                          />
                        </div>
                        <span className="wq-bar-count">{dist.safe_count}</span>
                      </div>
                      <div className="wq-bar-row">
                        <span className="wq-bar-label">Moderate</span>
                        <div className="wq-bar-track">
                          <div
                            className="wq-bar-fill"
                            style={{
                              width: `${(dist.moderate_count / dist.samples) * 100}%`,
                              background: STATUS_COLORS.moderate,
                            }}
                          />
                        </div>
                        <span className="wq-bar-count">{dist.moderate_count}</span>
                      </div>
                      <div className="wq-bar-row">
                        <span className="wq-bar-label">Exceeded</span>
                        <div className="wq-bar-track">
                          <div
                            className="wq-bar-fill"
                            style={{
                              width: `${(dist.unsuitable_count / dist.samples) * 100}%`,
                              background: STATUS_COLORS.exceeded,
                            }}
                          />
                        </div>
                        <span className="wq-bar-count">{dist.unsuitable_count}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
