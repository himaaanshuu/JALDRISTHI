"""
JAL-DRISHTI LLM RAG Pipeline
Retrieval-Augmented Generation for groundwater intelligence.
Uses Ollama (llama3.1:8b) for generation + TF-IDF for retrieval.
"""

import json
import os
import sqlite3
import subprocess
from typing import List, Dict, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─── Ollama Config ──────────────────────────────────────────────────────────

OLLAMA_BIN = os.getenv(
    "OLLAMA_BIN",
    "/Applications/Ollama.app/Contents/Resources/ollama",
)
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jaldrishti.db")


# ─── Knowledge Base ─────────────────────────────────────────────────────────

GROUNDWATER_DOMAIN_KB: List[Dict[str, str]] = [
    # === Core Concepts ===
    {
        "id": "gw_001",
        "topic": "Groundwater Basics",
        "content": (
            "Groundwater is water held underground in the soil or in pores and crevices in rock. "
            "It is recharged by rain and melts of snow and ice and is discharged into streams, wetlands, "
            "or lakes. In India, groundwater is the primary source of water for irrigation and drinking, "
            "supplying about 80% of rural water and 60% of urban water needs."
        ),
    },
    {
        "id": "gw_002",
        "topic": "Aquifer Types",
        "content": (
            "An aquifer is a body of porous rock or sediment saturated with groundwater. "
            "Types: (1) Unconfined Aquifer - directly recharged by surface water, water table is the upper surface. "
            "(2) Confined Aquifer - sandwiched between impermeable layers, water is under pressure. "
            "(3) Perched Aquifer - sits above the main water table on a clay layer. "
            "India has diverse aquifer systems including hard rock (Deccan Trap), alluvial (Ganga basin), "
            "and coastal aquifers."
        ),
    },
    {
        "id": "gw_003",
        "topic": "Groundwater Recharge",
        "content": (
            "Groundwater recharge is the process where water moves downward from surface to subsurface. "
            "Natural recharge occurs through precipitation, stream infiltration, and lake seepage. "
            "Artificial recharge includes rooftop rainwater harvesting, check dams, percolation tanks, "
            "and injection wells. In India, the Central Ground Water Board (CGWB) estimates total annual "
            "groundwater recharge at about 433 BCM (Billion Cubic Metres)."
        ),
    },
    {
        "id": "gw_004",
        "topic": "Extraction Stage",
        "content": (
            "Groundwater Extraction Stage = (Annual Groundwater Extraction / Annual Extractable Groundwater Resource) × 100. "
            "This is the key metric used by CGWB to classify blocks. "
            "If extraction stage > 100%, it means more water is being extracted than is naturally replenished, "
            "leading to declining water tables and long-term depletion."
        ),
    },
    {
        "id": "gw_005",
        "topic": "CGWB Categories",
        "content": (
            "CGWB classifies assessment units (blocks) into four categories based on extraction stage: "
            "(1) Safe: extraction stage < 70% - groundwater is within sustainable limits. "
            "(2) Semi-Critical: extraction stage 70-90% - needs monitoring, approaching limits. "
            "(3) Critical: extraction stage 90-100% - extraction near/at sustainability limit. "
            "(4) Over-Exploited: extraction stage > 100% - extraction exceeds recharge, requires intervention."
        ),
    },
    {
        "id": "gw_006",
        "topic": "IN-GRES",
        "content": (
            "India Groundwater Resource Estimation System (IN-GRES) is the methodology used by CGWB "
            "and state agencies to assess groundwater resources. It was jointly developed by CGWB and "
            "Central Water Commission (CWC). IN-GRES provides a standardized framework for estimating "
            "groundwater recharge, draft (extraction), and stage of extraction across all assessment units "
            "in India. The assessment is carried out at block/district level."
        ),
    },
    # === India-Specific Problems ===
    {
        "id": "gw_007",
        "topic": "Groundwater Depletion in India",
        "content": (
            "India is the largest user of groundwater in the world, extracting about 250 BCM annually. "
            "Key problem areas: (1) Punjab, Haryana, Rajasthan - over-exploited due to intensive irrigation. "
            "(2) Delhi, Chandigarh - urban over-extraction. "
            "(3) parts of Tamil Nadu, Karnataka - hard rock areas with declining water levels. "
            "NASA GRACE satellite data shows India lost about 18 BCM of groundwater between 2002-2021."
        ),
    },
    {
        "id": "gw_008",
        "topic": "Punjab Groundwater Crisis",
        "content": (
            "Punjab has the highest groundwater extraction stage in India at about 167%. "
            "Nearly 80% of blocks are classified as Over-Exploited. The crisis is driven by: "
            "(1) Rice-wheat monoculture requiring heavy irrigation. "
            "(2) Free electricity for pumping. "
            "(3) Minimum Support Price (MSP) incentivizing water-intensive crops. "
            "Water table dropping at 0.5-1 meter per year in many areas. The state needs crop diversification "
            "and micro-irrigation to become sustainable."
        ),
    },
    {
        "id": "gw_009",
        "topic": "Rajasthan Groundwater",
        "content": (
            "Rajasthan faces acute groundwater stress due to arid/semi-arid climate with very low rainfall "
            "(100-600mm annually). Over 70% of the state's blocks are Over-Exploited. "
            "Key issues: (1) Very low natural recharge. (2) Deep tube wells drawing fossil water. "
            "(3) Traditional water harvesting (johads, baoris) falling into disuse. "
            "The state has launched Jal Swavlamban Abhiyan and Mukhyamantri Jal Swarthan Yojana "
            "for community-based water management."
        ),
    },
    {
        "id": "gw_010",
        "topic": "Hard Rock Aquifers India",
        "content": (
            "About 65% of India's area is covered by hard rock aquifers (Deccan Trap basalt, "
            "granite-gneiss, schist). These have: (1) Low storage capacity - typically 1-5% porosity. "
            "(2) High spatial variability in yields. (3) Water table depends on fracture connectivity. "
            "States with significant hard rock areas: Maharashtra, Karnataka, Telangana, "
            "Andhra Pradesh, Madhya Pradesh, Rajasthan, Tamil Nadu. Yield in hard rock areas: "
            "1-50 m³/hour compared to 50-200 m³/hour in alluvial areas."
        ),
    },
    {
        "id": "gw_011",
        "topic": "Alluvial Aquifers India",
        "content": (
            "The Indo-Gangetic alluvial plains contain India's most productive aquifers. "
            "Covering states: UP, Bihar, West Bengal, Haryana, Punjab, parts of Rajasthan. "
            "Features: (1) High storage - 10-30% porosity. (2) Good yields - 50-200+ m³/hour. "
            "(3) Multiple aquifer layers. (4) Connected to river systems for recharge. "
            "Despite high potential, extraction in many areas exceeds recharge, especially in Punjab, "
            "Haryana, and western UP."
        ),
    },
    {
        "id": "gw_012",
        "topic": "Groundwater Contamination",
        "content": (
            "Major groundwater contamination issues in India: "
            "(1) Fluoride - affects 19 states, mainly Rajasthan, AP, Telangana, Karnataka. "
            "Causes skeletal fluorosis. WHO limit: 1.5 mg/L. "
            "(2) Arsenic - affects West Bengal, Bihar, UP, Assam. Linked to rice paddies and geology. "
            "WHO limit: 10 µg/L. "
            "(3) Nitrate - from agricultural runoff and sewage. Common in Maharashtra, Karnataka. "
            "WHO limit: 50 mg/L. "
            "(4) Salinity - coastal and arid regions."
        ),
    },
    {
        "id": "gw_013",
        "topic": "Inter-State Water Conflicts",
        "content": (
            "Groundwater-related interstate disputes in India include: "
            "(1) Cauvery water dispute - Karnataka vs Tamil Nadu vs Kerala vs Puducherry. "
            "(2) Krishna water dispute - Maharashtra vs Karnataka vs AP vs Telangana. "
            "(3) Ravi-Beas dispute - Punjab vs Haryana vs Rajasthan. "
            "(4) Narmada water dispute - MP vs Gujarat vs Maharashtra vs Rajasthan. "
            "Tribunals resolve surface water disputes, but groundwater conflicts are largely unaddressed."
        ),
    },
    # === Policy & Management ===
    {
        "id": "gw_014",
        "topic": "National Water Policy",
        "content": (
            "India's National Water Policy (2012, under revision 2024) addresses groundwater: "
            "(1) Treats groundwater as a community resource managed by local bodies. "
            "(2) Promotes rooftop rainwater harvesting. "
            "(3) Encourages micro-irrigation (drip, sprinkler). "
            "(4) Suggests pricing of groundwater extraction. "
            "States have their own groundwater acts - some regulate tube well registration, "
            "others mandate no-objection certificates for new wells."
        ),
    },
    {
        "id": "gw_015",
        "topic": "Atal Bhujal Yojana",
        "content": (
            "Atal Bhujal Yojana (ABHY) is a World Bank-funded ($1B) community-led groundwater "
            "management program launched in 2020. It covers 8000+ water-stressed Gram Panchayats "
            "across 80 districts in 7 states: Haryana, Gujarat, Karnataka, Madhya Pradesh, "
            "Maharashtra, Rajasthan, and Uttar Pradesh. Key features: (1) Incentive-based - "
            "communities get funds based on their water conservation efforts. "
            "(2) Data-driven - uses real-time monitoring. "
            "(3) Community participation in demand management."
        ),
    },
    {
        "id": "gw_016",
        "topic": "Micro Irrigation",
        "content": (
            "Micro irrigation (drip and sprinkler systems) can reduce groundwater extraction by 30-70%. "
            "Government schemes: (1) Pradhan Mantri Krishi Sinchayee Yojana (PMKSY) - provides 55% subsidy "
            "for small/marginal farmers, 45% for others. "
            "(2) State-level subsidies vary - some states offer up to 80% for SC/ST farmers. "
            "Current coverage: ~15 million hectares out of 142 million hectares irrigated area. "
            "Target: 20 million hectares by 2026."
        ),
    },
    {
        "id": "gw_017",
        "topic": "CGWB Organization",
        "content": (
            "Central Ground Water Board (CGWB) is under the Ministry of Jal Shakti. "
            "It is the apex body for: (1) Groundwater exploration and assessment. "
            "(2) Maintenance of national aquifer maps. "
            "(3) Groundwater monitoring through a network of ~25,000 observation wells. "
            "(4) Issuing guidelines for groundwater regulation. "
            "CGWB carries out groundwater assessment at block level in collaboration with "
            "State Ground Water Departments. Assessment cycle: typically every 3-5 years."
        ),
    },
    {
        "id": "gw_018",
        "topic": "Groundwater Regulation",
        "content": (
            "Key regulatory measures for groundwater in India: "
            "(1) Model Groundwater (Sustainable Management) Act, 2017 - provides framework for states. "
            "(2) Registration of borewells - required in many states. "
            "(3) Rainwater harvesting mandates - mandatory in most urban areas. "
            "(4) No-objection certificates for new wells in over-exploited areas. "
            "(5) Groundwater pricing in some states (Punjab, Haryana). "
            "Enforcement remains weak in many regions."
        ),
    },
    # === Data & Measurement ===
    {
        "id": "gw_019",
        "topic": "Measurement Units",
        "content": (
            "Groundwater measurement units used in India: "
            "(1) BCM (Billion Cubic Metres) = 1 billion m³ = 1 km³. Used for national/state-level totals. "
            "(2) MCM (Million Cubic Metres) = 1 million m³ = 1 TMC (Thousand Million Cubic feet) roughly. "
            "Used for district/block-level data. 1 BCM = 1000 MCM. "
            "(3) Ham (hectare-metres) = volume of water needed to cover 1 hectare to depth of 1 metre. "
            "1 ham = 10,000 m³ = 10 MCM. "
            "(4) m³ (cubic metres) - base SI unit. 1 m³ = 1000 litres."
        ),
    },
    {
        "id": "gw_020",
        "topic": "Data Sources",
        "content": (
            "Primary groundwater data sources for India: "
            "(1) CGWB Groundwater Assessment Reports - block-level extraction/recharge data. "
            "(2) IN-GRES portal (ingres.iith.ac.in) - digital platform for groundwater data. "
            "(3) Central Water Commission (CWC) - surface water and river flow data. "
            "(4) India Water Resources Information System (India-WRIS) - integrated water data. "
            "(5) State Ground Water Departments - local monitoring data. "
            "(6) NASA GRACE satellites - groundwater storage changes."
        ),
    },
    # === Solutions & Best Practices ===
    {
        "id": "gw_021",
        "topic": "Rainwater Harvesting",
        "content": (
            "Rainwater harvesting is the most effective way to augment groundwater recharge. "
            "Methods: (1) Rooftop harvesting - collecting rain from building roofs into tanks/borewells. "
            "(2) Surface runoff harvesting - check dams, percolation ponds, trenching. "
            "(3) Farm ponds - dug in fields to collect runoff. "
            "Success stories: (1) Rajasthan's traditional johads revived by community efforts. "
            "(2) Chennai mandatory rooftop harvesting since 2001. "
            "(3) Meghalaya's living root bridges for water management."
        ),
    },
    {
        "id": "gw_022",
        "topic": "Crop Diversification",
        "content": (
            "Shifting from water-intensive crops to less water-demanding alternatives: "
            "(1) Replace rice with millets, pulses, or oilseeds in water-scarce areas. "
            "(2) Replace sugarcane with less water-intensive crops in Maharashtra. "
            "(3) Alternate wetting and drying (AWD) in rice reduces water use by 20-30%. "
            "Punjab's paddy area: ~2.8 million hectares, requiring ~35 BCM of water annually. "
            "Switching even 20% to millets could save ~7 BCM of groundwater."
        ),
    },
    {
        "id": "gw_023",
        "topic": "Water Level Monitoring",
        "content": (
            "CGWB monitors groundwater levels through ~25,000 observation wells across India. "
            "Monitoring is done: (1) Pre-monsoon (May-June) - shows maximum depletion. "
            "(2) Post-monsoon (October-November) - shows recharge. "
            "Declining trends are observed in: (1) North-West India (Punjab, Haryana, Delhi). "
            "(2) South India hard rock areas (parts of Karnataka, TN, AP). "
            "Water level data is available on CGWB's web portal and India-WRIS."
        ),
    },
    {
        "id": "gw_024",
        "topic": "Climate Change Impact",
        "content": (
            "Climate change impacts on Indian groundwater: "
            "(1) Erratic monsoon patterns reduce recharge reliability. "
            "(2) Increased temperatures raise evapotranspiration. "
            "(3) Glacial melt affects Himalayan-fed rivers and their alluvial aquifers. "
            "(4) Sea level rise causes saltwater intrusion in coastal aquifers (Gujarat, Bengal, Kerala). "
            "(5) More frequent droughts increase extraction pressure. "
            "IPCC projects 10-25% reduction in groundwater recharge in semi-arid India by 2050."
        ),
    },
]


