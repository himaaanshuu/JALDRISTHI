"""
JAL-DRISHTI AI — Structured Chat Intent Parser
==============================================
Deterministic NLU: extracts structured intent from natural language queries.
No LLM required — pure regex + keyword matching.

Supports: English, Hindi (Devanagari), Hinglish (Romanized Hindi).
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


KNOWN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu & Kashmir", "Ladakh", "Chandigarh",
    "Puducherry",
]


@dataclass
class ChatIntent:
    """Structured intent parsed from a user query."""
    intent: str = "general"
    state: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    year: Optional[int] = None
    comparison_years: List[int] = field(default_factory=list)
    metric: Optional[str] = None
    category: Optional[str] = None
    confidence: float = 0.0
    language: str = "english"
    raw_message: str = ""

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "state": self.state,
            "district": self.district,
            "block": self.block,
            "year": self.year,
            "comparison_years": self.comparison_years,
            "metric": self.metric,
            "category": self.category,
            "confidence": self.confidence,
            "language": self.language,
            "raw_message": self.raw_message,
        }

# State name aliases (common misspellings / abbreviations)
STATE_ALIASES = {
    "up": "Uttar Pradesh",
    "tn": "Tamil Nadu",
    "wb": "West Bengal",
    "mp": "Madhya Pradesh",
    "ap": "Andhra Pradesh",
    "rajasthan": "Rajasthan",
    "gujarat": "Gujarat",
    "maharashtra": "Maharashtra",
    "punjab": "Punjab",
    "karnataka": "Karnataka",
    "tamil nadu": "Tamil Nadu",
    "tamilnadu": "Tamil Nadu",
    "uttar pradesh": "Uttar Pradesh",
    "west bengal": "West Bengal",
    "bengal": "West Bengal",
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
    # Hindi state names (Devanagari)
    "राजस्थान": "Rajasthan",
    "गुजरात": "Gujarat",
    "महाराष्ट्र": "Maharashtra",
    "पंजाब": "Punjab",
    "तमिल नाडु": "Tamil Nadu",
    "तमिलनाडु": "Tamil Nadu",
    "उत्तर प्रदेश": "Uttar Pradesh",
    "कर्नाटक": "Karnataka",
    "पश्चिम बंगाल": "West Bengal",
    # Hindi state names (Romanized / Hinglish)
    "rajasthan": "Rajasthan",
    "gujarat": "Gujarat",
    "maharashtra": "Maharashtra",
    "punjab": "Punjab",
    "karnataka": "Karnataka",
    "uttar pradesh": "Uttar Pradesh",
}

METRIC_KEYWORDS = {
    "extraction": [
        "extraction", "extracted", "withdrawal", "pumping", "usage", "consumption",
        # Hindi
        "दोहन", "निकासी", "निकाला", "उपयोग", "खपत",
        # Hinglish
        "dohan", "nikasi", "nikasi", "upayog", "khapat",
    ],
    "recharge": [
        "recharge", "recharged", "infiltration",
        # Hindi
        "रिचार्ज", "पुनर्भरण", "संग्रह",
        # Hinglish
        "recharge", "punarbharan", "sangrah",
    ],
    "stage": [
        "stage", "extraction stage", "extraction percentage", "extraction rate",
        # Hindi
        "चरण", "दर", "प्रतिशत",
        # Hinglish
        "charan", "dar", "pratishat",
    ],
    "resource": [
        "resource", "available", "potential", "reserve",
        # Hindi
        "संसाधन", "उपलब्ध", "संभावित", "भंडार",
        # Hinglish
        "sansadhan", "uplabdh", "sambhavit", "bhandar",
    ],
    "ph": ["ph", "acidity", "alkalinity", "अम्लता", "क्षारीयता"],
    "turbidity": [
        "turbidity", "turbid", "clarity", "suspended",
        # Hindi
        "अस्पष्टता", "मटमैला", "स्पष्टता",
        # Hinglish
        "aspashtata", "matmaila",
    ],
    "rainfall": [
        "rainfall", "rain", "precipitation", "monsoon",
        # Hindi
        "वर्षा", "बारिश", "मानसून",
        # Hinglish
        "varsha", "barish", "monsoon",
    ],
}

CATEGORY_KEYWORDS = {
    "Safe": ["safe", "सुरक्षित", "surakshit"],
    "Semi-Critical": [
        "semi-critical", "semi critical", "semicritical",
        "अर्ध-गंभीर", "अर्ध गंभीर",
    ],
    "Critical": [
        "critical", "stressed", "stress",
        "गंभीर", "तनाव",
        "gambhir",
    ],
    "Over-Exploited": [
        "over-exploited", "over exploited", "overexploited", "depleted",
        "अत्यधिक दोहन", "अति दोहन", "सूखा",
        "ati dohan", "atidohan",
    ],
}

# ─── Hinglish Intent Keywords ────────────────────────────────────────────────

HINGLISH_INTENT_KEYWORDS = {
    "compare": [
        "compare", "tulna", "tulanā", "banaam", "vs", "versus",
        "बनाम", "तुलना",
    ],
    "what_changed": [
        "what changed", "what's changed", "change", "changes", "difference",
        "diff", "kya badla", "kya badla", "badlaav", "badlav",
        "क्या बदला", "बदलाव", "परिवर्तन",
    ],
    "top_extraction": [
        "highest", "top", "most", "maximum", "largest", "biggest",
        "sabse", "sabsē", "zyada", "jyada", "ज्यादा", "सबसे",
        "sabse jyada", "sabse zyada", "सबसे ज्यादा", "सबसे ज़्यादा",
    ],
    "category": [
        "category", "distribution", "breakdown",
        "vargīkaran", "vargikaran", "वर्गीकरण",
    ],
    "critical_areas": [
        "over-exploited", "over exploited", "overexploited", "depleted",
        "critical", "stressed",
        "gambhir", "गंभीर", "khatre", "खतरे", "संकट",
    ],
    "trend": [
        "trend", "over time", "historical", "history", "change over",
        "rujhan", "rujhān", "pravritti", "रुझान", "प्रवृत्ति",
        "samay ke saath", "समय के साथ",
    ],
    "location": [
        "districts", "blocks", "regions", "areas", "locations",
        "zile", "jile", "blocks", "kshetra", "इलाके",
        "जिले", "ब्लॉक", "क्षेत्र",
        "zila", "jila", "जिला",
    ],
    "status": [
        "status", "overview", "summary", "how is", "what is",
        "tell me about", "describe", "kya hai", "kaisa hai",
        "kaisā hai", "kya hal hai", "status",
        "क्या है", "कैसा है", "हाल", "बताओ",
        "sthitisthiti", "sthiti", "स्थिति", "स्थितिस्थिति",
    ],
    "greeting": [
        "hello", "hi", "hey", "help", "start", "namaste", "नमस्ते",
    ],
}

# ─── Hinglish state aliases (romanized) ──────────────────────────────────────

HINGLISH_STATE_ALIASES = {
    "rajasthan": "Rajasthan",
    "gujarat": "Gujarat",
    "maharashtra": "Maharashtra",
    "punjab": "Punjab",
    "karnataka": "Karnataka",
    "up": "Uttar Pradesh",
    "uttar pradesh": "Uttar Pradesh",
    "tamil nadu": "Tamil Nadu",
    "tamilnadu": "Tamil Nadu",
    "west bengal": "West Bengal",
    "bengal": "West Bengal",
    "bangalore": "Karnataka",
    "bengaluru": "Karnataka",
}


# ─── Language Detection ──────────────────────────────────────────────────────

def _has_devanagari(text: str) -> bool:
    """Check if text contains Devanagari script characters."""
    return bool(re.search(r'[\u0900-\u097F]', text))


def _has_hinglish_markers(text: str) -> bool:
    """Check for common Hinglish markers that distinguish from English."""
    markers = [
        r'\bka\b', r'\bki\b', r'\bke\b', r'\bmein\b', r'\bhai\b',
        r'\bkya\b', r'\bkaisa\b', r'\bbatao\b', r'\bbataiye\b',
        r'\bsabse\b', r'\bzyada\b', r'\bjyada\b', r'\bthoda\b',
        r'\bbolo\b', r'\bho\b', r'\bchahiye\b', r'\bvala\b', r'\bwala\b',
    ]
    text_lower = text.lower()
    for pattern in markers:
        if re.search(pattern, text_lower):
            return True
    return False


def detect_language(message: str) -> str:
    """
    Detect the language of the message.
    Returns: 'hindi', 'hinglish', or 'english'
    """
    if _has_devanagari(message):
        return "hindi"
    if _has_hinglish_markers(message):
        return "hinglish"
    return "english"


# ─── Hindi/Hinglish-aware State Extraction ───────────────────────────────────

def extract_state(msg: str) -> Optional[str]:
    """Extract a known Indian state from the message (supports Hindi/Hinglish)."""
    msg_lower = msg.lower()

    # Check all aliases — use word boundary matching to avoid false positives
    for alias in sorted(STATE_ALIASES.keys(), key=len, reverse=True):
        if re.search(r'\b' + re.escape(alias) + r'\b', msg_lower):
            return STATE_ALIASES[alias]

    # Check canonical names
    for s in KNOWN_STATES:
        if s.lower() in msg_lower:
            return s

    return None


def extract_district(msg: str, known_districts: Optional[List[str]] = None) -> Optional[str]:
    """Extract a district name if present in the message."""
    if not known_districts:
        return None
    msg_lower = msg.lower()
    for d in sorted(known_districts, key=len, reverse=True):
        if d.lower() in msg_lower:
            return d
    return None


def extract_block(msg: str, known_blocks: Optional[List[str]] = None) -> Optional[str]:
    """Extract a block name if present in the message."""
    if not known_blocks:
        return None
    msg_lower = msg.lower()
    for b in sorted(known_blocks, key=len, reverse=True):
        if b.lower() in msg_lower:
            return b
    return None


def extract_years(msg: str) -> List[int]:
    """Extract all valid assessment years (2020-2025) from the message."""
    years = re.findall(r'\b(20[0-2]\d)\b', msg)
    return sorted(set(int(y) for y in years if 2020 <= int(y) <= 2025))


def extract_comparison_years(msg: str) -> List[int]:
    """Extract exactly two years for comparison queries."""
    years = extract_years(msg)
    if len(years) >= 2:
        return years[:2]
    return years


def extract_metric(msg: str) -> Optional[str]:
    """Extract which metric the user is asking about (supports Hindi/Hinglish)."""
    msg_lower = msg.lower()
    for metric, keywords in METRIC_KEYWORDS.items():
        for kw in keywords:
            if kw in msg_lower:
                return metric
    return None


def extract_category(msg: str) -> Optional[str]:
    """Extract a groundwater category (supports Hindi/Hinglish)."""
    msg_lower = msg.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', msg_lower):
                return cat
    return None


def detect_intent_type(msg: str) -> str:
    """Classify the user's intent into a query type (supports Hindi/Hinglish)."""
    msg_lower = msg.lower()
    language = detect_language(msg)

    # For Hindi/Devanagari, use substring matching (no word boundaries for Devanagari)
    if language == "hindi":
        if any(kw in msg for kw in ["तुलना", "बनाम", "tulna", "banaam"]):
            return "compare"
        if any(kw in msg for kw in ["बदला", "बदलाव", "परिवर्तन", "badlaav", "badlav"]):
            return "what_changed"
        if any(kw in msg for kw in ["सबसे", "ज्यादा", "ज़्यादा", "sabse", "zyada", "jyada"]):
            return "top_extraction"
        if any(kw in msg for kw in ["गंभीर", "संकट", "अत्यधिक दोहन", "अति दोहन", "gambhir"]):
            return "critical_areas"
        if any(kw in msg for kw in ["वर्गीकरण", "वितरण", "vargikaran", "distribution"]):
            return "category"
        if any(kw in msg for kw in ["प्रवृत्ति", "रुझान", "rujhan", "pravritti", "समय के साथ"]):
            return "trend"
        if any(kw in msg for kw in ["जिले", "जिला", "ब्लॉक", "क्षेत्र", "zile", "jile"]):
            return "location"
        if any(kw in msg for kw in ["क्या है", "कैसा है", "हाल", "बताओ", "स्थिति", "स्थितिस्थिति", "kya hai", "kaisa hai", "batao", "sthiti"]):
            return "status"
        if any(kw in msg for kw in ["नमस्ते", "namaste"]):
            return "greeting"
        return "general"

    # For Hinglish/English, use word boundary matching
    for intent_type, keywords in HINGLISH_INTENT_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', msg_lower):
                return intent_type

    # Fallback to English-only patterns
    if re.search(r'\b(compare|comparison|between|vs|versus)\b', msg_lower):
        return "compare"
    if re.search(r'\b(highest|top|most|maximum|largest|biggest)\b', msg_lower):
        return "top_extraction"
    if re.search(r'\b(over.?exploited|depleted)\b', msg_lower):
        return "critical_areas"
    if re.search(r'\b(category|distribution|breakdown|safe|semi.?critical)\b', msg_lower):
        return "category"
    if re.search(r'\b(critical|stressed)\b', msg_lower) and not re.search(r'\b(status|what is|overview)\b', msg_lower):
        return "critical_areas"
    if re.search(r'\b(trend|over time|historical|history|change over)\b', msg_lower):
        return "trend"
    if re.search(r'\b(districts?|blocks?|regions?|areas?|locations?)\b', msg_lower):
        return "location"
    if re.search(r'\b(status|overview|summary|how is|what is|tell me about|describe)\b', msg_lower):
        return "status"
    if re.search(r'\b(hello|hi|hey|help|start)\b', msg_lower):
        return "greeting"
    return "general"


