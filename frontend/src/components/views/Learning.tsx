const groundwaterTerms = [
  {
    term: "Groundwater Recharge",
    hindi: "भूजल पुनर्भरण",
    definition:
      "The process by which water moves from the surface downward through soil and rock to refill underground aquifers.",
    hindiDef:
      "वह प्रक्रिया जिसमें पानी सतह से मिट्टी और चट्टान के नीचे जाकर भूजल जलाधारों को भरता है।",
    importance:
      "India receives about 4,000 BCM of annual rainfall, but only ~214 BCM recharges groundwater. This is the primary source of replenishment for aquifers.",
    hindiImp:
      "भारत को लगभग 4,000 BCM वार्षिक वर्षा प्राप्त होती है, लेकिन केवल ~214 BCM भूजल को पुनर्भरित करती है।",
    example:
      "In Punjab, monsoon rainfall contributes ~70% of annual recharge. States like Rajasthan receive less rainfall, making artificial recharge critical.",
    hindiEx:
      "पंजाब में, मानसून की वर्षा वार्षिक पुनर्भरण का ~70% योगदान देती है। राजस्थान जैसे राज्यों में कम वर्षा होती है।",
    color: "var(--water-blue)",
  },
  {
    term: "Extraction Stage",
    hindi: "निष्कर्षण चरण",
    definition:
      "The ratio of total groundwater extraction to the net availability of groundwater, expressed as a percentage.",
    hindiDef:
      "कुल भूजल निष्कर्षण का भूजल की शुद्ध उपलब्धता के अनुपात को प्रतिशत के रूप में व्यक्त किया जाता है।",
    importance:
      "An extraction stage above 100% means more water is being pumped than naturally replenished — a direct indicator of unsustainable use.",
    hindiImp:
      "100% से अधिक निष्कर्षण चरण का अर्थ है कि प्राकृतिक रूप से पुनर्भरित होने से अधिक पानी निकाला जा रहा है।",
    example:
      "Haryana's extraction stage is ~130%, meaning it extracts 30% more than what is naturally available. This has caused water tables to drop by 1-2 meters per year in many districts.",
    hindiEx:
      "हरियाणा का निष्कर्षण चरण ~130% है, जिसका अर्थ है कि वह प्राकृतिक रूप से उपलब्ध से 30% अधिक निकालता है।",
    color: "var(--semi-critical)",
  },
  {
    term: "Safe Category",
    hindi: "सुरक्षित श्रेणी",
    definition:
      "Areas where groundwater extraction is within 70% of annual recharge, indicating sustainable use.",
    hindiDef:
      "वे क्षेत्र जहाँ भूजल निष्कर्षण वार्षिक पुनर्भरण के 70% के भीतर है, जो टिकाऊ उपयोग का संकेत देता है।",
    importance:
      "Safe areas have stable or rising water tables and can sustain current extraction patterns for decades.",
    hindiImp:
      "सुरक्षित क्षेत्रों में स्थिर या बढ़ता जल स्तर होता है और वे दशकों तक वर्तमान निष्कर्षण पैटर्न को बनाए रख सकते हैं।",
    example:
      "States like Kerala, Uttarakhand, and northeastern states fall mostly in the Safe category due to adequate rainfall and lower extraction pressure.",
    hindiEx:
      "केरल, उत्तराखंड और पूर्वोत्तर राज्य पर्याप्त वर्षा और कम निष्कर्षण दबाव के कारण मुख्य रूप से सुरक्षित श्रेणी में आते हैं।",
    color: "var(--safe)",
  },
  {
    term: "Over-Exploited",
    hindi: "अत्यधिक दोहन",
    definition:
      "Areas where extraction exceeds 100% of available groundwater, leading to continuous water table decline.",
    hindiDef:
      "वे क्षेत्र जहाँ निष्कर्षण उपलब्ध भूजल के 100% से अधिक है, जिससे जल स्तर में लगातार गिरावट होती है।",
    importance:
      "Over-exploited regions face serious water security threats, including drying wells, land subsidence, and saltwater intrusion in coastal areas.",
    hindiImp:
      "अत्यधिक दोहन वाले क्षेत्र गंभीर जल सुरक्षा खतरों का सामना करते हैं, जिसमें सूखे कुएं, भूमि धंसना और तटीय क्षेत्रों में खारे पानी का घुसना शामिल है।",
    example:
      "Punjab and Haryana have over 60% of blocks classified as Over-Exploited. Karnal district extracts nearly 196% of its available groundwater.",
    hindiEx:
      "पंजाब और हरियाणा में 60% से अधिक ब्लॉक अत्यधिक दोहन श्रेणी में हैं। करनाल जिला लगभग 196% भूजल निकालता है।",
    color: "var(--over-exploited)",
  },
  {
    term: "Annual Groundwater Recharge",
    hindi: "वार्षिक भूजल पुनर्भरण",
    definition:
      "Total volume of water replenishing aquifers annually from all sources including rainfall, surface water, and irrigation return flow.",
    hindiDef:
      "वर्षा, सतही जल और सिंचाई वापसी प्रवाह सहित सभी स्रोतों से वार्षिक रूप से जलाधारों को पुनर्भरित करने वाले पानी का कुल मात्रा।",
    importance:
      "India's total annual recharge is approximately 432 BCM, with monsoon season contributing the largest share.",
    hindiImp:
      "भारत का कुल वार्षिक पुनर्भरण लगभग 432 BCM है, जिसमें मानसून का मौसम सबसे बड़ा योगदान देता है।",
    example:
      "States like Uttar Pradesh receive ~60 BCM of annual recharge, while Rajasthan receives only ~18 BCM despite its large size.",
    hindiEx:
      "उत्तर प्रदेश को ~60 BCM वार्षिक पुनर्भरण प्राप्त होता है, जबकि राजस्थान को केवल ~18 BCM प्राप्त होता है।",
    color: "var(--muted-aqua)",
  },
  {
    term: "Extractable Groundwater Resource",
    hindi: "निकालने योग्य भूजल संसाधन",
    definition:
      "The portion of total groundwater that can be economically and technically extracted for beneficial use.",
    hindiDef:
      "कुल भूजल का वह हिस्सा जिसे आर्थिक और तकनीकी रूप से उपयोगी उपयोग के लिए निकाला जा सकता है।",
    importance:
      "This is typically 85% of total recharge, accounting for environmental flows and technical limitations.",
    hindiImp:
      "यह आमतौर पर कुल पुनर्भरण का 85% है, जो पर्यावरणीय प्रवाह और तकनीकी सीमाओं को ध्यान में रखता है।",
    example:
      "India's extractable resource is approximately 398 BCM, but actual extraction has reached ~245 BCM — over 60% of the total.",
    hindiEx:
      "भारत का निकालने योग्य संसाधन लगभग 398 BCM है, लेकिन वास्तविक निष्कर्षण ~245 BCM तक पहुंच गया है।",
    color: "var(--water-blue)",
  },
];