# ─── DB Knowledge Extractor ──────────────────────────────────────────────────

def _extract_db_knowledge(db_path: str) -> List[Dict[str, str]]:
    """Extract knowledge documents from the SQLite database."""
    documents = []
    if not os.path.exists(db_path):
        return documents

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get summary stats
    try:
        cursor.execute("SELECT COUNT(*) FROM groundwater")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT state) FROM groundwater")
        states = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT district) FROM groundwater WHERE district != ''")
        districts = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT block) FROM groundwater WHERE block != ''")
        blocks = cursor.fetchone()[0]

        documents.append({
            "id": "db_summary",
            "topic": "Database Summary",
            "content": (
                f"The JAL-DRISHTI database contains {total} groundwater assessment records "
                f"covering {states} states/UTs, {districts} districts, and {blocks} assessment blocks. "
                f"Data is sourced from CGWB/IN-GRES official assessments."
            ),
        })
    except Exception:
        pass

    # Get state-level summaries
    try:
        cursor.execute("""
            SELECT state,
                   COUNT(DISTINCT district) as districts,
                   COUNT(DISTINCT block) as blocks,
                   ROUND(AVG(extraction_stage), 1) as avg_stage,
                   ROUND(SUM(groundwater_extraction), 0) as total_extraction,
                   ROUND(SUM(annual_groundwater_recharge), 0) as total_recharge
            FROM groundwater
            WHERE district != '' AND block != ''
            GROUP BY state
            ORDER BY avg_stage DESC
        """)
        for row in cursor.fetchall():
            state, dists, blks, avg_stage, tot_ext, tot_rec = row
            if not state:
                continue
            documents.append({
                "id": f"db_state_{state.lower().replace(' ', '_')}",
                "topic": f"{state} Groundwater",
                "content": (
                    f"{state}: {blks} blocks assessed across {dists} districts. "
                    f"Average extraction stage: {avg_stage}%. "
                    f"Total extraction: {tot_ext:,.0f} MCM, Total recharge: {tot_rec:,.0f} MCM. "
                    f"{'OVER-EXPLOITED - extraction exceeds recharge.' if avg_stage > 100 else 'CRITICAL - extraction near limits.' if avg_stage > 90 else 'SEMI-CRITICAL - needs monitoring.' if avg_stage > 70 else 'SAFE - within sustainable limits.'}"
                ),
            })
    except Exception:
        pass

    # Get top over-exploited blocks
    try:
        cursor.execute("""
            SELECT block, district, state, extraction_stage, groundwater_extraction
            FROM groundwater
            WHERE category = 'Over-Exploited' AND block != ''
            ORDER BY extraction_stage DESC
            LIMIT 50
        """)
        rows = cursor.fetchall()
        if rows:
            lines = [f"{r[0]}, {r[1]} ({r[2]}): {r[3]:.1f}% stage, {r[4]:,.0f} MCM extraction" for r in rows]
            documents.append({
                "id": "db_overexploited_top",
                "topic": "Top Over-Exploited Blocks",
                "content": (
                    f"Most over-exploited blocks in the database: "
                    + "; ".join(lines[:10]) + ". "
                    + f"Total {len(rows)} over-exploited blocks found."
                ),
            })
    except Exception:
        pass

    conn.close()
    return documents


