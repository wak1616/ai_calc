# ai_calc - Arcuate Incision Calculator

Web app that predicts **laser arcuate incision length** for astigmatism correction in
cataract surgery, from an ML model. Joaquin's own project (he is the ophthalmologist and
the author). Live at **https://aicalc.derojas.ai** (no hyphen in the hostname).

Repo: `https://github.com/wak1616/ai_calc`

## Read this first

You are rooted at this repo, so this file is the whole context you get. Business/ops
context for Joaquin's projects lives in `~/macagent/` and is deliberately NOT loaded here.
If a question is about strategy, customers, or anything non-code, say so rather than
guessing from this repo.

## Branch convention: the default branch is literally named `DEFAULT`

Not `main`, not `master`. `origin/HEAD -> origin/DEFAULT`. This trips up every tool and
every agent that assumes `main`, so check before you branch or push:

```sh
git -C ~/ai_calc status -sb
git symbolic-ref refs/remotes/origin/HEAD
```

Feature branches follow `codex/<topic>` and `claude/<topic>` naming from prior agent work.

## Architecture

Two halves, deployed separately:

- **Frontend** - Vue 3 + Vuetify + Vite (`src/`, entry `index.html`). Note the
  `package.json` `name` is still the scaffold's `vue-vuetify-vite-template`; ignore it.
  Deployed on **Vercel** (`vercel.json`: framework `vite`, output `dist`, SPA rewrite of
  everything to `/`).
- **Backend** - FastAPI in `backend/` (`main.py`, `requirements.txt`, `Dockerfile`).
  Serves the prediction from an **XGBoost** model, with **Ridge Regression** as a
  selectable alternative. XGBoost is the default.
  Deployed on **Cloud Run**, in its own dedicated GCP project (`ai-calc-derojas`), moved
  there from Render (commits 2ed35ee, 6370ba0).

`middleware.js` and `public/` sit at the root alongside the Vue app.

**Gotcha for Iris/agent sessions:** the Cloud Run backend lives in a *separate* GCP
project from `sightflow-488620`. A `gcloud` session pointed at the usual project will not
see it. Also remember `gcloud`'s active account is global machine state shared by every
lane - set it explicitly in the same command chain rather than assuming.

## Local development

`run.py` is the convenience launcher (starts backend and frontend together, checks ports).
Manually:

```sh
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload      # backend, dev reload

npm install && npm run dev     # frontend (Vite)
```

Requires Python 3.8+ and Node 16+.

## Clinical + compliance constraints

- Input validation is clinical, not cosmetic. Ranges such as corneal astigmatism
  0.25-1.50 D are deliberate; do not widen a range to make a test pass.
- Supports single and paired arcuates, with a visual representation of the incisions.
- `SECURITY_REVIEW.md` and `backend/ENTERPRISE_READINESS.md` hold the security and
  deployment review notes. **Read `SECURITY_REVIEW.md` before touching anything that
  handles patient input or logging.**
- **No patient names, ever.** There is prior work specifically removing patient names for
  HIPAA (`claude/hipaa-remove-patient-names-CPZT6`). Do not add a field, a log line, or a
  telemetry payload that could carry an identifier.

## Working rules

- **Check the branch before you touch anything.** This checkout is shared machine state
  across several agent lanes plus Joaquin's own sessions. Dirty or off-default means
  someone has work in flight: leave it alone and use a worktree.
- **Do not push to `DEFAULT` without Joaquin saying so.** It is the production branch and
  Vercel deploys from it.
- Keep durable engineering knowledge (DOM gotchas, API quirks, model/serving behavior) in
  THIS file, not in the macagent ops folders.