const measurementUnits = [
  {
    unit: "BCM",
    hindi: "बिलियन क्यूबिक मीटर",
    full: "Billion Cubic Meters",
    value: "1 BCM = 10^9 m³",
    usage: "Used for national and large-scale assessments",
    hindiUsage: "राष्ट्रीय और बड़े पैमाने के आकलन के लिए उपयोग",
    example: "India's total annual recharge ~432 BCM",
  },
  {
    unit: "MCM",
    hindi: "मिलियन क्यूबिक मीटर",
    full: "Million Cubic Meters",
    value: "1 MCM = 10^6 m³ = 1 bcm",
    usage: "Used for state and district-level data",
    hindiUsage: "राज्य और जिला स्तर के डेटा के लिए उपयोग",
    example: "Punjab's annual recharge ~18,000 MCM",
  },
  {
    unit: "ham",
    hindi: "हेक्टेयर मीटर",
    full: "Hectare Meters",
    value: "1 ham = 10,000 m³ = 0.01 MCM",
    usage: "Used for block and local-level assessments",
    hindiUsage: "ब्लॉक और स्थानीय स्तर के आकलन के लिए उपयोग",
    example: "A block with 500 ham recharge capacity",
  },
  {
    unit: "m³",
    hindi: "क्यूबिक मीटर",
    full: "Cubic Meters",
    value: "1 m³ = 1,000 litres",
    usage: "Base unit for all water volume measurements",
    hindiUsage: "सभी जल मात्रा मापन की आधार इकाई",
    example: "One family uses ~200 m³ per year",
  },
  {
    unit: "%",
    hindi: "प्रतिशत",
    full: "Percentage (of extraction stage)",
    value: "Extraction / Available × 100",
    usage: "Indicates sustainability of groundwater use",
    hindiUsage: "भूजल उपयोग की स्थिरता का संकेत",
    example: "Stage of extraction 75% = Safe",
  },
];

