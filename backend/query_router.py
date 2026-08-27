"""
Query Router for Groundwater Intelligence.
Classifies user intent and routes to appropriate backend pipeline.
"""

import re
from typing import Dict, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass


class QueryType(Enum):
    STATE_STATUS = "state_status"
    DISTRICT_STATUS = "district_status"
    BLOCK_STATUS = "block_status"
    COMPARISON = "comparison"
    RANKING = "ranking"
    TREND = "trend"
    QUALITY = "quality"
    LEVEL = "level"
    EXTRACTION = "extraction"
    RECHARGE = "recharge"
    CATEGORY = "category"
    RECOMMENDATION = "recommendation"
    REGULATORY = "regulatory"
    SPATIAL = "spatial"
    GENERAL = "general"
    GREETING = "greeting"


class QueryRoute(Enum):
    SQL_ONLY = "sql_only"
    RAG_ONLY = "rag_only"
    SQL_PLUS_RAG = "sql_plus_rag"
    LLM_DIRECT = "llm_direct"


@dataclass
class ClassifiedQuery:
    query_type: QueryType
    route: QueryRoute
    entities: Dict[str, Optional[str]]
    metrics: List[str]
    confidence: float
    needs_calculation: bool
    needs_explanation: bool


# ─── Intent Patterns ──────────────────────────────────────────────────────

COMPARISON_PATTERNS = [
    r"compare\s+(\w+)\s+(?:and|vs|versus|with)\s+(\w+)",
    r"difference\s+between\s+(\w+)\s+and\s+(\w+)",
    r"(\w+)\s+(?:vs|versus)\s+(\w+)",
    r"की\s+तुलना\s+.*\s+(?:और|से)\s+",
    r"कौन\s+(?:बेहतर|ज्यादा|कम)\s+है",
]

RANKING_PATTERNS = [
    r"(?:top|highest|most|maximum|worst|lowest|minimum)\s+\d*\s*(?:state|district|block|region)",
    r"(?:which|what)\s+(?:states?|districts?|blocks?)\s+(?:have|has)\s+(?:the\s+)?(?:highest|most|lowest|worst)",
    r"(?:rank|ranking|list)\s+(?:states?|districts?|blocks?)",
    r"सबसे\s+(?:ज्यादा|कम|अधिक|कम)",
]

TREND_PATTERNS = [
    r"(?:trend|over\s+time|historical|change|pattern|since|from\s+\d{4})",
    r"(?:how\s+has|how\s+did|what\s+happened)",
    r"प्रवृत्ति|बदलाव|इतिहास",
]

QUALITY_PATTERNS = [
    r"(?:quality|contamin|fluoride|arsenic|nitrate|iron|tds|ph|salinity|uranium)",
    r"(?:गुणवत्ता|संदूषण|फ्लोराइड|आर्सेनिक)",
]

LEVEL_PATTERNS = [
    r"(?:water\s+level|groundwater\s+level|depth|tube\s+well\s+level)",
    r"जलस्तर|भूजल\s+स्तर",
]

EXTRACTION_PATTERNS = [
    r"(?:extraction|extract|withdraw|pump|usage|consumption)",
    r"निकासी|दोहन|उपयोग",
]

RECHARGE_PATTERNS = [
    r"(?:recharge|replenish|infiltrat)",
    r"रिचार्ज|पुनर्भरण",
]

CATEGORY_PATTERNS = [
    r"(?:safe|semi.?critical|critical|over.?exploited|saline|category|categoriz)",
    r"(?:वर्गीकरण|श्रेणी|सुरक्षित|गंभीर)",
]

RECOMMENDATION_PATTERNS = [
    r"(?:recommend|suggest|solution|measure|action|manage|policy|intervene)",
    r"(?:सुझाव|समाधान|उपाय|प्रबंधन)",
]

REGULATORY_PATTERNS = [
    r"(?:regulation|rule|law|act|policy|noc|permit|license|guideline)",
    r"(?:नियम|कानून|नीति|अनुमति)",
]


