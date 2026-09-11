# Resume editing contract

This is Sachin Gupta's YAML-based resume workspace. Use data/resume.yaml as the shared resume source, variants/*.yaml for role presets and variants/companies/<company>-<role>.yaml for company targets. Preserve archive/original-2026-09-11.tex verbatim. The repository is public: never import private profile notes, credentials or employer-internal documents.

For a requested company resume, create a new variant extending the closest role preset; do not overwrite another company's variant. Use existing facts only. Preserve qualifiers, metrics, contribution scope and dates. Unsupported additions require user input. Existing resume text is user-reported evidence, not permission to embellish it. No application submission or external messages are part of an edit.

Prefer shared YAML edits for global corrections and field overrides for target-specific wording. Lists replace lists; mapping overrides merge recursively. Review company overrides affected by a base correction. Do not edit generated PDFs or the previews branch manually. Do not change the template unless layout changes are needed.

Before finishing: uv sync --locked; uv run python -m unittest discover -s tests -v; uv run python -m resume_ci_automation --all. Inspect the affected PNGs for fit, overlap and legibility. All PDFs must be one page with readable text. Commit requested source changes and verify the GitHub Actions build and publish jobs plus the source-commit-matched preview. If publishing is blocked, preserve local work and report the exact remaining action; do not claim the GitHub workflow is working from a local build alone.

Record which facts/wording changed, variant ID, source commit and preview link. Keep actual application usage in the user's existing private tracker. No automatic synchronization with Overleaf, the dashboard or Google Docs is implemented here.
