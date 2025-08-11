import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TestRunner:
    name: str
    command: str


def _has_file(repo_root: str, relative: str) -> bool:
    return (Path(repo_root) / relative).exists()


def _load_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def detect_test_runner(repo_root: str) -> Optional[TestRunner]:
    # Node / npm / pnpm / yarn
    package_json_path = Path(repo_root) / "package.json"
    if package_json_path.exists():
        pkg = _load_json(package_json_path)
        if pkg and isinstance(pkg.get("scripts"), dict) and "test" in pkg["scripts"]:
            # Prefer pnpm > npm > yarn if lockfiles present
            if _has_file(repo_root, "pnpm-lock.yaml"):
                return TestRunner(name="pnpm", command="pnpm test --reporter=dot")
            if _has_file(repo_root, "package-lock.json"):
                return TestRunner(name="npm", command="npm test --silent")
            if _has_file(repo_root, "yarn.lock"):
                return TestRunner(name="yarn", command="yarn test")
            return TestRunner(name="npm", command="npm test --silent")

    # Python / pytest
    if _has_file(repo_root, "pytest.ini") or _has_file(repo_root, "pyproject.toml") or _has_file(repo_root, "tests"):
        return TestRunner(name="pytest", command="pytest -q")

    # Go
    if _has_file(repo_root, "go.mod"):
        return TestRunner(name="go", command="go test ./...")

    # Maven
    if _has_file(repo_root, "pom.xml"):
        return TestRunner(name="maven", command="mvn -q -DskipITs=false test")

    # Gradle
    if _has_file(repo_root, "build.gradle") or _has_file(repo_root, "build.gradle.kts"):
        return TestRunner(name="gradle", command="./gradlew test") if _has_file(repo_root, "gradlew") else TestRunner(name="gradle", command="gradle test")

    return None