# Stanford AI Study Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the validated 30-day Stanford AI study bundle at `https://bjpark-lab.github.io/stanford-ai-study/` without changing the existing Chirpy site behavior.

**Architecture:** Add one isolated static subtree, `stanford-ai-study/`, to the existing GitHub Pages repository. Keep every learning page self-contained HTML with relative links so Jekyll copies the subtree into `_site` unchanged while the existing Pages workflow continues to build and deploy the root site.

**Tech Stack:** Static HTML/CSS/JavaScript, Jekyll/Chirpy existing site, GitHub Pages, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-12-stanford-ai-study-pages-design.md`

## Global Constraints

- Do not modify `_config.yml`, existing posts, tabs, theme assets, or existing navigation.
- Publish only generalized/synthetic learning content; no internal identifiers or real company data.
- Use `/stanford-ai-study/index.html` plus `stanford-ai-study/days/*.html`.
- Preserve relative links between master, PC, and mobile pages.
- Use the repository's existing `pages-deploy.yml`; do not add a second Pages workflow.
- Verify 61 HTML files total: one master plus 30 PC and 30 mobile pages.

---

### Task 1: Validate the static bundle

**Files:**
- Source: local generated bundle `stanford_ai_30day_process_memory_final.zip`

**Interfaces:**
- Consumes: final generated ZIP from the learning-material workflow.
- Produces: a validated directory containing exactly 61 HTML files and zero broken relative HTML links.

- [ ] **Step 1:** Extract the ZIP into a clean temporary directory.
- [ ] **Step 2:** Count `*.html`; expected `61`.
- [ ] **Step 3:** Count `days/*.html`; expected `60`.
- [ ] **Step 4:** Parse every anchor with a relative `href` and verify its target exists.
- [ ] **Step 5:** Stop if any local link is missing; otherwise record `VALIDATION_OK`.

### Task 2: Add the deployment subtree on an isolated branch

**Files:**
- Create: `stanford-ai-study/index.html`
- Create: `stanford-ai-study/days/day01_2026-09-14_pc.html` through `day30_2026-10-23_pc.html`
- Create: `stanford-ai-study/days/day01_2026-09-14_mobile.html` through `day30_2026-10-23_mobile.html`
- Create: `stanford-ai-study/README.md`

**Interfaces:**
- Consumes: validated bundle from Task 1.
- Produces: an isolated static subtree that Jekyll can copy unchanged.

- [ ] **Step 1:** Work on branch `feat/stanford-ai-study-pages` based on `main`.
- [ ] **Step 2:** Upload the 61 HTML files with their relative paths preserved.
- [ ] **Step 3:** Add `README.md` explaining URL, file layout, public-content constraints, and update procedure.
- [ ] **Step 4:** Verify representative files on the branch: master, Day 1 PC/mobile, Day 30 PC/mobile.
- [ ] **Step 5:** Compare branch to `main`; expected changes are limited to the new static subtree plus this implementation plan.

### Task 3: Merge through a pull request

**Files:**
- No additional content files.

**Interfaces:**
- Consumes: validated feature branch.
- Produces: merged `main` commit that triggers the existing Pages workflow.

- [ ] **Step 1:** Open a PR from `feat/stanford-ai-study-pages` to `main` describing the isolated static-site addition.
- [ ] **Step 2:** Verify the PR changed-file list contains the plan plus the `stanford-ai-study/` subtree and no unrelated modifications.
- [ ] **Step 3:** Merge with squash or merge commit according to repository capability.
- [ ] **Step 4:** Capture the resulting `main` commit SHA.

### Task 4: Verify GitHub Pages deployment

**Files:**
- Existing workflow: `.github/workflows/pages-deploy.yml` (read only)

**Interfaces:**
- Consumes: merged `main` commit.
- Produces: confirmed public site at `/stanford-ai-study/`.

- [ ] **Step 1:** Check workflow runs triggered by the merged commit/push.
- [ ] **Step 2:** Confirm the Pages build/deploy completes successfully; if it fails, inspect the failing job/log before making further changes.
- [ ] **Step 3:** Open `https://bjpark-lab.github.io/stanford-ai-study/`.
- [ ] **Step 4:** Verify at least the master page and representative Day 1/Day 30 links resolve.
- [ ] **Step 5:** Confirm the root site remains reachable and report the final public URL.