const keyStats = [
  { label: "India's Annual Recharge", hindi: "भारत का वार्षिक पुनर्भरण", value: "~432 BCM", sub: "Billion Cubic Meters" },
  { label: "Extractable Resource", hindi: "निकालने योग्य संसाधन", value: "~398 BCM", sub: "85% of total recharge" },
  { label: "Current Extraction", hindi: "वर्तमान निष्कर्षण", value: "~245 BCM", sub: "61% of extractable" },
  { label: "Over-Exploited Blocks", hindi: "अत्यधिक दोहन ब्लॉक", value: "~1,500+", sub: "Across northern states" },
  { label: "Irrigation Share", hindi: "सिंचाई हिस्सा", value: "~63%", sub: "Of total groundwater use" },
  { label: "Domestic Use", hindi: "घरेलू उपयोग", value: "~18%", sub: "Drinking & household" },
];

const aquiferBasics = [
  {
    title: "What is an Aquifer?",
    hindi: "जलाधार क्या है?",
    body: "An aquifer is a body of saturated rock or soil through which water can move freely. Think of it as an underground sponge that holds water. India has two main types — unconfined (shallow, directly recharged by rain) and confined (deep, trapped between rock layers).",
    hindiBody: "जलाधार संतृप्त चट्टान या मिट्टी का एक शरीर है जिसके माध्यम से पानी स्वतंत्र रूप से बह सकता है। भारत में दो मुख्य प्रकार हैं — असंयम (उथला, वर्षा से सीधा पुनर्भरण) और संयम (गहरा, चट्टान की परतों के बीच फंसा हुआ)।",
  },
  {
    title: "Water Table",
    hindi: "जल स्तर",
    body: "The water table is the upper surface of the zone of saturation. When you dig a well and hit water, you've reached the water table. In over-exploited areas of Punjab, the water table drops 1-2 meters every year.",
    hindiBody: "जल स्तर संतृप्ति क्षेत्र की ऊपरी सतह है। जब आप कुआं खोदते हैं और पानी मिलता है, तो आप जल स्तर तक पहुंच गए हैं। पंजाब के अत्यधिक दोहन वाले क्षेत्रों में जल स्तर हर साल 1-2 मीटर गिरता है।",
  },
  {
    title: "Declining Water Levels",
    hindi: "गिरता जल स्तर",
    body: "Across India, groundwater levels have been declining at alarming rates. In parts of Rajasthan, the water table has dropped over 30 meters in the last two decades. In coastal Tamil Nadu, this causes saltwater intrusion into freshwater aquifers.",
    hindiBody: "पूरे भारत में भूजल स्तर चिंताजनक दर से गिर रहा है। राजस्थान के कुछ हिस्सों में पिछले दो दशकों में जल स्तर 30 मीटर से अधिक गिर गया है। तटीय तमिलनाडु में इससे मीठे पानी के जलाधारों में खारे पानी का घुसना होता है।",
  },
];

