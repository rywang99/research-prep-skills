# Extension Guide

Use this guide when adding a new research mode, output section, source type, or storage behavior.

## Add a research mode

1. Create `.agents/skills/research-<mode>/SKILL.md` and `agents/openai.yaml`.
2. Add the mode to `auto-research-common/config/research_modes.json` under `modes`:
   - `label`: Chinese report label.
   - `skill`: skill directory name.
   - `default_window_days`: default rolling window.
   - `description`: short human-readable purpose.
3. Update `.agents/skills/auto-research/SKILL.md` routing keywords if the mode should be inferred automatically.
4. Add at least one prompt example to `PROMPTS.md` if the mode is user-facing.
5. Run `python3 scripts/validate_skills.py`.

## Add a report section

Prefer using the generic `sections` array in `report_schema.md`. Only change the renderer when the section needs a distinct layout, such as a timeline, heatmap, or scorecard.

When adding a rendered section:

1. Add a `render_<section>()` function to `render_report.py`.
2. Add its nav entry to `config/research_modes.json` if it should appear in the sidebar.
3. Document the JSON field in `report_schema.md`.
4. Add fixture data to `examples/minimal_report.json` or a new example.

## Add a source type or confidence label

- Add display labels to `config/research_modes.json` under `source_types`.
- Keep CSS badge classes generic; unknown types still render safely.
- Do not remove existing source types without migration because old `knowledge_base/*/sources.jsonl` entries may use them.

## Add a source collector

1. Add a provider function to `scripts/collect_sources.py` that returns normalized source records.
2. Register it in the script's collector map and expose it through `--sources`.
3. Keep the output compatible with `report_schema.md` source fields; add provenance fields only when they are safe to ignore.
4. Add or update `examples/collected_sources.jsonl` so `scripts/validate_skills.py` can test the mapping without network access.

## Storage compatibility

Knowledge-base files are append-friendly and should remain backward compatible:

- `sources.jsonl`: append source records; never rewrite historical rows unless repairing invalid JSON.
- `runs.jsonl`: append one run summary per rendered report.
- `keywords.json`: latest keyword snapshot for quick reuse.

If a future migration is required, write a new script under `scripts/` and keep old files readable.
