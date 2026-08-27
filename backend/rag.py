"""
JAL-DRISHTI LLM RAG Pipeline
Retrieval-Augmented Generation for groundwater intelligence.
Uses Ollama (llama3.1:8b) for generation + TF-IDF for retrieval.
Optimized for speed: HTTP API instead of subprocess, minimal context.
"""

import json
import os
import sqlite3
import requests
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─── Ollama Config ──────────────────────────────────────────────────────────

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jaldrishti.db")


# ─── Knowledge Base ─────────────────────────────────────────────────────────

GROUNDWATER_DOMAIN_KB: List[Dict[str, str]] = [
    {
        "id": "gw_001", "topic": "Groundwater Basics",
        "content": "Groundwater is water held underground in soil or rock pores. In India, it supplies 80% of rural water and 60% of urban water. India is the largest groundwater user extracting ~250 BCM annually.",
    },
    {
        "id": "gw_002", "topic": "Aquifer Types",
        "content": "Types: (1) Unconfined - directly recharged by surface water. (2) Confined - between impermeable layers, under pressure. (3) Perched - above main water table. India has hard rock (Deccan Trap), alluvial (Ganga basin), and coastal aquifers.",
    },
    {
        "id": "gw_003", "topic": "Groundwater Recharge",
        "content": "Recharge is water moving downward from surface to subsurface. Natural: precipitation, stream infiltration. Artificial: rainwater harvesting, check dams, percolation tanks. India total annual recharge: ~433 BCM.",
    },
    {
        "id": "gw_004", "topic": "Extraction Stage Formula",
        "content": "Extraction Stage = (Annual Extraction / Annual Extractable Resource) x 100. Key CGWB metric. >100% means extraction exceeds recharge causing depletion.",
    },
    {
        "id": "gw_005", "topic": "CGWB Categories",
        "content": "Safe: <70% stage. Semi-Critical: 70-90%. Critical: 90-100%. Over-Exploited: >100%. Classification by Central Ground Water Board for assessment blocks.",
    },
    {
        "id": "gw_006", "topic": "IN-GRES System",
        "content": "India Groundwater Resource Estimation System (IN-GRES) by CGWB+CWC. Standardized framework for block-level groundwater assessment across India.",
    },
    {
        "id": "gw_007", "topic": "India Depletion Crisis",
        "content": "India extracts ~250 BCM/year, largest user globally. Worst: Punjab (167% stage), Haryana, Rajasthan. NASA GRACE data: India lost ~18 BCM between 2002-2021. Water table dropping 0.5-1m/year in Punjab.",
    },
    {
        "id": "gw_008", "topic": "Punjab Crisis",
        "content": "Punjab: 167% extraction stage, 80% blocks Over-Exploited. Caused by rice-wheat monoculture, free electricity for pumps, MSP incentives. Water table drops 0.5-1m/year. Needs crop diversification.",
    },
    {
        "id": "gw_009", "topic": "Rajasthan Stress",
        "content": "Rajasthan: 70%+ blocks Over-Exploited. Arid climate (100-600mm rainfall), very low recharge, deep tube wells drawing fossil water. Traditional harvesting (johads, baoris) declining.",
    },
    {
        "id": "gw_010", "topic": "Hard Rock Aquifers",
        "content": "65% of India is hard rock (basalt, granite-gneiss). Low storage (1-5% porosity), yields 1-50 m3/hour. States: Maharashtra, Karnataka, Telangana, AP, MP, Rajasthan, Tamil Nadu.",
    },
    {
        "id": "gw_011", "topic": "Alluvial Aquifers",
        "content": "Indo-Gangetic plains: most productive aquifers. 10-30% porosity, 50-200+ m3/hour yields. States: UP, Bihar, WB, Haryana, Punjab. Despite high potential, many areas over-extracted.",
    },
    {
        "id": "gw_012", "topic": "Contamination Issues",
        "content": "Fluoride: 19 states (Rajasthan, AP, Telangana, Karnataka), causes fluorosis, WHO limit 1.5mg/L. Arsenic: WB, Bihar, UP, Assam, WHO limit 10ug/L. Nitrate: Maharashtra, Karnataka, WHO limit 50mg/L.",
    },
    {
        "id": "gw_013", "topic": "Water Conflicts",
        "content": "Major disputes: Cauvey (KA vs TN), Krishna (MH vs KA vs AP vs TS), Ravi-Beas (Punjab vs Haryana vs Rajasthan), Narmada (MP vs GJ vs MH vs RJ). Groundwater conflicts largely unaddressed.",
    },
    {
        "id": "gw_014", "topic": "National Water Policy",
        "content": "Policy 2012 (under revision 2024): groundwater as community resource, promotes rainwater harvesting, micro-irrigation, suggests pricing. States have own groundwater acts.",
    },
    {
        "id": "gw_015", "topic": "Atal Bhujal Yojana",
        "content": "World Bank $1B program (2020): community-led groundwater management. 8000+ Gram Panchayats in 80 districts across 7 states (Haryana, Gujarat, Karnataka, MP, Maharashtra, Rajasthan, UP). Incentive-based conservation.",
    },
    {
        "id": "gw_016", "topic": "Micro Irrigation",
        "content": "Drip/sprinkler reduces extraction 30-70%. PMKSY scheme: 55% subsidy for small farmers. Current: ~15M hectares. Target: 20M hectares by 2026.",
    },
    {
        "id": "gw_017", "topic": "CGWB Organization",
        "content": "Under Ministry of Jal Shakti. Maintains 25,000 observation wells. Conducts block-level assessment every 3-5 years with state departments.",
    },
    {
        "id": "gw_018", "topic": "Regulation Measures",
        "content": "Model Groundwater Act 2017, borewell registration, rainwater harvesting mandates, NOC for new wells in over-exploited areas, groundwater pricing in some states. Enforcement weak.",
    },
    {
        "id": "gw_019", "topic": "Measurement Units",
        "content": "BCM = Billion Cubic Metres = 1km3 (national totals). MCM = Million Cubic Metres (district/block level). 1 BCM = 1000 MCM. Ham = hectare-metres, 1 ham = 10,000 m3 = 10 MCM.",
    },
    {
        "id": "gw_020", "topic": "Data Sources",
        "content": "CGWB Reports (block-level), IN-GRES portal, CWC (surface water), India-WRIS, State Ground Water Departments, NASA GRACE satellites.",
    },
    {
        "id": "gw_021", "topic": "Rainwater Harvesting",
        "content": "Most effective recharge method. Rooftop, surface runoff (check dams, percolation ponds), farm ponds. Success: Rajasthan johads, Chennai mandatory rooftop since 2001.",
    },
    {
        "id": "gw_022", "topic": "Crop Diversification",
        "content": "Replace rice with millets/pulses, sugarcane with less water crops. AWD in rice saves 20-30% water. Punjab paddy: 2.8M hectares needing ~35 BCM/year. 20% switch saves ~7 BCM.",
    },
    {
        "id": "gw_023", "topic": "Water Level Monitoring",
        "content": "CGWB monitors 25,000 wells. Pre-monsoon (May-June): max depletion. Post-monsoon (Oct-Nov): recharge. Declining: NW India (Punjab, Haryana, Delhi), South hard rock areas.",
    },
    {
        "id": "gw_024", "topic": "Climate Change Impact",
        "content": "Erratic monsoons reduce recharge. Higher temps increase evapotranspiration. Glacial melt affects Himalayan rivers. Sea level rise causes coastal saltwater intrusion (Gujarat, Bengal, Kerala). IPCC: 10-25% recharge reduction by 2050.",
    },
]


