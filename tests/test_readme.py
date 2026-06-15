from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_workflow_does_not_depend_on_mermaid_rendering() -> None:
    for filename in ["README.md", "README.en.md"]:
        text = (ROOT / filename).read_text(encoding="utf-8")

        assert "```mermaid" not in text
        assert "No diagram type detected" not in text