def classify_query(query: str, entities: Dict[str, Optional[str]]) -> ClassifiedQuery:
    """Classify a user query into type and route."""
    lower_q = query.lower().strip()

    # Greeting
    if re.match(r"^(hi|hello|hey|namaste|नमस्ते|नमस्कार|good\s+(morning|afternoon|evening))", lower_q):
        return ClassifiedQuery(
            query_type=QueryType.GREETING, route=QueryRoute.LLM_DIRECT,
            entities=entities, metrics=[], confidence=0.9,
            needs_calculation=False, needs_explanation=False
        )

    # Check patterns in priority order
    for pattern in COMPARISON_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.COMPARISON, route=QueryRoute.SQL_PLUS_RAG,
                entities=entities, metrics=["extraction_stage", "groundwater_extraction", "annual_groundwater_recharge"],
                confidence=0.85, needs_calculation=True, needs_explanation=True
            )

    for pattern in RANKING_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.RANKING, route=QueryRoute.SQL_ONLY,
                entities=entities, metrics=["extraction_stage"],
                confidence=0.85, needs_calculation=True, needs_explanation=True
            )

    for pattern in TREND_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.TREND, route=QueryRoute.SQL_PLUS_RAG,
                entities=entities, metrics=["extraction_stage", "groundwater_extraction"],
                confidence=0.8, needs_calculation=True, needs_explanation=True
            )

    for pattern in QUALITY_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.QUALITY, route=QueryRoute.SQL_PLUS_RAG,
                entities=entities, metrics=["fluoride", "arsenic", "nitrate"],
                confidence=0.8, needs_calculation=False, needs_explanation=True
            )

    for pattern in LEVEL_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.LEVEL, route=QueryRoute.SQL_PLUS_RAG,
                entities=entities, metrics=["water_level"],
                confidence=0.8, needs_calculation=False, needs_explanation=True
            )

    for pattern in EXTRACTION_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.EXTRACTION, route=QueryRoute.SQL_PLUS_RAG,
                entities=entities, metrics=["groundwater_extraction", "extraction_stage"],
                confidence=0.8, needs_calculation=False, needs_explanation=True
            )

    for pattern in RECHARGE_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.RECHARGE, route=QueryRoute.SQL_PLUS_RAG,
                entities=entities, metrics=["annual_groundwater_recharge"],
                confidence=0.8, needs_calculation=False, needs_explanation=True
            )

    for pattern in CATEGORY_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.CATEGORY, route=QueryRoute.SQL_ONLY,
                entities=entities, metrics=["category"],
                confidence=0.8, needs_calculation=True, needs_explanation=True
            )

    for pattern in RECOMMENDATION_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.RECOMMENDATION, route=QueryRoute.RAG_ONLY,
                entities=entities, metrics=[],
                confidence=0.75, needs_calculation=False, needs_explanation=True
            )

    for pattern in REGULATORY_PATTERNS:
        if re.search(pattern, lower_q):
            return ClassifiedQuery(
                query_type=QueryType.REGULATORY, route=QueryRoute.RAG_ONLY,
                entities=entities, metrics=[],
                confidence=0.75, needs_calculation=False, needs_explanation=True
            )

    # Default: state/district status or general
    if entities.get("state"):
        return ClassifiedQuery(
            query_type=QueryType.STATE_STATUS, route=QueryRoute.SQL_PLUS_RAG,
            entities=entities, metrics=["extraction_stage", "groundwater_extraction", "annual_groundwater_recharge"],
            confidence=0.8, needs_calculation=True, needs_explanation=True
        )

    if entities.get("district"):
        return ClassifiedQuery(
            query_type=QueryType.DISTRICT_STATUS, route=QueryRoute.SQL_PLUS_RAG,
            entities=entities, metrics=["extraction_stage", "groundwater_extraction"],
            confidence=0.75, needs_calculation=True, needs_explanation=True
        )

    return ClassifiedQuery(
        query_type=QueryType.GENERAL, route=QueryRoute.SQL_PLUS_RAG,
        entities=entities, metrics=[],
        confidence=0.6, needs_calculation=False, needs_explanation=True
    )
