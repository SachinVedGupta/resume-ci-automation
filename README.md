# Sachin's resume workspace

Edit YAML → commit → view the generated resume in GitHub.

**[Edit shared resume](https://github.com/SachinVedGupta/resume-ci-automation/edit/main/data/resume.yaml)** · **[View all previews](https://github.com/SachinVedGupta/resume-ci-automation/tree/previews)** · **[Build status & downloads](https://github.com/SachinVedGupta/resume-ci-automation/actions/workflows/build-resume.yml)**

## Everyday editing in GitHub

1. Open [`data/resume.yaml`](data/resume.yaml), click the pencil, and edit the text. Use `**bold**` for emphasis and `[label](https://url)` for links. Quote strings containing `: `, or use `>-` for long paragraphs.
2. Click **Commit changes**. Commit to `main` for an ordinary update, or choose a new branch and pull request to review a larger change.
3. Open **Actions → Build Resume** and wait for both jobs to turn green. Open **View all previews** above, choose a version, and see its inline image or PDF. The preview README displays the source commit so you can check it matches your edit.

A failed build leaves the last successful preview intact, including during local editing. Each generated preview also has direct links to edit the shared resume or its variant. Read the error in Actions, fix the YAML or shorten the content, and commit again. A preview is generated after a commit, not while typing in GitHub's editor.

## Versions without duplicating your whole resume

| File | Purpose |
|---|---|
| [`data/resume.yaml`](data/resume.yaml) | Shared career facts, contact details and bullets |
| [`variants/general.yaml`](variants/general.yaml) | Full base resume |
| [`variants/swe.yaml`](variants/swe.yaml) | Software engineering emphasis |
| [`variants/ai.yaml`](variants/ai.yaml) | Agents emphasis, LearnBridge first |
| [`variants/ml.yaml`](variants/ml.yaml) | ML emphasis |
| [`variants/fintech.yaml`](variants/fintech.yaml) | Systems/performance emphasis; no invented finance experience |
| [`variants/companies/`](variants/companies/) | Company-specific versions you create |
| [`archive/original-2026-09-11.tex`](archive/original-2026-09-11.tex) | Your pasted LaTeX, preserved verbatim |

All five presets are drafts for review, not independently researched role-specific applications.

### Add a company resume entirely in GitHub

Choose **Add file → Create new file**, name it `variants/companies/company-role.yaml`, and start with:

```yaml
label: Company — Software Engineering
extends: swe
projects: [nki, learnbridge]
overrides:
  experiences:
    microsoft:
      details:
        - "Your truthful tailored bullet, with **emphasis** if useful."
        - "Another supported bullet."
```

Omit `overrides` to start with an unchanged copy of the parent. Dictionaries merge by field; **lists replace the entire list**. A company override stays independent of later shared edits to that same field; review it when updating the base. Unknown fields, IDs, duplicate keys and inheritance cycles fail the build.

Select or reorder entries with `experiences: [microsoft, zipline, shopify, gdsc, drones]` and `projects: [nki, learnbridge]`. `bullet_order: {shopify: [2, 1, 0]}` uses zero-based indices and may select a subset. The PDF filename remains `resume.pdf`; the containing folder identifies the variant without putting a company target in the PDF header.

## Review and version history

- GitHub **History** shows past YAML changes. Revert a commit to undo it.
- Every successful branch push saves permanent previews at `previews/builds/<source-commit>/`, with PDFs, images, resolved YAML and a PDF SHA-256 manifest. The preview branch's home page points to the latest successful `main` build.
- Branch builds are linked from their Actions summary. Fork pull requests only receive downloadable artifacts; they cannot publish to this repository.
- Actions artifacts expire after 90 days. The committed previews remain in Git history.
- When using a resume for an application, record its variant, source commit and PDF hash in your existing private application tracker. This repository does not track submissions or synchronize the dashboard/Google Docs automatically.
- Do not edit the `previews` branch or generated PDFs. Edit source YAML, then rebuild.

## Ask Codex to edit a resume

> In SachinVedGupta/resume-ci-automation, create companies/acme-ml from ml for this job description. Use only supported experience, preserve other variants, build and visually inspect the one-page PDF, and send me its GitHub preview link.

Repository [AGENTS.md](AGENTS.md) defines the editing and validation rules. This workspace is self-contained; it does not replace or automatically modify Overleaf or your internship tracker.

## Run locally (optional)

With [uv](https://docs.astral.sh/uv/) and either Tectonic or pdfLaTeX installed:

```sh
uv sync --locked
uv run python -m resume_ci_automation --all
uv run python -m resume_ci_automation --variant companies/acme-ml
uv run python -m resume_ci_automation --new companies/acme-ml --from ml
uv run python -m resume_ci_automation --all --validate
uv run python -m unittest discover -s tests -v
uv run python -m resume_ci_automation.watch_resume
```

Or use `docker compose up --build --abort-on-container-exit --exit-code-from resume_ci_automation`. Results appear in `out/<variant>/`.

## Setup and content notes

GitHub Actions uses only this repository's built-in token; no personal access token or separate publishing repository is needed. If Actions is disabled for the fork, open Actions and enable workflows. If your account policy blocks workflow write permissions, a repository administrator must permit the publish job's `contents: write`; PDFs still appear as build artifacts.

This fork is public: source YAML, archived original and generated previews are public. Add only resume material intended for this repository. Attribution and the upstream MIT license are retained.

The migration preserves supplied claims, fixes the email hyperlink and duplicated slash in the LinkedIn URL, normalizes a few technology spellings, and uses a simpler one-page template. The original remains archived. The source's Jetson Nano / FP8 statement merits your technical review before applications; it has not been silently replaced with an invented precision claim. Dates, metrics and company claims are user-supplied, not independently verified by this setup.

Based on [adityarao2005/resume-ci-automation](https://github.com/adityarao2005/resume-ci-automation), with the Jake Gutierrez / sb2nov LaTeX resume design lineage.