# ─── RAG Engine ─────────────────────────────────────────────────────────────

class RAGEngine:
    """Retrieval-Augmented Generation engine for groundwater queries."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.documents: List[Dict[str, str]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build the knowledge base from domain KB + database."""
        # Add domain knowledge
        self.documents.extend(GROUNDWATER_DOMAIN_KB)
        # Add DB knowledge
        self.documents.extend(_extract_db_knowledge(self.db_path))
        # Build TF-IDF index
        corpus = [doc["content"] for doc in self.documents]
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """Retrieve most relevant documents for a query."""
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = scores.argsort()[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if scores[idx] > 0.01:
                doc = self.documents[idx].copy()
                doc["relevance_score"] = round(float(scores[idx]), 3)
                results.append(doc)
        return results

    def _query_db_for_context(self, query: str) -> str:
        """Query the database directly for specific state/district/block data."""
        if not os.path.exists(self.db_path):
            return ""

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Extract state names from query for direct DB lookup
        from parser import KNOWN_STATES
        mentioned_states = [s for s in KNOWN_STATES if s.lower() in query.lower()]

        context_parts = []

        for state in mentioned_states[:2]:
            try:
                cursor.execute("""
                    SELECT state, district, block, assessment_year,
                           annual_groundwater_recharge, groundwater_extraction,
                           extraction_stage, category
                    FROM groundwater
                    WHERE state = ? AND block != ''
                    ORDER BY extraction_stage DESC
                    LIMIT 10
                """, (state,))
                rows = cursor.fetchall()
                if rows:
                    lines = [f"{r['block']}, {r['district']}: {r['extraction_stage']:.1f}% stage, "
                             f"{r['category']}, extraction={r['groundwater_extraction']:.0f} MCM "
                             f"(year {r['assessment_year']})" for r in rows]
                    context_parts.append(
                        f"Database records for {state} (top 10 blocks by extraction stage):\n"
                        + "\n".join(lines)
                    )
            except Exception:
                pass

        # Also get national summary if relevant
        try:
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(DISTINCT state) as states,
                    ROUND(AVG(extraction_stage), 1) as avg_stage,
                    ROUND(SUM(groundwater_extraction), 0) as total_ext
                FROM groundwater WHERE block != ''
            """)
            row = cursor.fetchone()
            if row:
                context_parts.append(
                    f"National summary: {row['total']} blocks across {row['states']} states, "
                    f"average extraction stage: {row['avg_stage']}%, "
                    f"total extraction: {row['total_ext']:,.0f} MCM"
                )
        except Exception:
            pass

        conn.close()
        return "\n\n".join(context_parts)

    def generate(self, query: str, top_k: int = 5) -> Dict:
        """Generate a response using RAG."""
        # Retrieve relevant documents
        retrieved = self.retrieve(query, top_k=top_k)
        context_docs = "\n\n".join(
            f"[{doc['topic']}] {doc['content']}" for doc in retrieved
        )

        # Get DB-specific context
        db_context = self._query_db_for_context(query)

        # Build the system prompt
        system_prompt = """You are JAL-DRISHTI AI, an expert groundwater intelligence assistant for India.
You have access to official CGWB/IN-GRES groundwater assessment data and domain knowledge.
Answer questions accurately, using specific numbers when available.
If discussing specific states/districts, reference actual data from the knowledge base.
Provide practical recommendations where relevant.
Always mention the data source when citing statistics.
Answer in the same language the user writes in (English, Hindi, or Hinglish)."""

        # Build the user prompt with context
        user_prompt = f"""Knowledge Base Context:
{context_docs}

Database Records:
{db_context}

User Question: {query}

Provide a comprehensive, accurate answer based on the above context. Use specific numbers and data where available. If the data is not available in the context, say so clearly."""

        # Call Ollama
        try:
            result = subprocess.run(
                [OLLAMA_BIN, "run", LLM_MODEL, "--nowordwrap"],
                input=json.dumps({
                    "model": LLM_MODEL,
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_ctx": 4096,
                    },
                }),
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                return {
                    "reply": f"Error calling Ollama: {result.stderr[:500]}",
                    "sources": [],
                    "retrieved_docs": retrieved,
                }

            # Parse Ollama response
            try:
                response_data = json.loads(result.stdout)
                reply = response_data.get("response", result.stdout)
            except json.JSONDecodeError:
                reply = result.stdout.strip()

        except subprocess.TimeoutExpired:
            return {
                "reply": "The LLM request timed out after 120 seconds. Please try again.",
                "sources": [],
                "retrieved_docs": retrieved,
            }
        except FileNotFoundError:
            return {
                "reply": (
                    "Ollama is not installed or not found at the expected path. "
                    "Please install Ollama from https://ollama.ai and ensure it's running."
                ),
                "sources": [],
                "retrieved_docs": retrieved,
            }
        except Exception as e:
            return {
                "reply": f"Error generating response: {str(e)}",
                "sources": [],
                "retrieved_docs": retrieved,
            }

        # Build sources from retrieved docs
        sources = []
        for doc in retrieved:
            sources.append({
                "title": doc["topic"],
                "relevance": doc.get("relevance_score", 0),
                "content_preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
            })

        return {
            "reply": reply,
            "sources": sources,
            "retrieved_docs": retrieved,
        }


# ─── Singleton ──────────────────────────────────────────────────────────────

_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine


def rebuild_rag_engine():
    global _rag_engine
    _rag_engine = RAGEngine()