# ─── DB Knowledge Extractor ──────────────────────────────────────────────────

def _extract_db_knowledge(db_path: str) -> List[Dict[str, str]]:
    documents = []
    if not os.path.exists(db_path):
        return documents
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM groundwater"); total = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT state) FROM groundwater"); states = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT district) FROM groundwater WHERE district != ''"); districts = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT block) FROM groundwater WHERE block != ''"); blocks = c.fetchone()[0]
        documents.append({"id": "db_summary", "topic": "Database Summary", "content": f"JAL-DRISHTI DB: {total} records, {states} states, {districts} districts, {blocks} blocks from CGWB/IN-GRES."})
    except Exception:
        pass
    try:
        c.execute("""SELECT state, COUNT(DISTINCT district), COUNT(DISTINCT block),
            ROUND(AVG(extraction_stage),1), ROUND(SUM(groundwater_extraction),0), ROUND(SUM(annual_groundwater_recharge),0)
            FROM groundwater WHERE district != '' AND block != '' GROUP BY state ORDER BY AVG(extraction_stage) DESC""")
        for row in c.fetchall():
            s, d, b, avg, te, tr = row
            if not s: continue
            status = "OVER-EXPLOITED" if avg > 100 else "CRITICAL" if avg > 90 else "SEMI-CRITICAL" if avg > 70 else "SAFE"
            documents.append({"id": f"db_{s.lower().replace(' ','_')}", "topic": f"{s} Groundwater",
                "content": f"{s}: {b} blocks, {d} districts. Stage: {avg}%. Extraction: {te:,.0f} MCM. Recharge: {tr:,.0f} MCM. Status: {status}."})
    except Exception:
        pass
    try:
        c.execute("""SELECT block, district, state, extraction_stage, groundwater_extraction
            FROM groundwater WHERE category='Over-Exploited' AND block!='' ORDER BY extraction_stage DESC LIMIT 20""")
        rows = c.fetchall()
        if rows:
            txt = "; ".join(f"{r[0]},{r[1]}({r[2]}):{r[3]:.0f}%" for r in rows)
            documents.append({"id": "db_oe_top", "topic": "Top Over-Exploited Blocks", "content": f"Most over-exploited: {txt}"})
    except Exception:
        pass
    conn.close()
    return documents


