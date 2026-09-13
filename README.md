# bjpark-lab.github.io

Personal AI engineering knowledge base built with the Chirpy Jekyll theme and GitHub Pages.

## Topics

- Stanford AI curriculum notes
- LLM engineering
- AI agents and tool use
- RAG, memory, and evaluation
- Data science and practical system design

## Learning projects

### Stanford AI 30-Day Study

A 30-day learning path covering CS224N, CS336, CS329Z, and CS329A topics with daily PC/mobile study pages, active recall, practical exercises, and progress tracking.

- Site: https://bjpark-lab.github.io/stanford-ai-study/
- Source: `stanford-ai-study/`

## Repository structure

- `_posts/` — public technical notes
- `_tabs/` — top-level site navigation
- `stanford-ai-study/` — standalone interactive learning site
- `tools/validate_stanford_study.py` — schema + content checks for the study site
- `_config.yml` — Chirpy/Jekyll site configuration

## Local development

```bash
npm install        # install the asset toolchain
npm run build      # build assets/js/dist (gitignored, required by the site)
npm test           # stylelint the SCSS
npm run validate   # validate the Stanford study data
bundle install     # install Jekyll and plugins
bash tools/run     # serve the site locally
bash tools/test    # production build + htmlproofer
```

`assets/js/dist` is not committed, so `npm run build` must run before any Jekyll
build — CI does this in both workflows.

## Public-content rule

Only generalized or synthetic examples belong in this public repository. Do not publish internal URLs, account/server names, real production data, equipment or lot identifiers, proprietary recipe values, or other confidential information.

## Local development

```bash
bundle install
bundle exec jekyll serve
```

The GitHub Actions workflow builds and deploys the site to GitHub Pages.
