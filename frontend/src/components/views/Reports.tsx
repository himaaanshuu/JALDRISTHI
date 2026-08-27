import { useEffect, useState } from "react";
import { fetchJson } from "../../lib/api";

interface StateSummary {
  state: string;
  districts: number;
  blocks: number;
  latest_assessment_year: number;
  avg_extraction_stage: number;
}

const reportSections = [
  { id: "executive", label: "Executive Summary", hindi: "कार्यकारी सारांश", defaultChecked: true },
  { id: "status", label: "Groundwater Status", hindi: "भूजल स्थिति", defaultChecked: true },
  { id: "classification", label: "CGWB Classification", hindi: "CGWB वर्गीकरण", defaultChecked: true },
  { id: "historical", label: "Historical Analysis", hindi: "ऐतिहासिक विश्लेषण", defaultChecked: true },
  { id: "critical", label: "Critical Areas", hindi: "गंभीर क्षेत्र", defaultChecked: true },
  { id: "recommendations", label: "Recommendations", hindi: "सिफारिशें", defaultChecked: false },
  { id: "data-sources", label: "Data Sources", hindi: "डेटा स्रोत", defaultChecked: true },
];

export default function Reports() {
  const [states, setStates] = useState<StateSummary[]>([]);
  const [selectedState, setSelectedState] = useState("Haryana");
  const [selectedSections, setSelectedSections] = useState<string[]>(
    reportSections.filter((s) => s.defaultChecked).map((s) => s.id)
  );

  useEffect(() => {
    fetchJson<StateSummary[]>("/api/states")
      .then(setStates)
      .catch(() => {});
  }, []);

  const toggleSection = (id: string) => {
    setSelectedSections((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const stateData = states.find((s) => s.state === selectedState);
  const stage = stateData?.avg_extraction_stage ?? 0;
  const category = stage >= 100 ? "Over-Exploited" : stage >= 90 ? "Critical" : stage >= 70 ? "Semi-Critical" : "Safe";

  return (
    <section className="view active">
      <div className="ov-hero">
        <div className="eyebrow">रिपोर्ट्स · REPORTS</div>
        <h1 className="hero-title">
          Intelligence
          <span className="hero-title-line2">Reports</span>
        </h1>
        <p className="hero-sub">
          Generate comprehensive groundwater intelligence reports from official CGWB/IN-GRES
          assessment data with AI-powered insights.
        </p>
        <p className="hero-sub-hindi">
          आधिकारिक CGWB/IN-GRES मूल्यांकन डेटा से व्यापक भूजल बुद्धिमत्ता रिपोर्ट बनाएं।
        </p>
      </div>

      <div className="rep-shell">
        <div className="rep-side">
          <div className="col-title">Report Configuration</div>

          <div className="rep-config-group">
            <label className="rep-config-label">Select State</label>
            <select
              className="rep-state-select"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
            >
              {states.map((s) => (
                <option key={s.state} value={s.state}>
                  {s.state} ({s.blocks} blocks)
                </option>
              ))}
            </select>
          </div>

          <div className="rep-config-group">
            <label className="rep-config-label">Include Sections</label>
            {reportSections.map((s) => (
              <label className="rep-check" key={s.id}>
                <input
                  type="checkbox"
                  checked={selectedSections.includes(s.id)}
                  onChange={() => toggleSection(s.id)}
                />
                <div>
                  <span>{s.label}</span>
                  <span className="rep-check-hindi">{s.hindi}</span>
                </div>
              </label>
            ))}
          </div>

          <div className="rep-actions">
            <button className="btn btn-primary">Generate Report</button>
            <button className="btn btn-ghost">Export PDF</button>
          </div>
        </div>

        <div className="rep-preview">
          <div className="rep-preview-header">
            <h2>Groundwater Intelligence Report</h2>
            <div className="rp-meta">
              <span>{selectedState}</span> · Assessment Year {stateData?.latest_assessment_year ?? 2024} · CGWB / IN-GRES
            </div>
          </div>

          {selectedSections.includes("executive") && (
            <div className="rep-sec">
              <h4>Executive Summary</h4>
              <p>
                {selectedState}&apos;s groundwater extraction stage stands at{" "}
                <strong style={{ color: category === "Safe" ? "var(--safe)" : category === "Semi-Critical" ? "var(--semi-critical)" : category === "Critical" ? "var(--critical)" : "var(--over-exploited)" }}>
                  {stage.toFixed(1)}%
                </strong>
                , placing it in the <strong>{category}</strong> category. With {stateData?.districts ?? 0} districts
                and {stateData?.blocks ?? 0} assessment units, the state faces{" "}
                {stage >= 100 ? "severe groundwater stress requiring immediate intervention" :
                 stage >= 90 ? "critical conditions requiring urgent regulatory measures" :
                 stage >= 70 ? "approaching sustainable limits with growing extraction pressure" :
                 "manageable extraction levels with sustainable practices"}
                .
              </p>
            </div>
          )}

          {selectedSections.includes("status") && (
            <div className="rep-sec">
              <h4>Groundwater Status</h4>
              <p>
                Current extraction stage: <strong>{stage.toFixed(1)}%</strong>.
                {stage >= 100
                  ? " More groundwater is being extracted than naturally replenished, leading to continuous water table decline."
                  : stage >= 90
                  ? " Extraction is approaching the limit of sustainable use, with seasonal stress becoming more common."
                  : stage >= 70
                  ? " Extraction is within sustainable limits but shows increasing pressure from agricultural and industrial demand."
                  : " Groundwater extraction remains within sustainable limits with stable water tables."}
              </p>
            </div>
          )}

          {selectedSections.includes("classification") && (
            <div className="rep-sec">
              <h4>CGWB Classification</h4>
              <div className="rep-classification-grid">
                <div className="rep-class-item">
                  <span className="rep-class-label">Category</span>
                  <span className="rep-class-value" style={{ color: category === "Safe" ? "var(--safe)" : category === "Semi-Critical" ? "var(--semi-critical)" : category === "Critical" ? "var(--critical)" : "var(--over-exploited)" }}>
                    {category}
                  </span>
                </div>
                <div className="rep-class-item">
                  <span className="rep-class-label">Extraction Stage</span>
                  <span className="rep-class-value">{stage.toFixed(1)}%</span>
                </div>
                <div className="rep-class-item">
                  <span className="rep-class-label">Assessment Units</span>
                  <span className="rep-class-value">{stateData?.blocks ?? 0}</span>
                </div>
                <div className="rep-class-item">
                  <span className="rep-class-label">Districts</span>
                  <span className="rep-class-value">{stateData?.districts ?? 0}</span>
                </div>
              </div>
              <p>
                According to CGWB guidelines, {selectedState} is classified as <strong>{category}</strong> based on an
                extraction stage of {stage.toFixed(1)}%.{" "}
                {category === "Safe"
                  ? "This indicates sustainable groundwater use with stable water tables."
                  : category === "Semi-Critical"
                  ? "Regulatory measures are recommended to prevent further deterioration."
                  : category === "Critical"
                  ? "Urgent intervention is required to prevent permanent aquifer damage."
                  : "Emergency measures are needed to address severe groundwater depletion."}
              </p>
            </div>
          )}

          {selectedSections.includes("historical") && (
            <div className="rep-sec">
              <h4>Historical Analysis</h4>
              <p>
                {selectedState}&apos;s groundwater extraction has{" "}
                {stage > 100 ? "significantly exceeded" : stage > 70 ? "been approaching" : "remained within"}
                {" "}sustainable limits. The assessment data across available years shows{" "}
                {stage >= 100
                  ? "a concerning upward trend in extraction rates."
                  : "relatively stable conditions with manageable fluctuations."}
              </p>
            </div>
          )}

          {selectedSections.includes("critical") && (
            <div className="rep-sec">
              <h4>Critical Areas</h4>
              <p>
                {stage >= 100
                  ? `Multiple blocks across ${selectedState} show extraction stages exceeding 100%, indicating areas where groundwater is being depleted faster than it can be naturally replenished.`
                  : stage >= 70
                  ? `Several blocks in ${selectedState} are approaching critical extraction levels. Monitoring and early intervention are recommended.`
                  : `${selectedState} currently has no blocks in critical or over-exploited categories, but continued monitoring is essential.`}
              </p>
            </div>
          )}

          {selectedSections.includes("recommendations") && (
            <div className="rep-sec">
              <h4>Recommendations</h4>
              <ul className="rep-recommendations">
                {stage >= 100 && (
                  <>
                    <li>Implement emergency groundwater extraction regulations</li>
                    <li>Enforce water pricing and metering for commercial users</li>
                    <li>Promote alternative water sources and rainwater harvesting</li>
                    <li>Establish groundwater monitoring networks in critical blocks</li>
                  </>
                )}
                {stage >= 70 && stage < 100 && (
                  <>
                    <li>Regulate new well drilling in semi-critical areas</li>
                    <li>Promote water-efficient irrigation technologies</li>
                    <li>Implement managed aquifer recharge programs</li>
                    <li>Establish community-based groundwater management committees</li>
                  </>
                )}
                {stage < 70 && (
                  <>
                    <li>Maintain current sustainable extraction practices</li>
                    <li>Continue monitoring and data collection</li>
                    <li>Implement preventive measures to maintain safe levels</li>
                    <li>Promote water conservation awareness programs</li>
                  </>
                )}
              </ul>
            </div>
          )}

          {selectedSections.includes("data-sources") && (
            <div className="rep-sec">
              <h4>Data Sources</h4>
              <p>
                This report is generated from official data sources including:
              </p>
              <ul className="rep-sources">
                <li>Central Ground Water Board (CGWB) — Ground Water Year Books</li>
                <li>IN-GRES (India Ground Resource Estimation System)</li>
                <li>OpenCity.in CKAN Datastore API</li>
                <li>जलDRISTHI INGRES AI Assessment Database</li>
              </ul>
            </div>
          )}

          <div className="rep-footer">
            <span>Generated by जल DRISTHI INGRES AI Platform</span>
            <span>{new Date().toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" })}</span>
          </div>
        </div>
      </div>
    </section>
  );
}
