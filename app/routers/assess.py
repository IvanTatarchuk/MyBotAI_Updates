from fastapi import APIRouter

from ..models import AssessmentRequest, AssessmentResult
from ..services.assessor import assess as run_assessment
from ..services.llm_adapter import llm


router = APIRouter(prefix="/assess")


@router.post("", response_model=AssessmentResult)
def assess_endpoint(payload: AssessmentRequest) -> AssessmentResult:
    result = run_assessment(payload)
    # Generate a short LLM-based summary (stubbed)
    result.summary = llm.summarize(result.summary)
    return result