def parse_message(
    message: str,
    known_districts: Optional[List[str]] = None,
    known_blocks: Optional[List[str]] = None,
) -> ChatIntent:
    """
    Parse a natural language message into a structured ChatIntent.

    This is the main entry point. It extracts:
    - intent:        query type (status, compare, top_extraction, etc.)
    - state:         Indian state name
    - district:      district name (if in known_districts)
    - block:         block name (if in known_blocks)
    - year:          single assessment year
    - comparison_years: [year1, year2] for compare queries
    - metric:        which metric (extraction, recharge, stage, etc.)
    - category:      groundwater category (Safe, Critical, etc.)
    - confidence:    0.0–1.0 parsing confidence score
    """
    msg = message.strip()
    msg_lower = msg.lower()

    language = detect_language(msg)
    intent = detect_intent_type(msg)
    state = extract_state(msg)
    district = extract_district(msg, known_districts)
    block = extract_block(msg, known_blocks)
    years = extract_years(msg)
    comparison_years = extract_comparison_years(msg) if intent in ("compare", "what_changed") else []
    metric = extract_metric(msg)
    category = extract_category(msg)

    # Single year extraction (for non-comparison queries)
    year = years[0] if years and intent != "compare" else None

    # Calculate confidence based on how many fields were extracted
    fields_extracted = sum([
        intent != "general",
        state is not None,
        district is not None,
        block is not None,
        year is not None or len(comparison_years) > 0,
        metric is not None,
        category is not None,
    ])
    confidence = round(min(fields_extracted / 4.0, 1.0), 2)

    return ChatIntent(
        intent=intent,
        state=state,
        district=district,
        block=block,
        year=year,
        comparison_years=comparison_years,
        metric=metric,
        category=category,
        confidence=confidence,
        language=language,
        raw_message=msg,
    )
