"""
Backend Numerical Calculations for Groundwater Intelligence.
All calculations done here, NOT by the LLM.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class ComparisonResult:
    state_a: str
    state_b: str
    metric: str
    value_a: float
    value_b: float
    difference: float
    percentage_change: float
    unit: str
    year_a: int
    year_b: int
    a_higher: bool


@dataclass
class TrendPoint:
    year: int
    value: float


@dataclass
class TrendResult:
    location: str
    metric: str
    unit: str
    points: List[TrendPoint]
    direction: str  # "increasing", "decreasing", "stable"
    total_change: float
    percentage_change: float
    avg_annual_change: float


@dataclass
class RankingEntry:
    rank: int
    name: str
    value: float
    unit: str
    category: Optional[str] = None


def percentage_change(old: float, new: float) -> float:
    """Calculate percentage change. Returns 0 if old is 0."""
    if old == 0:
        return 0.0
    return round(((new - old) / old) * 100, 2)


def absolute_change(old: float, new: float) -> float:
    """Calculate absolute change."""
    return round(new - old, 2)


def compute_comparison(
    name_a: str, data_a: Dict[str, Any],
    name_b: str, data_b: Dict[str, Any],
    metric: str, unit: str
) -> Optional[ComparisonResult]:
    """Compute comparison between two entities for a given metric."""
    val_a = data_a.get(metric)
    val_b = data_b.get(metric)
    if val_a is None or val_b is None:
        return None
    val_a = float(val_a)
    val_b = float(val_b)
    diff = absolute_change(val_a, val_b)
    pct = percentage_change(val_a, val_b)
    year_a = data_a.get("assessment_year", 0)
    year_b = data_b.get("assessment_year", 0)
    return ComparisonResult(
        state_a=name_a, state_b=name_b, metric=metric,
        value_a=val_a, value_b=val_b, difference=diff,
        percentage_change=pct, unit=unit,
        year_a=year_a, year_b=year_b,
        a_higher=val_a > val_b
    )


def compute_state_comparison(
    state_a_data: Dict[str, Any], state_a_name: str,
    state_b_data: Dict[str, Any], state_b_name: str,
) -> Dict[str, Any]:
    """Full comparison between two states."""
    metrics = [
        ("annual_groundwater_recharge", "Annual Recharge", "MCM"),
        ("extractable_groundwater_resource", "Extractable Resource", "MCM"),
        ("groundwater_extraction", "Groundwater Extraction", "MCM"),
        ("extraction_stage", "Stage of Extraction", "%"),
    ]
    comparisons = []
    for metric, label, unit in metrics:
        comp = compute_comparison(
            state_a_name, state_a_data,
            state_b_name, state_b_data,
            metric, unit
        )
        if comp:
            comparisons.append({
                "metric": label,
                "unit": unit,
                state_a_name: comp.value_a,
                state_b_name: comp.value_b,
                "difference": comp.difference,
                "percentage_change": comp.percentage_change,
                "a_higher": comp.a_higher,
            })

    return {
        "state_a": state_a_name,
        "state_b": state_b_name,
        "comparisons": comparisons,
        "year_a": state_a_data.get("assessment_year"),
        "year_b": state_b_data.get("assessment_year"),
    }


def compute_trend(
    location: str, metric: str, unit: str,
    data_points: List[Dict[str, Any]]
) -> Optional[TrendResult]:
    """Compute trend from time-series data."""
    if len(data_points) < 2:
        return None

    sorted_pts = sorted(data_points, key=lambda x: x.get("assessment_year", 0))
    points = [TrendPoint(year=p["assessment_year"], value=float(p.get(metric, 0))) for p in sorted_pts]

    first_val = points[0].value
    last_val = points[-1].value
    total_change = absolute_change(first_val, last_val)
    pct_change = percentage_change(first_val, last_val)

    n_years = points[-1].year - points[0].year
    avg_annual = round(total_change / max(n_years, 1), 2)

    if pct_change > 5:
        direction = "increasing"
    elif pct_change < -5:
        direction = "decreasing"
    else:
        direction = "stable"

    return TrendResult(
        location=location, metric=metric, unit=unit,
        points=points, direction=direction,
        total_change=total_change, percentage_change=pct_change,
        avg_annual_change=avg_annual
    )


def compute_rankings(
    items: List[Dict[str, Any]],
    name_key: str, value_key: str, unit: str,
    limit: int = 10, ascending: bool = False
) -> List[RankingEntry]:
    """Compute rankings from a list of records."""
    valid = [(i.get(name_key, "Unknown"), float(i.get(value_key, 0))) for i in items if i.get(value_key) is not None]
    valid.sort(key=lambda x: x[1], reverse=not ascending)
    return [
        RankingEntry(rank=idx + 1, name=name, value=val, unit=unit)
        for idx, (name, val) in enumerate(valid[:limit])
    ]


def compute_category_distribution(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute category distribution from block records."""
    total = len(records)
    if total == 0:
        return {"total": 0, "categories": {}}

    cats = {"Safe": 0, "Semi-Critical": 0, "Critical": 0, "Over-Exploited": 0}
    for r in records:
        cat = r.get("category", "Safe")
        if cat in cats:
            cats[cat] += 1

    return {
        "total": total,
        "categories": {k: {"count": v, "percentage": round(v / total * 100, 1)} for k, v in cats.items()}
    }


def compute_risk_score(state_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute risk score 0-100 for a state."""
    score = 0
    factors = []

    # Extraction stage (0-40 points)
    stage = float(state_data.get("avg_extraction_stage", 0))
    if stage > 100:
        stage_pts = 40
    elif stage > 90:
        stage_pts = 35
    elif stage > 70:
        stage_pts = 25
    elif stage > 50:
        stage_pts = 15
    else:
        stage_pts = 5
    score += stage_pts
    if stage_pts > 20:
        factors.append(f"High extraction stage ({stage:.1f}%)")

    # Category distribution (0-30 points)
    oe_pct = float(state_data.get("over_exploited_pct", 0))
    crit_pct = float(state_data.get("critical_pct", 0))
    cat_pts = min(30, int(oe_pct * 0.4 + crit_pct * 0.6))
    score += cat_pts
    if cat_pts > 15:
        factors.append(f"Significant over-exploitation ({oe_pct:.1f}% blocks)")

    # Risk concentration (0-15 points)
    stressed = oe_pct + crit_pct
    risk_pts = min(15, int(stressed * 0.3))
    score += risk_pts
    if risk_pts > 8:
        factors.append(f"{stressed:.1f}% blocks in critical/over-exploited")

    # Historical trend (-15 to +15)
    trend = float(state_data.get("trend_delta", 0))
    if trend > 10:
        trend_pts = -10
        factors.append("Deteriorating trend")
    elif trend > 5:
        trend_pts = -5
    elif trend < -10:
        trend_pts = 10
        factors.append("Improving trend")
    elif trend < -5:
        trend_pts = 5
    else:
        trend_pts = 0
    score += trend_pts

    score = max(0, min(100, score))

    if score >= 76:
        level = "Critical"
    elif score >= 51:
        level = "High"
    elif score >= 26:
        level = "Medium"
    else:
        level = "Low"

    return {"score": score, "level": level, "factors": factors[:5]}


def format_number(value: float, unit: str = "") -> str:
    """Format a number for display."""
    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}M {unit}".strip()
    elif value >= 1_000:
        return f"{value/1_000:.1f}K {unit}".strip()
    elif value == int(value):
        return f"{int(value)} {unit}".strip()
    else:
        return f"{value:.2f} {unit}".strip()
