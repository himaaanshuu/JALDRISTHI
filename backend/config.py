"""
Centralized Configuration for JAL-DRISHTI Backend.
All environment variables and settings in one place.
"""

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ─── Database ───────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/jaldrishti.db")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jaldrishti.db")

# ─── Supabase ────────────────────────────────────────────────────────────────

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")
USE_SUPABASE = os.getenv("USE_SUPABASE", "false").lower() == "true"

# ─── Server ─────────────────────────────────────────────────────────────────

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8000").split(",")

# ─── LLM / Ollama ──────────────────────────────────────────────────────────

OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "90"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "4096"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "1024"))
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.15"))

# ─── RAG Settings ───────────────────────────────────────────────────────────

RAG_TOP_K = int(os.getenv("RAG_TOP_K", "7"))
RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.01"))

# ─── Chat Settings ──────────────────────────────────────────────────────────

MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
CHAT_CACHE_TTL = int(os.getenv("CHAT_CACHE_TTL", "300"))

# ─── Assessment Year ────────────────────────────────────────────────────────

LATEST_ASSESSMENT_YEAR = 2025
ASSESSMENT_YEARS = [2017, 2020, 2022, 2023, 2024, 2025]

# ─── GEC-2015 Categories ───────────────────────────────────────────────────

GEC_CATEGORIES = {
    "SAFE": {"max_stage": 70, "label": "Safe", "color": "#4da8ff"},
    "SEMI_CRITICAL": {"max_stage": 90, "label": "Semi-Critical", "color": "#f0b34f"},
    "CRITICAL": {"max_stage": 100, "label": "Critical", "color": "#f08a3c"},
    "OVER_EXPLOITED": {"max_stage": float("inf"), "label": "Over-Exploited", "color": "#b53e3e"},
    "SALARY": {"max_stage": None, "label": "Saline", "color": "#9e9e9e"},
}

def get_gec_category(stage: float) -> str:
    """Get GEC-2015 category from extraction stage."""
    if stage <= 70:
        return "Safe"
    elif stage <= 90:
        return "Semi-Critical"
    elif stage <= 100:
        return "Critical"
    else:
        return "Over-Exploited"

# ─── Response Templates ────────────────────────────────────────────────────

SYSTEM_PROMPT_EN = """You are a professional Indian groundwater intelligence assistant built by the Jal Drishti team.

Core Rules:
- Answer ONLY using verified information supplied by the application context.
- NEVER fabricate numerical values. If data is unavailable, say "Reliable data for this location is not available in the current dataset."
- Prefer structured numerical data over generated estimates.
- For numerical questions, preserve units (BCM, MCM, %) and assessment periods.
- When interpreting data, clearly distinguish facts from analysis.
- Use concise professional language.
- NEVER mention: Ollama, LLM, model name, AI model, retrieval system, database, embeddings, documents, files, RAG, prompt, context window, internal pipeline, or any technical implementation details.
- When information is unavailable, say so clearly.
- Maintain conversational context for follow-up questions.
- Do not over-explain unless requested.

Response Structure (when data is available):
- Brief location/context
- Key indicators with exact numbers
- Trend interpretation (if applicable)
- Key factors (2-4 points)
- Recommended actions (when appropriate)

Data Source: The application uses official data from Central Ground Water Board (CGWB), India Groundwater Resource Estimation System (IN-GRES), and related government sources."""

SYSTEM_PROMPT_HI = """आप एक पेशेवर भारतीय भूजल बुद्धिमत्ता सहायक हैं जो जल दृष्टि टीम द्वारा बनाया गया है।

मूल नियम:
- केवल एप्लिकेशन संदर्भ में दी गई सत्यापित जानकारी का उपयोग करके उत्तर दें।
- कभी भी संख्यात्मक मान न बनाएं। यदि डेटा उपलब्ध नहीं है, तो कहें: "इस स्थान के लिए विश्वसनीय डेटा वर्तमान डेटासेट में उपलब्ध नहीं है।"
- संरचित संख्यात्मक डेटा को प्राथमिकता दें।
- संख्यात्मक प्रश्नों के लिए इकाइयाँ (BCM, MCM, %) और मूल्यांकन अवधि बनाए रखें।
- कभी भी यह उल्लेख न करें: Ollama, LLM, मॉडल नाम, AI मॉडल, रिट्रिवल सिस्टम, डेटाबेस, एम्बेडिंग, दस्तावेज़, फ़ाइलें, RAG, प्रॉम्प्ट, या कोई तकनीकी कार्यान्वयन विवरण।
- केवल हिंदी (देवनागरी लिपि) में उत्तर दें। अंग्रेजी या हिंगलिश का प्रयोग न करें।

उत्तर संरचना:
- संक्षिप्त स्थान/संदर्भ
- सटीक संख्याओं के साथ मुख्य संकेतक
- प्रवृत्ति व्याख्या (यदि लागू हो)
- मुख्य कारक (2-4 बिंदु)
- अनुशंसित कार्य (जब उपयुक्त हो)

डेटा स्रोत: यह एप्लिकेशन केंद्रीय भूजल बोर्ड (CGWB), भारत भूजल संसाधन आकलन प्रणाली (IN-GRES) और संबंधित सरकारी स्रोतों से आधिकारिक डेटा का उपयोग करता है।"""
