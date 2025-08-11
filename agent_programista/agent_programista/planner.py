from typing import List, Optional

from .executor import PlanStep
from .detectors import TestRunner


def generate_plan(task_description: str, repo_root: str, test_runner: Optional[TestRunner]) -> List[PlanStep]:
    steps: List[PlanStep] = []

    normalized = task_description.lower()

    # Always start with an initial test run if runner exists
    if test_runner is not None:
        steps.append(PlanStep(kind="test", description="Uruchom testy bazowe", command=test_runner.command))

    # Heuristics
    if any(keyword in normalized for keyword in ["test", "napraw", "fix", "bug", "błąd"]):
        steps.append(PlanStep(kind="search", description="Szukaj TODO/FIXME", payload={"query": "TODO|FIXME"}))

    if any(keyword in normalized for keyword in ["zależno", "dependency", "update", "upgrade"]):
        # Try common package managers
        steps.append(PlanStep(kind="shell", description="Aktualizacja pakietów npm/pnpm/yarn (jeśli dotyczy)", command="[ -f package.json ] && ( [ -f pnpm-lock.yaml ] && pnpm up || [ -f package-lock.json ] && npm update || [ -f yarn.lock ] && yarn upgrade ) || true"))
        steps.append(PlanStep(kind="shell", description="Aktualizacja pakietów Python (jeśli dotyczy)", command="[ -f requirements.txt ] && pip install -U -r requirements.txt || true"))

    # Second test run to see effects
    if test_runner is not None:
        steps.append(PlanStep(kind="test", description="Uruchom testy po zmianach", command=test_runner.command))

    # Final commit step
    steps.append(PlanStep(kind="git_commit", description="Commit zmian", payload={"message": f"agent: {task_description}"}))

    return steps