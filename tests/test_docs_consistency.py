"""The docs must agree on the phase plan recorded in ADR 0004.

Phase 1 is built on the Spotify Web API. The export is a phase 2 backfill. These tests fail
if a doc, a diagram or the env template drifts back to the old order.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PHASE_1 = "docs/phases/phase-1-local-mvp.md"
PHASE_2 = "docs/phases/phase-2-automated-cloud.md"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Body under a markdown heading, up to the next heading of the same or a higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    body: list[str] = []
    inside = False
    in_code = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not inside:
            inside = not in_code and line.strip() == heading
            continue
        # A "# comment" inside a code block is not a heading.
        match = None if in_code else re.match(r"(#+) ", line)
        if match and len(match.group(1)) <= level:
            break
        body.append(line)
    assert inside, f"heading not found: {heading}"
    return "\n".join(body)


def _table_row(text: str, first_cell: str) -> list[str]:
    """Cells of the markdown table row whose first cell is `first_cell`."""
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == first_cell:
            return cells
    raise AssertionError(f"table row not found: {first_cell}")


def _mermaid_dashed(text: str) -> dict[str, bool]:
    """Node id -> True when the node carries the phase 2 class, which must draw a dashed line."""
    block = re.search(r"```mermaid\n(.*?)```", text, re.DOTALL)
    assert block, "no mermaid diagram"
    assert re.search(r"classDef p2 .*stroke-dasharray", block.group(1)), "p2 is not dashed"
    nodes = re.findall(r'^\s*(\w+)\[\(?"[^"]*"\)?\](:::\w+)?', block.group(1), re.MULTILINE)
    return {node_id: css == ":::p2" for node_id, css in nodes}


def test_phase_1_is_built_on_the_api_and_leaves_the_export_out():
    spec = _read(PHASE_1)
    goal = next(line for line in spec.splitlines() if line.startswith("**Goal:**"))
    assert "from the Spotify Web API alone" in goal
    assert "on my laptop" in goal
    assert "export" not in goal.lower()

    scope = _section(spec, "## Scope")
    assert "`raw.plays_api`" in scope
    assert re.search(r"launchd runs .* hourly", scope)
    assert "export" not in scope.lower()

    out_of_scope = _section(spec, "## Out of scope").splitlines()
    assert any(line.startswith("- The export") and "phase 2" in line for line in out_of_scope)


def test_phase_1_done_when_needs_no_history_before_the_first_sync():
    done_when = _section(_read(PHASE_1), "## Done when")
    assert "2022" not in done_when
    assert "export" not in done_when.lower()
    assert "fake API data" in done_when


def test_phase_2_holds_the_export_backfill_and_june_2022():
    spec = _read(PHASE_2)
    scope = _section(spec, "## Scope")
    assert "`raw.plays_export`" in scope
    assert "unions export and API" in scope
    assert "export wins" in scope
    # The sync is built in phase 1. Phase 2 only moves it off the laptop.
    assert "`raw.plays_api`" not in scope

    assert "June 2022" in _section(spec, "## Done when")


def test_docs_agree_on_which_source_belongs_to_which_phase():
    readme = _read("README.md")
    roadmap = _section(readme, "## Roadmap")
    phase_1_scope = _table_row(roadmap, "1. Local MVP")[1]
    assert "API" in phase_1_scope
    assert "export" not in phase_1_scope.lower()
    phase_2_row = next(line for line in roadmap.splitlines() if line.startswith("| 2."))
    assert "export backfill" in phase_2_row

    assert "Phase 1 is API-first" in _read("CLAUDE.md")

    sources_row = _table_row(_read("docs/architecture.md"), "Sources")
    assert sources_row[1] == "API"
    assert "export" in sources_row[2]

    phase_1_models = _section(_read("docs/data-model.md"), "## Phase 1 models")
    model_rows = [line for line in phase_1_models.splitlines() if line.startswith("|")]
    assert any("`raw.plays_api`" in row for row in model_rows)
    assert not any("plays_export" in row for row in model_rows)

    sources = _read("docs/data-sources.md")
    headings = [line for line in sources.splitlines() if line.startswith("## ")]
    api_heading = next(line for line in headings if "Web API" in line)
    export_heading = next(line for line in headings if "export" in line)
    assert "phase 1" in api_heading
    assert "phase 2" in export_heading


def test_no_doc_still_carries_the_export_first_wording():
    # Phrases the export-first plan used. The ADRs are left out: they describe the old plan.
    stale = [
        r"from the (Spotify )?export alone",
        r"export only",
        r"fake export",
        r"recently played \(phase 2\)",
        r"phase 2 sync",
        r"hourly sync \(phase 2\)",
        r"API sync in phase 2",
    ]
    paths = [
        ROOT / "README.md",
        ROOT / "CLAUDE.md",
        ROOT / "dashboard" / "README.md",
        ROOT / "docs" / "architecture.excalidraw",
        *sorted((ROOT / "docs").rglob("*.md")),
    ]
    checked = [path for path in paths if "adr" not in path.parts]
    assert len(checked) > 8
    for path in checked:
        text = path.read_text(encoding="utf-8")
        for pattern in stale:
            assert not re.search(pattern, text, re.IGNORECASE), f"{path.name}: {pattern}"


def test_diagrams_draw_the_api_solid_and_the_export_dashed():
    for path in ("README.md", "docs/architecture.md"):
        dashed = _mermaid_dashed(_read(path))
        assert dashed["API"] is False, path
        assert dashed["SYNC"] is False, path
        assert dashed["EXP"] is True, path
        assert dashed["LOAD"] is True, path

    elements = json.loads(_read("docs/architecture.excalidraw"))["elements"]
    by_id = {element["id"]: element for element in elements}
    expected = {
        "Spotify Web API": "solid",
        "sync_recently_played.py": "solid",
        "Spotify export": "dashed",
        "load_export.py": "dashed",
    }
    style_of_box: dict[str, str] = {}
    for label, style in expected.items():
        text = next(
            element
            for element in elements
            if element["type"] == "text" and element["text"].startswith(label)
        )
        box = by_id[text["containerId"]]
        assert box["strokeStyle"] == style, label
        style_of_box[box["id"]] = style

    # An arrow leaving one of those boxes is drawn the same way as the box.
    arrows = [
        element
        for element in elements
        if element["type"] == "arrow"
        and (element.get("startBinding") or {}).get("elementId") in style_of_box
    ]
    assert len(arrows) == len(expected)
    for arrow in arrows:
        assert arrow["strokeStyle"] == style_of_box[arrow["startBinding"]["elementId"]]


def test_adr_0004_records_the_decision_and_adr_0003_points_to_it():
    adr = _read("docs/adr/0004-api-first-mvp.md")
    assert "**Status:** accepted" in adr
    decision = _section(adr, "## Decision")
    assert "API" in decision
    assert "phase 2" in decision
    assert _section(adr, "## Alternatives considered").strip()
    assert _section(adr, "## Consequences").strip()

    adr_0003 = _read("docs/adr/0003-full-refresh-export-loader.md")
    note = next(line for line in adr_0003.splitlines() if line.startswith("- **Note:**"))
    assert "0004-api-first-mvp.md" in note
    assert "moved from phase 1 to phase 2" in note

    assert "docs/adr/0004-api-first-mvp.md" in _section(_read("README.md"), "## Key decisions")


def test_env_example_puts_spotify_in_phase_1_and_the_export_in_phase_2():
    phase_1, marker, phase_2 = _read(".env.example").partition("# Phase 2")
    assert marker, "no '# Phase 2' section"

    active = dict(
        line.split("=", 1)
        for line in phase_1.splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    )
    secrets = ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REFRESH_TOKEN")
    for key in secrets:
        assert key in active
        assert active[key] == "", f"{key} must be empty in the template"
    assert "EXPORT_GLOB" not in active
    assert "EXPORT_GLOB" in phase_2


def test_docs_state_the_spotify_limits_checked_on_2026_11_25():
    sources = _read("docs/data-sources.md")
    api = sources[sources.index("## Spotify Web API") : sources.index("## Spotify extended")]
    assert "last 50 plays" in api
    assert "`user-read-recently-played`" in api
    assert "doesn't return podcast" in api
    assert "needs Spotify Premium" in api
    assert "refresh token lasts 6 months" in api
    assert "`http://127.0.0.1:<port>`" in api
    assert "`localhost` is rejected" in api

    runbook = _read("docs/runbooks/spotify-api-setup.md")
    assert "Premium" in runbook
    assert "6 months" in runbook
    assert "`user-read-recently-played`" in runbook
    assert "`http://127.0.0.1:8888/callback`" in runbook

    redirect = re.search(r"^SPOTIFY_REDIRECT_URI=(.*)$", _read(".env.example"), re.MULTILINE)
    assert redirect and redirect.group(1) == "http://127.0.0.1:8888/callback"