# ─── RAG Engine ─────────────────────────────────────────────────────────────

class RAGEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.documents: List[Dict[str, str]] = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build()

    def _build(self):
        self.documents.extend(GROUNDWATER_DOMAIN_KB)
        self.documents.extend(_extract_db_knowledge(self.db_path))
        corpus = [d["content"] for d in self.documents]
        self.vectorizer = TfidfVectorizer(max_features=3000, stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 5):
        # TF-IDF retrieval
        qv = self.vectorizer.transform([query])
        tfidf_scores = cosine_similarity(qv, self.tfidf_matrix).flatten()

        # Keyword fallback: boost docs whose topic/content match query words
        query_words = set(query.lower().split())

        # Hindi keyword mapping
        hi_map = {
            "भूजल": "groundwater", "संकट": "crisis", "कारण": "causes", "निकासी": "extraction",
            "रिचार्ज": "recharge", "स्थिति": "status", "जिला": "district", "राज्य": "state",
            "ब्लॉक": "block", "श्रेणी": "category", "सुरक्षित": "safe", "गंभीर": "critical",
            "अत्यधिक": "over", "दोहन": "exploited", "प्रवृत्ति": "trend", "तुलना": "compare",
            "जलस्तर": "water level", "संदूषण": "contamination", "फ्लोराइड": "fluoride",
            "आर्सेनिक": "arsenic", "नीति": "policy", "योजना": "scheme", "सिंचाई": "irrigation",
            "कृषि": "agriculture", "मानसून": "monsoon", "वर्षा": "rainfall", "जल": "water",
            "भूमि": "land", "पानी": "water", "कुआं": "well", "ट्यूबवेल": "tube well",
            "अक्विफर": "aquifer", "प्रकार": "types", "प्रबंधन": "management", "संरक्षण": "conservation",
            "समस्या": "problem", "समाधान": "solution", "सरकार": "government", "मंत्रालय": "ministry",
        }

        # Translate Hindi words to English for matching
        expanded_words = set(query_words)
        for hi, en in hi_map.items():
            if hi in query.lower():
                expanded_words.add(en)

        keyword_scores = []
        for doc in self.documents:
            doc_text = (doc["topic"] + " " + doc["content"]).lower()
            matches = sum(1 for w in expanded_words if w in doc_text)
            keyword_scores.append(matches / max(len(expanded_words), 1))
        keyword_scores = [s * 0.3 for s in keyword_scores]

        # Combine scores
        combined = tfidf_scores + keyword_scores
        top = combined.argsort()[-top_k:][::-1]
        results = []
        for i in top:
            if combined[i] > 0.0:
                doc = self.documents[i].copy()
                doc["relevance_score"] = round(float(combined[i]), 3)
                results.append(doc)
        return results

    def _query_db(self, query: str) -> str:
        if not os.path.exists(self.db_path):
            return ""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        from parser import KNOWN_STATES
        mentioned = [s for s in KNOWN_STATES if s.lower() in query.lower()]
        parts = []
        for state in mentioned[:2]:
            try:
                c.execute("""SELECT block, district, extraction_stage, category, groundwater_extraction, assessment_year
                    FROM groundwater WHERE state=? AND block!='' ORDER BY extraction_stage DESC LIMIT 8""", (state,))
                rows = c.fetchall()
                if rows:
                    lines = [f"{r['block']},{r['district']}: {r['extraction_stage']:.1f}% {r['category']} {r['groundwater_extraction']:.0f}MCM({r['assessment_year']})" for r in rows]
                    parts.append(f"{state} data:\n" + "\n".join(lines))
            except Exception:
                pass
        conn.close()
        return "\n\n".join(parts)

    def generate(self, query: str, top_k: int = 5, language: str = "english") -> Dict:
        retrieved = self.retrieve(query, top_k=top_k)
        context = "\n".join(f"[{d['topic']}] {d['content']}" for d in retrieved)
        db_ctx = self._query_db(query)

        lang = "hindi" if language in ("hindi", "hinglish") else "english"

        system = f"""You are JAL-DRISHTI AI, a groundwater expert for India.

LANGUAGE RULE - MOST IMPORTANT:
Respond 100% in {lang.upper()}.
- If HINDI: ALL text in Devanagari script. No English words. Use Hindi terms: "भूजल निकासी चरण" not "extraction stage", "केंद्रीय भूजल बोर्ड" not "CGWB".
- If ENGLISH: ALL text in English. No Hindi/Devanagari.
- NEVER mix languages. NEVER use Hinglish.

Use data and numbers from context. Be concise. Mention source when citing stats."""

        user = f"""Context:\n{context}\n\n{db_ctx}\n\nQuestion: {query}\n\nAnswer in {lang}:"""

        try:
            resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
                "model": LLM_MODEL,
                "prompt": user,
                "system": system,
                "stream": False,
                "options": {"temperature": 0.2, "top_p": 0.85, "num_ctx": 2048, "num_predict": 512},
            }, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            reply = data.get("response", "")
        except requests.exceptions.ConnectionError:
            return {"reply": "Ollama is not running. Please start Ollama and try again.", "sources": [], "retrieved_docs": retrieved}
        except requests.exceptions.Timeout:
            return {"reply": "Request timed out. Please try again.", "sources": [], "retrieved_docs": retrieved}
        except Exception as e:
            return {"reply": f"Error: {str(e)[:200]}", "sources": [], "retrieved_docs": retrieved}

        sources = [{"title": d["topic"], "relevance": d.get("relevance_score", 0),
                     "content_preview": d["content"][:150]} for d in retrieved]
        return {"reply": reply, "sources": sources, "retrieved_docs": retrieved}


# ─── Singleton ──────────────────────────────────────────────────────────────

_rag_engine = None

def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

def rebuild_rag_engine():
    global _rag_engine
    _rag_engine = RAGEngine()