export default function Learning() {
  return (
    <section className="view active">
      <div className="ov-hero">
        <div className="eyebrow">जलज्ञान · GROUNDWATER KNOWLEDGE</div>
        <h1 className="hero-title">Groundwater Learning Center</h1>
        <p className="hero-sub">
          Essential concepts, definitions and real-world data to understand India's groundwater situation.
          <br />
          <span className="hero-sub-hindi">भारत की भूजल स्थिति को समझने के लिए आवश्यक अवधारणाएं, परिभाषाएं और वास्तविक डेटा।</span>
        </p>
      </div>

      <div className="learn-stats-strip">
        {keyStats.map((s) => (
          <div className="learn-stat" key={s.label}>
            <div className="learn-stat-value">{s.value}</div>
            <div className="learn-stat-label">{s.label}</div>
            <div className="learn-stat-hindi">{s.hindi}</div>
            <div className="learn-stat-sub">{s.sub}</div>
          </div>
        ))}
      </div>

      <div className="learn-section">
        <div className="learn-header">
          <div className="eyebrow" style={{ marginBottom: 8 }}>मापन इकाइयाँ · MEASUREMENT UNITS</div>
          <h2 className="learn-title">Understanding Units & Formulas</h2>
          <p className="learn-sub">How groundwater is measured — from cubic meters to extraction stage percentage.</p>
        </div>
        <div className="learn-units-grid">
          {measurementUnits.map((u) => (
            <article className="learn-unit-card" key={u.unit}>
              <div className="learn-unit-head">
                <span className="learn-unit-symbol">{u.unit}</span>
                <span className="learn-unit-name">{u.full}</span>
              </div>
              <div className="learn-unit-hindi-name">{u.hindi}</div>
              <div className="learn-unit-formula">{u.value}</div>
              <div className="learn-unit-usage">{u.usage}</div>
              <div className="learn-unit-usage-hindi">{u.hindiUsage}</div>
              <div className="learn-unit-example">{u.example}</div>
            </article>
          ))}
        </div>
        <article className="learn-formula-card">
          <div className="learn-formula-title">Stage of Extraction Formula</div>
          <div className="learn-formula-hindi">निष्कर्षण चरण सूत्र</div>
          <div className="learn-formula-expr">
            Stage (%) = (Groundwater Extraction / Net Availability) × 100
          </div>
          <div className="learn-formula-expr-hindi">
            चरण (%) = (भूजल निष्कर्षण / शुद्ध उपलब्धता) × 100
          </div>
          <div className="learn-formula-ranges">
            <div className="learn-formula-range safe">
              <span className="range-label">Safe</span>
              <span className="range-val">≤ 70%</span>
              <span className="range-hindi">सुरक्षित</span>
            </div>
            <div className="learn-formula-range semi">
              <span className="range-label">Semi-Critical</span>
              <span className="range-val">70 – 90%</span>
              <span className="range-hindi">अर्ध-गंभीर</span>
            </div>
            <div className="learn-formula-range crit">
              <span className="range-label">Critical</span>
              <span className="range-val">90 – 100%</span>
              <span className="range-hindi">गंभीर</span>
            </div>
            <div className="learn-formula-range over">
              <span className="range-label">Over-Exploited</span>
              <span className="range-val">&gt; 100%</span>
              <span className="range-hindi">अत्यधिक दोहन</span>
            </div>
          </div>
        </article>
      </div>

      <div className="learn-section">
        <div className="learn-header">
          <div className="eyebrow" style={{ marginBottom: 8 }}>Core Concepts · मूल अवधारणाएँ</div>
          <h2 className="learn-title">Groundwater Fundamentals</h2>
        </div>
        <div className="learn-grid">
          {groundwaterTerms.map((item, idx) => (
            <article className="learn-card" key={item.term}>
              <div className="learn-card-icon" style={{ borderColor: item.color, color: item.color }}>
                {String(idx + 1).padStart(2, "0")}
              </div>
              <div className="learn-card-body">
                <h3 className="learn-card-term">{item.term}</h3>
                <span className="learn-card-hindi">{item.hindi}</span>
                <p className="learn-card-def">{item.definition}</p>
                <p className="learn-card-def-hindi">{item.hindiDef}</p>
                <div className="learn-card-importance">
                  <span className="learn-card-label">Why it matters</span>
                  <p>{item.importance}</p>
                  <p className="learn-card-imp-hindi">{item.hindiImp}</p>
                </div>
                <div className="learn-card-example">
                  <span className="learn-card-label">Real-world example</span>
                  <p>{item.example}</p>
                  <p className="learn-card-ex-hindi">{item.hindiEx}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>

      <div className="learn-section">
        <div className="learn-header">
          <div className="eyebrow" style={{ marginBottom: 8 }}>Aquifer Basics · जलाधार मूल बातें</div>
          <h2 className="learn-title">Understanding Aquifers & Water Levels</h2>
        </div>
        <div className="learn-aquifer-grid">
          {aquiferBasics.map((item) => (
            <article className="learn-aquifer-card" key={item.title}>
              <h3 className="learn-aquifer-title">{item.title}</h3>
              <span className="learn-card-hindi">{item.hindi}</span>
              <p className="learn-aquifer-body">{item.body}</p>
              <p className="learn-aquifer-body-hindi">{item.hindiBody}</p>
            </article>
          ))}
        </div>
      </div>

      <div className="learn-section">
        <div className="learn-header">
          <div className="eyebrow" style={{ marginBottom: 8 }}>India Context · भारत संदर्भ</div>
          <h2 className="learn-title">How India Uses Groundwater</h2>
        </div>
        <div className="learn-usage-grid">
          <article className="learn-usage-card">
            <div className="learn-usage-header">
              <span className="learn-usage-pct">63%</span>
              <div>
                <span className="learn-usage-label">Irrigation</span>
                <span className="learn-usage-hindi">सिंचाई</span>
              </div>
            </div>
            <p className="learn-usage-body">
              India is the world's largest user of groundwater for irrigation. Over 20 million borewells and
              tube wells pump water for agriculture. States like Punjab, Haryana and western UP are heavily
              dependent — with extraction rates exceeding 100% in many blocks.
            </p>
            <p className="learn-usage-body-hindi">
              भारत सिंचाई के लिए भूजल का उपयोग करने वाला विश्व का सबसे बड़ा देश है। 20 मिलियन से अधिक बोरवेल और
              ट्यूबवेल कृषि के लिए पानी पंप करते हैं।
            </p>
          </article>
          <article className="learn-usage-card">
            <div className="learn-usage-header">
              <span className="learn-usage-pct">18%</span>
              <div>
                <span className="learn-usage-label">Domestic Use</span>
                <span className="learn-usage-hindi">घरेलू उपयोग</span>
              </div>
            </div>
            <p className="learn-usage-body">
              Over 80% of India's rural drinking water supply depends on groundwater. In urban areas,
              private borewells supplement municipal supply. Contamination from arsenic, fluoride and
              salinity affects millions across the Indo-Gangetic plain and coastal regions.
            </p>
            <p className="learn-usage-body-hindi">
              भारत के 80% से अधिक ग्रामीण पेयजल आपूर्ति भूजल पर निर्भर है। शहरी क्षेत्रों में,
              निजी बोरवेल नगरपालिका आपूर्ति का पूरक हैं।
            </p>
          </article>
          <article className="learn-usage-card">
            <div className="learn-usage-header">
              <span className="learn-usage-pct">19%</span>
              <div>
                <span className="learn-usage-label">Industrial Use</span>
                <span className="learn-usage-hindi">औद्योगिक उपयोग</span>
              </div>
            </div>
            <p className="learn-usage-body">
              Industrial clusters in Gujarat, Maharashtra, and Tamil Nadu draw heavily from deep aquifers.
              In Sabarkantha and Mehsana districts of Gujarat, industrial demand has contributed to
              declining water tables of 1-3 meters per year.
            </p>
            <p className="learn-usage-body-hindi">
              गुजरात, महाराष्ट्र और तमिलनाडु के औद्योगिक क्लस्टर गहरे जलाधारों से भारी मात्रा में पानी लेते हैं।
              गुजरात के साबरकांठा और मेहसाणा जिलों में औद्योगिक मांग ने जल स्तर में 1-3 मीटर प्रति वर्ष की गिरावट में योगदान दिया है।
            </p>
          </article>
        </div>
      </div>
    </section>
  );
}
