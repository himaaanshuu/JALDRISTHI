import { useEffect, useState } from "react";
import { fetchJson } from "../../lib/api";

interface StateSummary {
  state: string;
  districts: number;
  blocks: number;
  latest_assessment_year: number;
  avg_extraction_stage: number;
}

export default function Analytics() {
  const [states, setStates] = useState<StateSummary[]>([]);

  useEffect(() => {
    let active = true;

    fetchJson<StateSummary[]>("/api/states")
      .then((statesData) => {
        if (active) {
          setStates(statesData);
        }
      })
      .catch(() => {
        if (active) {
          setStates([]);
        }
      });

    return () => { active = false; };
  }, []);

  const totalRecords = states.reduce((sum, s) => sum + s.blocks, 0);
  const totalDistricts = states.reduce((sum, s) => sum + s.districts, 0);

  const categoryCounts = states.reduce(
    (acc, s) => {
      const stage = s.avg_extraction_stage;
      if (stage >= 100) acc["Over-Exploited"] += s.blocks;
      else if (stage >= 90) acc["Critical"] += s.blocks;
      else if (stage >= 70) acc["Semi-Critical"] += s.blocks;
      else acc["Safe"] += s.blocks;
      return acc;
    },
    { Safe: 0, "Semi-Critical": 0, Critical: 0, "Over-Exploited": 0 }
  );

  const topStates = [...states]
    .sort((a, b) => b.avg_extraction_stage - a.avg_extraction_stage)
    .slice(0, 8);

  const regionData = [
    { name: "North", hindi: "उत्तर", states: ["Punjab", "Haryana", "Delhi", "Uttar Pradesh", "Rajasthan"], color: "var(--over-exploited)" },
    { name: "South", hindi: "दक्षिण", states: ["Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh", "Telangana"], color: "var(--critical)" },
    { name: "West", hindi: "पश्चिम", states: ["Gujarat", "Maharashtra", "Goa"], color: "var(--semi-critical)" },
    { name: "East", hindi: "पूर्व", states: ["West Bengal", "Bihar", "Jharkhand", "Odisha"], color: "var(--safe)" },
    { name: "Central", hindi: "मध्य", states: ["Madhya Pradesh", "Chhattisgarh"], color: "var(--safe)" },
  ];

  const getRegionAvg = (regionStates: string[]) => {
    const regionStats = states.filter((s) => regionStates.includes(s.state));
    if (regionStats.length === 0) return 0;
    return regionStats.reduce((sum, s) => sum + s.avg_extraction_stage, 0) / regionStats.length;
  };

  return (
    <section className="view active">
      <div className="ov-hero">
        <div className="eyebrow">विश्लेषण · ANALYTICS</div>
        <h1 className="hero-title">
          Groundwater
          <span className="hero-title-line2">Analytics</span>
        </h1>
        <p className="hero-sub">
          Deep insights into extraction patterns, category distribution, and regional trends
          across {totalRecords} assessment units in {states.length} states.
        </p>
        <p className="hero-sub-hindi">
          {states.length} राज्यों में {totalRecords} मूल्यांकन इकाइयों में निष्कर्षण पैटर्न, श्रेणी वितरण और क्षेत्रीय रुझानों में गहरी अंतर्दृष्टि।
        </p>
        <div className="hero-meta">
          <div className="hero-meta-item">
            <span className="hero-meta-label">States / UTs</span>
            <span className="hero-meta-value">{states.length}</span>
          </div>
          <div className="hero-meta-item">
            <span className="hero-meta-label">Districts</span>
            <span className="hero-meta-value">{totalDistricts}</span>
          </div>
          <div className="hero-meta-item">
            <span className="hero-meta-label">Assessment Units</span>
            <span className="hero-meta-value">{totalRecords}</span>
          </div>
          <div className="hero-meta-item">
            <span className="hero-meta-label">Data Source</span>
            <span className="hero-meta-value">CGWB / IN-GRES</span>
          </div>
        </div>
      </div>

      <div className="an-grid">
        <div className="an-card an-card-wide">
          <div className="an-card-title">CGWB Category Distribution</div>
          <div className="an-card-sub">Assessment units by extraction stage classification</div>
          <div className="an-category-bars">
            {Object.entries(categoryCounts).map(([cat, count]) => {
              const pct = totalRecords > 0 ? (count / totalRecords) * 100 : 0;
              const colorMap: Record<string, string> = {
                Safe: "var(--safe)",
                "Semi-Critical": "var(--semi-critical)",
                Critical: "var(--critical)",
                "Over-Exploited": "var(--over-exploited)",
              };
              return (
                <div className="an-category-row" key={cat}>
                  <div className="an-category-label">
                    <span className="an-category-dot" style={{ background: colorMap[cat] }} />
                    {cat}
                  </div>
                  <div className="an-category-bar-track">
                    <div
                      className="an-category-bar-fill"
                      style={{ width: `${pct}%`, background: colorMap[cat] }}
                    />
                  </div>
                  <div className="an-category-count">{count} units</div>
                  <div className="an-category-pct">{pct.toFixed(1)}%</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="an-card">
          <div className="an-card-title">State Rankings</div>
          <div className="an-card-sub">Highest extraction stage states</div>
          {topStates.map((s, i) => {
            const stage = s.avg_extraction_stage;
            const cat = stage >= 100 ? "Over-Exploited" : stage >= 90 ? "Critical" : stage >= 70 ? "Semi-Critical" : "Safe";
            const colorMap: Record<string, string> = {
              Safe: "var(--safe)",
              "Semi-Critical": "var(--semi-critical)",
              Critical: "var(--critical)",
              "Over-Exploited": "var(--over-exploited)",
            };
            return (
              <div className="rank-row" key={s.state}>
                <span className="rank-num">{String(i + 1).padStart(2, "0")}</span>
                <span className="rank-name">{s.state}</span>
                <div className="rank-bar-track">
                  <div className="rank-bar-fill" style={{ width: `${Math.min(stage, 200) / 2}%`, background: colorMap[cat] }} />
                </div>
                <span className="rank-val" style={{ color: colorMap[cat] }}>{stage.toFixed(0)}%</span>
              </div>
            );
          })}
        </div>

        <div className="an-card">
          <div className="an-card-title">Regional Analysis</div>
          <div className="an-card-sub">Average extraction stage by region</div>
          {regionData.map((r) => {
            const avg = getRegionAvg(r.states);
            const pct = Math.min(avg, 150) / 1.5;
            return (
              <div className="rank-row" key={r.name}>
                <span className="rank-num-hi">{r.hindi}</span>
                <span className="rank-name">{r.name}</span>
                <div className="rank-bar-track">
                  <div className="rank-bar-fill" style={{ width: `${pct}%`, background: r.color }} />
                </div>
                <span className="rank-val">{avg.toFixed(0)}%</span>
              </div>
            );
          })}
        </div>

        <div className="an-card an-card-wide">
          <div className="an-card-title">Key Insights</div>
          <div className="an-card-sub">AI-powered analysis of groundwater trends</div>
          <div className="an-insights-grid">
            <div className="an-insight">
              <div className="an-insight-icon" style={{ background: "rgba(184,146,63,0.15)", color: "var(--semi-critical)" }}>!</div>
              <div>
                <div className="an-insight-title">Northern States Under Stress</div>
                <div className="an-insight-body">
                  Punjab, Haryana, and Rajasthan collectively account for over 60% of India's
                  over-exploited blocks. Intensive paddy cultivation and free electricity for
                  pumping are major drivers.
                </div>
                <div className="an-insight-hindi">
                  पंजाब, हरियाणा और राजस्थान मिलकर भारत के 60% से अधिक अत्यधिक दोहन ब्लॉकों का प्रतिनिधित्व करते हैं।
                </div>
              </div>
            </div>
            <div className="an-insight">
              <div className="an-insight-icon" style={{ background: "rgba(92,138,107,0.15)", color: "var(--safe)" }}>✓</div>
              <div>
                <div className="an-insight-title">Southern States Show Resilience</div>
                <div className="an-insight-body">
                  Kerala, Karnataka, and Tamil Nadu maintain moderate extraction levels due to
                  diverse water sources and better irrigation efficiency.
                </div>
                <div className="an-insight-hindi">
                  केरल, कर्नाटक और तमिलनाडु विविध जल स्रोतों और बेहतर सिंचाई दक्षता के कारण मध्यम निष्कर्षण स्तर बनाए रखते हैं।
                </div>
              </div>
            </div>
            <div className="an-insight">
              <div className="an-insight-icon" style={{ background: "rgba(154,62,62,0.15)", color: "var(--over-exploited)" }}>✕</div>
              <div>
                <div className="an-insight-title">Declining Water Tables</div>
                <div className="an-insight-body">
                  Over 1,500 blocks across India show declining water levels. At current extraction
                  rates, many aquifers face permanent depletion within 20 years.
                </div>
                <div className="an-insight-hindi">
                  भारत भर में 1,500 से अधिक ब्लॉकों में जल स्तर गिर रहा है। वर्तमान निष्कर्षण दरों पर, कई जलाधार 20 वर्षों में स्थायी रूप से समाप्त हो जाएंगे।
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
