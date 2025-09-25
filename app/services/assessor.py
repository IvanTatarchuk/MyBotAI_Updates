from typing import List

from ..models import AssessmentRequest, AssessmentResult, PricingTier


def _heuristic_score(req: AssessmentRequest) -> int:
    score = 50

    description = (req.description or "").lower()
    title = (req.title or "").lower()

    keywords = [
        "compliance",
        "automation",
        "copilot",
        "enterprise",
        "security",
        "governance",
        "ai",
        "api",
        "platform",
    ]
    for word in keywords:
        if word in description or word in title:
            score += 4

    if req.market_size_estimate:
        if req.market_size_estimate > 5_000_000_000:
            score += 15
        elif req.market_size_estimate > 1_000_000_000:
            score += 10
        elif req.market_size_estimate > 100_000_000:
            score += 5

    return max(0, min(100, score))


def _suggest_pricing(score: int) -> List[PricingTier]:
    if score >= 80:
        base = 299
    elif score >= 65:
        base = 199
    else:
        base = 99

    tiers = [
        PricingTier(name="Starter", price_per_month=float(base), notes="Solo or early teams"),
        PricingTier(name="Team", price_per_month=float(base * 1.8), notes="Growing teams"),
        PricingTier(name="Pro", price_per_month=float(base * 3.5), notes="Studios & enterprise"),
    ]
    return tiers


def assess(req: AssessmentRequest) -> AssessmentResult:
    score = _heuristic_score(req)
    summary = (
        f"Idea '{req.title}' shows a score of {score}/100 based on heuristic signals. "
        "Consider focusing on a high-urgency buyer, clear ROI narrative, and early lighthouse accounts."
    )
    pricing = _suggest_pricing(score)
    return AssessmentResult(score=score, summary=summary, suggested_pricing=pricing)

