export default function AIAssistant() {
  return (
    <section className="view active">
      <div className="assist-shell">
        <div className="assist-col">
          <div className="assist-col-pad">
            <div className="col-title">Recent Topics</div>
            <div className="topic-item active">
              Haryana extraction trend
              <span className="t-date">Today, 11:42</span>
            </div>
            <div className="topic-item">
              Over-exploited districts, TN
              <span className="t-date">Yesterday</span>
            </div>
            <div className="topic-item">
              Delhi NCR stress zones
              <span className="t-date">2 days ago</span>
            </div>
            <div className="topic-item">
              Punjab recharge deficit
              <span className="t-date">4 days ago</span>
            </div>
            <div className="col-title" style={{ marginTop: 18 }}>
              Saved Queries
            </div>
            <div className="topic-item">Monsoon recharge correlation</div>
          </div>
        </div>

        <div className="assist-center">
          <div className="assist-thread">
            <div className="msg msg-user">
              <div className="bubble">
                Compare groundwater extraction in Haryana between 2020 and 2024.
              </div>
            </div>

            <div className="msg msg-ai">
              <div className="ai-tag">
                <span className="dot-live" />
                <span>जलदृष्टि DRISTI</span>
              </div>
              <div className="ai-card">
                <div className="ai-card-body">
                  Haryana&apos;s groundwater extraction rose over the assessment period,
                  deepening its over-exploited status statewide.
                </div>
                <div className="ai-metric-pair">
                  <div className="ai-metric">
                    <div className="yr">2020</div>
                    <div className="val mono">13.42 BCM</div>
                  </div>
                  <div className="ai-metric">
                    <div className="yr">2024</div>
                    <div className="val mono" style={{ color: "var(--over-exploited)" }}>
                      14.87 BCM
                    </div>
                  </div>
                </div>
                <svg viewBox="0 0 300 70" width="100%" height="70" style={{ display: "block" }}>
                  <polyline
                    points="0,50 60,44 120,38 180,30 240,20 300,10"
                    fill="none"
                    stroke="var(--water-blue)"
                    strokeWidth={2}
                  />
                  <circle cx="300" cy="10" r="3" fill="var(--over-exploited)" />
                </svg>
                <div className="ai-insight">
                  <b>Key Insight</b>
                  <p>
                    Extraction growth is concentrated in Karnal, Kaithal and Kurukshetra,
                    where paddy-dominant cropping keeps demand well above natural recharge.
                  </p>
                </div>
                <div className="ai-followups">
                  <span className="chip" style={{ color: "var(--water-blue)", borderColor: "var(--water-blue)" }}>
                    Show district breakdown
                  </span>
                  <span className="chip" style={{ color: "var(--water-blue)", borderColor: "var(--water-blue)" }}>
                    View on map
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="assist-inputbar">
            <div className="assist-input">
              <input type="text" placeholder="Ask a follow-up about groundwater…" />
              <button aria-label="Send">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path d="M5 12h14M13 6l6 6-6 6" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div className="assist-col">
          <div className="assist-col-pad">
            <div className="col-title">Evidence</div>
            <div className="evidence-block">
              <div className="e-row">
                <span>Source</span>
                <span>CGWB / IN-GRES</span>
              </div>
              <div className="e-row">
                <span>Assessment Year</span>
                <span>2024</span>
              </div>
              <div className="e-row">
                <span>Location</span>
                <span>Haryana</span>
              </div>
              <div className="e-row">
                <span>Confidence</span>
                <span>94%</span>
              </div>
              <div className="conf-bar">
                <div className="conf-fill" style={{ width: "94%" }} />
              </div>
            </div>
            <div className="col-title" style={{ marginTop: 16 }}>
              Related Units
            </div>
            <div className="evidence-block">
              <div className="e-row">
                <span>Karnal</span>
                <span style={{ color: "var(--over-exploited)" }}>Over-Exploited</span>
              </div>
            </div>
            <div className="evidence-block">
              <div className="e-row">
                <span>Kaithal</span>
                <span style={{ color: "var(--over-exploited)" }}>Over-Exploited</span>
              </div>
            </div>
            <div className="evidence-block">
              <div className="e-row">
                <span>Panchkula</span>
                <span style={{ color: "var(--safe)" }}>Safe</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
