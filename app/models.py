from typing import List, Optional
from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
    title: str = Field(..., min_length=2)
    description: str = Field(..., min_length=10)
    target_customer: Optional[str] = None


class Idea(IdeaCreate):
    id: str


class AssessmentRequest(BaseModel):
    title: str
    description: str
    market_size_estimate: Optional[float] = None  # USD


class PricingTier(BaseModel):
    name: str
    price_per_month: float
    notes: Optional[str] = None


class AssessmentResult(BaseModel):
    score: int  # 0-100
    summary: str
    suggested_pricing: List[PricingTier] = []

