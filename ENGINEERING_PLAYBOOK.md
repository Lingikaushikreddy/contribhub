# ContribHub — Engineering Playbook & Task Assignments
## Senior Engineer Roles, Sprint Tasks, and Best Practices

**Version:** 1.0
**Created:** March 13, 2026
**Timeline:** 12-Week MVP Sprint (Weeks 1-12)

---

## Table of Contents

1. [Team Structure & Role Assignments](#1-team-structure--role-assignments)
2. [Development Methodology](#2-development-methodology)
3. [Sprint Breakdown & Task Assignments](#3-sprint-breakdown--task-assignments)
4. [Best Practices by Domain](#4-best-practices-by-domain)
5. [Technical Standards & Quality Gates](#5-technical-standards--quality-gates)
6. [Infrastructure & DevOps](#6-infrastructure--devops)
7. [Cost & Budget Projections](#7-cost--budget-projections)

---

## 1. Team Structure & Role Assignments

### Org Chart (MVP Phase)

```
                         Kaushik Reddy
                     CEO / Technical Founder
                    (Product vision, GTM, hiring)
                              |
                     ┌────────┴────────┐
                     │                 │
              Aravind K.          Meera S.
         CTO / Tech Lead       Head of AI/ML
        (Architecture,         (ML pipeline,
         code review,           models, evals)
         sprint planning)            |
              |                      |
     ┌────────┼────────┐        Rajan P.
     │        │        │      ML Engineer
  Vikram D.  Neha R.  Karthik M.  (Data, evals,
  Sr. Full-  Sr. Full- Sr. Backend  fine-tuning)
  Stack #1   Stack #2  / Infra
  (Triage)   (Matching) (Platform)
```

### Role Definitions

---

### Role 1: CTO / Tech Lead — Aravind K.

**Profile:** 8+ years full-stack, prior startup CTO experience, strong in system design and API architecture. Writes 50%+ of early codebase.

**Owns:**
- Overall architecture decisions and tech stack governance
- Sprint planning, task decomposition, and dependency management
- Code review (final approver on all PRs)
- GitHub App skeleton and webhook infrastructure
- Database schema design
- Security architecture (HMAC verification, token encryption)

**Key Metrics:**
- PR review turnaround: <4 hours
- Architecture decisions documented within 24 hours
- Zero security vulnerabilities in core auth/webhook paths

---

### Role 2: Head of AI/ML — Meera S.

**Profile:** 6+ years ML/NLP, experience with transformer fine-tuning, production ML systems, and LLM integration. Published research or significant OSS contributions in NLP.

**Owns:**
- Issue classification model (SetFit → DeBERTa fine-tuning pipeline)
- Embedding pipeline for duplicate detection
- LLM-powered response drafting (RAG architecture)
- Model evaluation framework and golden datasets
- ML cost optimization (model routing, caching)
- Drift monitoring setup (Evidently AI)

**Key Metrics:**
- Auto-label accuracy: >88% within Sprint 2, >92% by Sprint 4
- Duplicate detection F1: >85%
- LLM cost per issue triage: <$0.025
- Response draft quality: >80% maintainer acceptance rate

---

### Role 3: ML Engineer — Rajan P.

**Profile:** 3-5 years ML engineering, strong Python, experience with data pipelines, model evaluation, and GitHub API. Reports to Meera S.

**Owns:**
- Training data collection and synthetic data generation
- Active learning pipeline (maintainer feedback → model retraining)
- Code complexity analysis (Tree-sitter AST parsing, cyclomatic/cognitive complexity)
- Skill profiling engine (GitHub activity → skill taxonomy mapping)
- Project health scoring algorithm (CHAOSS-inspired metrics)
- Model versioning (MLflow setup)

**Key Metrics:**
- Training dataset: 5,000+ labeled issues by Week 4
- Complexity scorer accuracy: within 1 level of human assessment 80% of time
- Health score correlation with human judgment: r > 0.75
- Skill profile generation: <30 seconds per contributor

---

### Role 4: Sr. Full-Stack Engineer #1 (Triage) — Vikram D.

**Profile:** 5+ years TypeScript/React/Next.js, experience with GitHub integrations and real-time systems. Strong frontend with solid backend skills.

**Owns:**
- Maintainer-facing features end-to-end
- GitHub App UI (installation flow, permissions, OAuth)
- `.contribhub.yml` configuration parser and validation
- Triage dashboard (analytics, charts, label accuracy feedback)
- Maintainer notification system (email digests, GitHub comments)
- Response draft approval workflow (maintainer reviews AI drafts)

**Key Metrics:**
- GitHub App installation: <2 minutes, <3 clicks
- Dashboard load time: <1.5 seconds (LCP)
- Config changes take effect: <30 seconds
- Email digest delivery: 99.5% reliability

---

### Role 5: Sr. Full-Stack Engineer #2 (Matching) — Neha R.

**Profile:** 5+ years TypeScript/React/Next.js, experience with recommendation systems or marketplace products. Strong UX sensibility.

**Owns:**
- Contributor-facing features end-to-end
- Skill profile builder UI (auto-generated + editable)
- Issue recommendation feed (matching engine → ranked cards)
- Project health score display and filtering
- Contributor onboarding flow (GitHub OAuth → profile → first recommendations)
- Feedback loop UI (thumbs up/down, difficulty ratings)
- Contributor reputation/growth tracking (V1.2)

**Key Metrics:**
- Onboarding to first recommendation: <60 seconds
- Recommendation feed load: <500ms
- Contributor 7-day retention: >40%
- Feedback submission rate: >15% of recommendation views

---

### Role 6: Sr. Backend / Infrastructure Engineer — Karthik M.

**Profile:** 6+ years backend (Python/Node.js), deep expertise in distributed systems, databases, CI/CD, and cloud infrastructure. DevOps generalist.

**Owns:**
- FastAPI backend architecture (routers/services/repositories pattern)
- PostgreSQL schema, migrations (Alembic), indexing strategy
- Redis + BullMQ/Dramatiq job queue infrastructure
- Webhook gateway (signature verification, idempotency, queue routing)
- CI/CD pipeline (GitHub Actions → Vercel + Railway)
- Infrastructure setup (Vercel, Railway, monitoring stack)
- Rate limiting, API versioning, security hardening
- pgvector setup for embeddings storage

**Key Metrics:**
- Webhook processing: <10 seconds end-to-end
- API p99 latency: <200ms
- CI pipeline: <5 minutes green-to-deploy
- System uptime: 99.9%
- Zero data loss on webhook failures (queue + retry)

---

## 2. Development Methodology

### Sprint Structure

**Cadence:** 2-week sprints (6 sprints = 12 weeks)
**Ceremony (kept minimal):**

| Event | Duration | When |
|---|---|---|
| Sprint Planning | 45 min | Monday, Day 1 of sprint |
| Daily Standup | 10 min (async Slack OK) | Every day, 10 AM |
| Demo | 30 min | Friday, Day 10 of sprint |
| Retro | 15 min (async doc) | Friday, Day 10 of sprint |

### Git Strategy: Trunk-Based Development

```
main (always deployable)
  ├── feature/ch-123-issue-classifier     (lives <3 days)
  ├── feature/ch-124-duplicate-detection  (lives <3 days)
  └── feature/ch-125-webhook-gateway      (lives <3 days)
```

**Rules:**
- All branches merge to `main` via PR with 1 approval
- No branch lives longer than 3 days — break work down further if needed
- Feature flags for incomplete features (environment variables initially, PostHog flags later)
- Deploy to staging on every merge to `main`
- Deploy to production on tag/release

### Quality Gates (CI Pipeline)

```yaml
# Automated on every PR:
- TypeScript: tsc --noEmit (zero errors)
- Python: mypy + ruff (zero errors)
- Lint: ESLint + Prettier (frontend), ruff (backend)
- Unit tests: vitest (frontend), pytest (backend)
- Security: gitleaks (secret scanning)
- Build: next build (must succeed)

# On merge to main (additional):
- Integration tests (API + database)
- Model evaluation (if ML code changed)
- Deploy to staging
```

### Task Sizing

| Size | Time | Example |
|---|---|---|
| **S** | <4 hours | Add a new API endpoint with tests |
| **M** | 4-12 hours (1-2 days) | Build the config file parser + validation |
| **L** | 2-3 days | Implement duplicate detection pipeline end-to-end |
| **XL** | >3 days | **Must be broken down** into S/M/L tasks |

---

## 3. Sprint Breakdown & Task Assignments

---

### SPRINT 1 (Weeks 1-2): Foundation & Skeleton

**Goal:** Standing infrastructure, deployable skeleton, GitHub App installed on test repos.

| Task ID | Task | Size | Assignee | Dependencies | Best Practice |
|---|---|---|---|---|---|
| S1-01 | **Monorepo scaffold** — Set up Turborepo monorepo with `apps/web` (Next.js 15), `apps/api` (FastAPI), `packages/ml-pipeline`, `packages/shared` | M | Karthik M. | None | Turborepo for build caching; shared TypeScript types between frontend and API |
| S1-02 | **PostgreSQL schema v1** — Design and implement core tables: `users`, `repos`, `issues`, `skills`, `user_skills`, `issue_skills`, `matches`, `triage_events` | M | Aravind K. | None | UUID PKs (v7 if Postgres 18), B-tree indexes on FKs, GIN index on jsonb columns. Use Alembic for migrations. |
| S1-03 | **GitHub App registration + OAuth flow** — Register GitHub App, configure permissions (issues:read/write, PRs:read, contents:read, metadata:read), implement OAuth with Auth.js v5 | M | Vikram D. | None | Principle of least privilege — only request permissions you use today. Auth.js v5 auto-infers GitHub credentials. |
| S1-04 | **Webhook gateway** — FastAPI endpoint that receives GitHub webhooks, verifies HMAC-SHA256 signature, deduplicates via `X-GitHub-Delivery` header, enqueues to BullMQ/Dramatiq | L | Karthik M. | S1-01 | Use constant-time comparison (`hmac.compare_digest`). Return 2xx within 10 seconds. Store delivery IDs in Redis (TTL 72h) for idempotency. |
| S1-05 | **CI/CD pipeline** — GitHub Actions workflow: lint, type-check, test, build, deploy to Railway (API) + Vercel (web) | M | Karthik M. | S1-01 | Parallel jobs for lint/type-check/test. Cache `node_modules` and pip deps. Target <5 min total pipeline. |
| S1-06 | **Next.js app shell** — Layout, navigation, GitHub OAuth login, dark mode, shadcn/ui setup, TanStack Query provider | M | Neha R. | S1-01, S1-03 | Server Components for layout, Client Components only for interactive widgets. shadcn/ui + Recharts for dashboard charts. |
| S1-07 | **ML pipeline skeleton** — Python package structure, model loading/inference interfaces, pytest fixtures, MLflow experiment tracking setup | M | Meera S. | S1-01 | Separate `inference/`, `training/`, `evaluation/` modules. Mock LLM calls in tests. MLflow with Postgres backend. |
| S1-08 | **Training data collection** — Script to pull issues from 50 popular OSS repos via GitHub GraphQL API, extract labels/categories, build initial labeled dataset (target: 5,000 issues) | L | Rajan P. | None | Use GraphQL `search` query with `is:issue` filters. Batch in pages of 100. Respect rate limits (5,000 points/hr). Store as Parquet files versioned with DVC. |
| S1-09 | **Redis + message queue setup** — Redis instance on Railway, BullMQ workers for Python tasks via bridge, or Dramatiq with Redis broker | M | Karthik M. | S1-01 | BullMQ for Node.js tasks (notifications, config updates), Dramatiq for Python tasks (ML inference). Use separate queues per task type. |
| S1-10 | **Monitoring bootstrap** — Sentry (errors), PostHog (analytics), Grafana Cloud (infra metrics) — basic setup across web + API | S | Karthik M. | S1-01, S1-05 | Use OpenTelemetry instrumentation to avoid vendor lock-in. PostHog free tier: 1M events/mo. Sentry free: 5K errors/mo. |

**Sprint 1 Deliverable:** A deployable skeleton where GitHub App can be installed on a test repo, webhook events are received and queued, and the web app shows a login page.

---

### SPRINT 2 (Weeks 3-4): AI Triage Core

**Goal:** Issues get auto-labeled within 30 seconds of creation. Duplicate detection working.

| Task ID | Task | Size | Assignee | Dependencies | Best Practice |
|---|---|---|---|---|---|
| S2-01 | **Issue classifier v1** — Fine-tune SetFit + ModernBERT on collected dataset. Categories: `bug`, `feature`, `question`, `docs`, `chore`. Priority: `P0-P3`. Output confidence scores. | L | Meera S. | S1-08 | SetFit handles cold-start (few-shot). Use 80/10/10 train/val/test split. Track precision/recall per class. Target >88% accuracy. |
| S2-02 | **Complexity scorer v1** — Tree-sitter AST analysis for affected files: cyclomatic complexity, cognitive complexity, nesting depth, file coupling from git co-change history | L | Rajan P. | S1-08 | Formula: `0.6 * cognitive + 0.25 * cyclomatic + 0.15 * coupling`. Map to 4 levels: beginner (1-2), intermediate (3-5), advanced (6-8), expert (9-10). Use lizard for multi-language analysis. |
| S2-03 | **Embedding pipeline** — Embed all open issues using text-embedding-3-large (1024d), store in pgvector, similarity search endpoint | L | Rajan P. | S1-02, S1-09 | Start with pgvector (avoids new infra). Cosine similarity. Incremental: embed new issues on webhook, upsert into index. Threshold 0.85 for duplicates. |
| S2-04 | **Duplicate detection worker** — On new issue: embed → query top-5 similar → if score >0.80, comment on issue with link; if >0.95, auto-label `possible-duplicate` | M | Meera S. | S2-03 | Never auto-close — only suggest. Include confidence score in comment. Let maintainer confirm/dismiss. Log all decisions for model improvement. |
| S2-05 | **Label application worker** — On classifier output: apply labels via GitHub API, add confidence badge in comment, handle label creation if labels don't exist | M | Vikram D. | S2-01, S1-04 | Create labels with consistent colors on first run. Only apply labels above 70% confidence. Labels below threshold get `needs-review`. |
| S2-06 | **Config file parser** — Parse `.contribhub.yml` from repo root: custom label taxonomy, tone, thresholds, excluded labels, trusted reporters | M | Vikram D. | S1-04 | Validate with JSON Schema / Pydantic. Fail gracefully with defaults if file missing or malformed. Cache parsed config in Redis (invalidate on push event). |
| S2-07 | **Evaluation framework** — Golden test set (500 manually labeled issues), automated eval script, accuracy/precision/recall/F1 per category, CI integration | M | Rajan P. | S2-01 | Run evals on every ML code change. Track metrics in MLflow. Set deployment gate: new model must beat baseline on golden set. |
| S2-08 | **Webhook event routing** — Route different GitHub events to appropriate workers: `issues.opened` → classifier + duplicate detector, `issues.edited` → re-classify, `push` → invalidate config cache | M | Karthik M. | S1-04, S1-09 | Use event type + action as routing key. Dead-letter queue for failed events. Retry with exponential backoff (3 attempts, 1s/5s/30s). |

**Sprint 2 Deliverable:** Install ContribHub on a test repo, create an issue, and see it auto-labeled within 30 seconds with category, priority, complexity, and duplicate check.

---

### SPRINT 3 (Weeks 5-6): Response Drafting & Skill Profiling

**Goal:** AI drafts responses for maintainers. Contributors can build skill profiles.

| Task ID | Task | Size | Assignee | Dependencies | Best Practice |
|---|---|---|---|---|---|
| S3-01 | **RAG context builder** — Index repo docs (README, CONTRIBUTING.md, past maintainer responses, issue templates) per repo. Chunk by section, embed, store in pgvector. | L | Meera S. | S2-03 | Chunk at heading boundaries (H2/H3). Embed with same model as issues. Refresh on `push` events to default branch. Cap context to 4K tokens for LLM prompt. |
| S3-02 | **Response drafter** — LLM generates response drafts grounded in RAG context. Templates: missing-info request, feature acknowledgment, question→docs redirect, duplicate link. | L | Meera S. | S3-01 | Use model routing: Claude Haiku for templated responses ($0.003), Claude Sonnet for complex issues ($0.02). Cache common responses in Redis (semantic cache). Never auto-post — draft only. |
| S3-03 | **Maintainer approval flow** — Dashboard UI for reviewing/editing/approving AI-drafted responses before posting to GitHub | M | Vikram D. | S3-02, S1-06 | One-click approve, inline edit, discard with reason. Show response alongside original issue. Track approval/edit/discard rates as model quality metric. |
| S3-04 | **Issue quality scorer** — Score each issue 0-100 on completeness: reproduction steps, environment info, error logs, screenshots, expected vs. actual | M | Rajan P. | S2-01 | Use a checklist approach: +20 for repro steps, +15 for environment, +15 for error logs, +10 for screenshots, +15 for expected/actual, +10 for version info, +15 for clear description. NLP entity extraction to detect presence. |
| S3-05 | **Skill profile builder (backend)** — GitHub GraphQL queries to extract: languages used (weighted by LOC), repos contributed to, PR complexity, review activity. Map to 3-level skill taxonomy. | L | Rajan P. | S1-02 | Use `contributionsCollection` for efficient data pull. Hierarchical taxonomy: Domain → Technology → Specific (e.g., Backend → Python → FastAPI). Refresh profiles weekly via batch job. |
| S3-06 | **Skill profile builder (frontend)** — Auto-generated profile with editable skills, interests selector, experience level self-declaration. Public profile page (opt-in). | M | Neha R. | S3-05, S1-06 | Show inferred skills with confidence. Let contributor override. Skill chips with proficiency levels. Clean, resume-linkable public profile URL. |
| S3-07 | **Tone configuration** — Support 3 response tones (formal/friendly/minimal) per `.contribhub.yml`. Include 3-5 few-shot examples per tone in LLM prompt. | S | Meera S. | S3-02, S2-06 | Curate example responses for each tone from real OSS projects. Use system prompt for tone control + few-shot examples in user prompt. |
| S3-08 | **Cost tracking dashboard** — Internal dashboard showing LLM API costs per repo, per day, per operation (classify/embed/draft). Alert if daily cost exceeds threshold. | S | Karthik M. | S3-02 | Log token usage per API call. Aggregate in PostgreSQL. Alert via Slack webhook if daily cost >$50. Display in admin dashboard. |

**Sprint 3 Deliverable:** Maintainers see AI-drafted responses they can approve with one click. Contributors can sign up and see their auto-generated skill profile.

---

### SPRINT 4 (Weeks 7-8): Matching Engine & Health Scoring

**Goal:** Contributors receive personalized issue recommendations ranked by fit.

| Task ID | Task | Size | Assignee | Dependencies | Best Practice |
|---|---|---|---|---|---|
| S4-01 | **Project health scorer** — CHAOSS-inspired scoring: commit frequency (0.18), community engagement (0.18), code quality (0.15), documentation (0.15), responsiveness (0.12), sustainability (0.12), security (0.10) | L | Rajan P. | S1-02 | Normalize within language/size cohort (percentile ranking). Update daily via batch job. Filter out repos scoring <30 from matching pool. Bus factor via DOA algorithm. |
| S4-02 | **Matching algorithm v1** — Composite score: skill match (40%) × project health (25%) × interest alignment (20%) × growth stretch (15%). Rank top 10 issues per contributor. | L | Meera S. | S3-05, S4-01, S2-02 | Content-based matching first (no collab filtering data yet). Pre-compute contributor embeddings nightly. Query pgvector ANN for candidate generation, then re-rank with cross-features. Exclude: dormant repos, claimed issues, issues with open PRs. |
| S4-03 | **Recommendation feed (frontend)** — Issue cards: project name, health score (dots), difficulty (bar), estimated time, prerequisite skills, maintainer response time | L | Neha R. | S4-02 | Server Component for initial load, TanStack Query for pagination/refresh. Skeleton loading states. Each card links to GitHub issue. "I'll take this" button logs match acceptance. |
| S4-04 | **Feedback loop (backend + frontend)** — Thumbs up/down on recommendations. Dismissal reasons: "Too hard", "Too easy", "Not interested", "Already taken". Persist for model retraining. | M | Neha R. | S4-03 | Implicit signal: card viewed (weakest). Explicit: thumbs up/down (strong). Log all feedback events to BullMQ → PostgreSQL. Retrain matching weights weekly with feedback data. |
| S4-05 | **Dormant repo filter** — Multi-signal detection: commit decay curve, issue response time >30 days for 3+ months, `isArchived` flag, top contributors inactive >6 months | M | Rajan P. | S4-01 | Don't rely on last commit alone — mature/stable repos have low activity without being dead. Cross-reference with download metrics (npm, PyPI) if available. |
| S4-06 | **Claimed issue detection** — Check for existing open PRs referencing an issue. Parse PR body/title for issue number patterns (#123, "fixes #123", "closes #123"). | S | Vikram D. | S1-04 | Use GitHub's timeline API to detect linked PRs. Cache PR↔issue mapping. Update on `pull_request` webhook events. |
| S4-07 | **Health score display** — Add health indicators to all issue recommendations and project pages. Transparent scoring methodology page. | M | Neha R. | S4-01, S4-03 | Show breakdown on hover/click (commit frequency: A, responsiveness: B, docs: C). Link to "How We Score Projects" docs page. |
| S4-08 | **Rate limiter** — Token bucket rate limiting for all API endpoints. Tiered limits: free (100/hr), pro (1,000/hr), enterprise (10,000/hr). `X-RateLimit-*` headers. | M | Karthik M. | S1-09 | Redis-based sliding window counter. Return 429 with `Retry-After` header. Log rate limit events. Proactive notification at 75% threshold. |

**Sprint 4 Deliverable:** Contributors see personalized recommendations with health-scored projects. The matching engine is live and learning from feedback.

---

### SPRINT 5 (Weeks 9-10): Dashboard, Analytics & Polish

**Goal:** Maintainer dashboard with full analytics. Contributor experience polished. System hardened.

| Task ID | Task | Size | Assignee | Dependencies | Best Practice |
|---|---|---|---|---|---|
| S5-01 | **Triage dashboard** — Charts: issue volume trends, category breakdown, MTTR, MTTFR, AI accuracy over time, top contributors, backlog burndown | L | Vikram D. | S2-05, S1-06 | shadcn/ui charts (Recharts). Server Components for data fetch, Client Components for interactive charts. Date range picker. Export to CSV. |
| S5-02 | **Weekly email digest** — Automated email to maintainers: new issues, resolved, avg response time, AI accuracy stats, top contributor shoutouts | M | Karthik M. | S5-01 | Use SendGrid or AWS SES. Batch job (Dramatiq scheduled task) every Monday. Unsubscribe link per CAN-SPAM. Plain HTML email (no heavy frameworks). |
| S5-03 | **Model retraining pipeline** — Weekly automated pipeline: collect maintainer corrections → merge into training set → fine-tune DeBERTa-v3 → evaluate on golden set → deploy if better | L | Meera S. | S2-01, S2-07 | Active learning: prioritize issues where maintainer corrected the AI. SetFit → DeBERTa-v3 transition when dataset >1,000 issues per repo. Canary rollout: 10% traffic → 50% → 100%. |
| S5-04 | **Drift monitoring** — Evidently AI dashboard tracking input distribution drift (Jensen-Shannon divergence on embeddings) and concept drift (accuracy degradation over time) | M | Rajan P. | S5-03 | Alert on drift exceeding threshold. Trigger retraining. Track maintainer override rate as primary quality signal. |
| S5-05 | **Guided onboarding brief** — When contributor selects an issue, generate a contribution brief: relevant files (GitHub links), key functions, related tests, setup instructions, suggested approach | L | Neha R. | S4-02 | Use LLM with repo context (RAG). Extract from CONTRIBUTING.md + Dockerfile + CI config. Generate within 60 seconds. Clean reading view. |
| S5-06 | **Contributor growth tracking** — Visualization: skills gained over time, issues completed, difficulty progression. Personal growth dashboard (not competitive leaderboard). | M | Neha R. | S3-06, S4-04 | Line chart of difficulty level over time. Skill radar chart. "Next milestone" suggestion. Opt-in public profile. No leaderboards — growth is personal. |
| S5-07 | **Notification preferences** — Per-channel (email, GitHub, in-app), per-event-type toggles. Batch vs. immediate. One-click unsubscribe. | M | Vikram D. | S5-02 | Store preferences in PostgreSQL. Check before sending any notification. GDPR: default all notifications to off, let user opt in. |
| S5-08 | **API documentation** — Auto-generated OpenAPI docs (FastAPI), interactive Swagger UI at `/docs`, getting started guide, webhook event reference | M | Karthik M. | All API work | Use Pydantic models as response schemas. Add descriptions, summaries, tags to all routes. ReDoc at `/redoc`. Versioned at `/api/v1/`. |
| S5-09 | **Security audit** — HMAC verification review, token encryption at rest (AES-256-GCM), CSRF protection, Content-Security-Policy headers, dependency audit (`npm audit`, `safety check`) | M | Aravind K. | All | Never store tokens in plaintext. Use `crypto.timingSafeEqual` for signature verification. Rotate webhook secrets every 90 days. Run gitleaks in CI. |

**Sprint 5 Deliverable:** Full maintainer dashboard with analytics. Contributor experience with guided onboarding. Security audit passed.

---

### SPRINT 6 (Weeks 11-12): Beta Launch & Hardening

**Goal:** Public beta launch. 50 repos installed. System stable under real load.

| Task ID | Task | Size | Assignee | Dependencies | Best Practice |
|---|---|---|---|---|---|
| S6-01 | **Load testing** — Simulate 1,000 concurrent webhook events, 500 simultaneous dashboard users, 10,000 matching queries/hour | M | Karthik M. | All | Use k6 or Artillery. Test webhook processing latency under load. Identify bottlenecks. Auto-scaling rules for Railway workers. |
| S6-02 | **GitHub Marketplace listing** — Logo, feature card, screenshots, description, pricing plans, installation flow, privacy policy, terms of service | M | Vikram D. | All | GitHub requires 100 installs before paid plans. Start free. Clear screenshots showing value (before/after triage). Privacy policy covering data usage. |
| S6-03 | **Onboarding flow optimization** — Measure drop-off at each step (install → configure → first triage → dashboard visit). Fix highest drop-off points. | M | Neha R. | S6-02 | PostHog funnel analysis. Target: 80% completion from install to first auto-labeled issue. Reduce steps. Add progress indicator. |
| S6-04 | **Beta outreach campaign** — Identify 50 target repos (10K+ stars, active maintainers, high issue volume). Personalized outreach via Twitter/email showing their specific triage burden. | L | Kaushik + Aravind | S6-02 | Show them: "Your repo got 847 issues in the last 90 days. 312 were missing reproduction steps. ContribHub auto-requests these." Personalized pitch > generic launch post. |
| S6-05 | **Error handling hardening** — Graceful degradation: if LLM API down, queue and retry; if GitHub API rate limited, backoff; if classifier confidence <50%, skip auto-label and notify maintainer | M | Meera S. + Karthik M. | All | Circuit breaker pattern. Fallback responses. Never fail silently. Alert team on persistent failures. Status page at status.contribhub.dev. |
| S6-06 | **Model fine-tuning on beta data** — Use real issues from beta repos to fine-tune classifier. Collect maintainer corrections. Retrain and deploy improved model. | L | Meera S. + Rajan P. | S5-03 | Per-repo fine-tuning if repo has >200 labeled issues. Otherwise use aggregate model. A/B test fine-tuned vs. base model. |
| S6-07 | **Documentation site** — Landing page, features overview, getting started guide, API reference, FAQ, pricing page | L | Vikram D. + Neha R. | All | Minimal marketing site. Focus on developer trust: open-source triage action, transparent AI reasoning, privacy-first design. |
| S6-08 | **Backup & disaster recovery** — PostgreSQL automated backups (daily), Redis persistence, webhook replay capability, infrastructure recovery runbook | M | Karthik M. | All | Railway automated backups. Test restore procedure. Document recovery steps. RTO target: <1 hour. RPO target: <24 hours. |

**Sprint 6 Deliverable:** ContribHub is live on GitHub Marketplace. 50 beta repos installed. System handles real-world load. Public launch announcement.

---

## 4. Best Practices by Domain

### 4.1 AI/ML Pipeline (Meera S. & Rajan P.)

#### Issue Classification

| Decision | Choice | Rationale |
|---|---|---|
| **Cold-start model** | SetFit + ModernBERT | 50% improvement over standard fine-tuning in few-shot scenarios. Handles repos with <100 labeled issues. |
| **Production model** | DeBERTa-v3-base fine-tuned | Best accuracy among encoders (disentangled attention). 100x cheaper than LLM APIs at scale. <50ms p99 latency. |
| **LLM fallback** | Claude Haiku / GPT-4o-mini | For edge cases where classifier confidence <50%. Model routing saves 47-85% on LLM costs. |
| **Training data** | Synthetic + real | Use LLM to generate labeled examples from repo's existing issues. Validate with maintainers. |
| **Active learning** | Uncertainty sampling + BADGE | Prioritize issues where classifier was corrected by maintainer. Retrain weekly. |
| **Drift detection** | Evidently AI | Monitor embedding distribution + maintainer override rate. Alert + retrain on drift. |

#### Duplicate Detection

| Decision | Choice | Rationale |
|---|---|---|
| **Embedding model** | text-embedding-3-large (1024d) | Top MTEB scores. Flexible dimensionality. $0.00013/1K tokens. |
| **Vector store** | pgvector (start) → Qdrant (scale) | Zero new infra initially. pgvector handles <1M vectors easily. Migrate to Qdrant at 10M+. |
| **Similarity threshold** | 0.85 (configurable per repo) | GitHub issues are more varied than product descriptions. Lower threshold catches more, higher reduces false positives. |
| **Indexing** | Incremental (upsert on each issue) | Real-time freshness. pgvector 0.8.0+ supports iterative index scans. |

#### Response Drafting

| Decision | Choice | Rationale |
|---|---|---|
| **Model routing** | Haiku for templates ($0.003), Sonnet for complex ($0.02) | 70% of responses are templated (missing info, duplicates). Route to cheapest model. |
| **Context retrieval** | RAG from repo docs | README, CONTRIBUTING.md, past responses, issue templates. Chunk by heading, embed, retrieve top-3 chunks. |
| **Caching** | Redis semantic cache | Cache embeddings of common issue patterns + responses. 73% cost reduction with cache hits. |
| **Safety** | Never auto-post | All drafts require maintainer approval. Log accept/edit/discard for quality tracking. |

### 4.2 Full-Stack Application (Vikram D. & Neha R.)

#### Frontend Architecture

| Decision | Choice | Rationale |
|---|---|---|
| **Framework** | Next.js 15 (App Router) | Server Components for data-heavy pages. Streaming for dashboard sections. |
| **State management** | TanStack Query v5 | Cache invalidation, optimistic updates, background refetch. Prefetch in RSC, hydrate on client. |
| **UI library** | shadcn/ui + Recharts | 50KB gzipped (vs 200KB+ for Tremor). Full Tailwind control. 53+ pre-built chart components. |
| **Auth** | Auth.js v5 (GitHub OAuth) | Unified `auth()` API across server/client. Auto-detects GitHub credentials from env vars. |
| **Performance targets** | LCP <1.5s, FCP <0.8s, CLS <0.1 | React Suspense boundaries for streaming. Dynamic imports for heavy charts. |

#### Key Frontend Patterns

```
Server Component (data fetch, no JS shipped)
  └── Suspense boundary (streaming, loading skeleton)
       └── Client Component (interactive chart, "use client")
            └── TanStack Query (cache, refetch, optimistic updates)
```

### 4.3 Backend & Infrastructure (Karthik M.)

#### API Architecture

| Decision | Choice | Rationale |
|---|---|---|
| **Framework** | FastAPI (async) | Native async, auto-OpenAPI docs, Pydantic validation. Best Python web framework for ML integration. |
| **ORM** | SQLAlchemy 2.0 (async engine) | Production-proven. Native async support. Full Python ecosystem. |
| **Task queue** | Dramatiq + Redis (Python tasks), BullMQ (Node.js tasks) | Dramatiq: 10x faster than RQ, simpler than Celery. BullMQ: native for TypeScript workers. |
| **Migrations** | Alembic | Full Python scripting power. Natural fit with SQLAlchemy. |
| **API versioning** | Path-based (`/api/v1/`) | Simple, explicit. Add `X-API-Deprecation` headers to old versions. |

#### Infrastructure Stack

| Layer | Service | Cost (Early Stage) |
|---|---|---|
| Frontend hosting | Vercel (Pro: $20/mo) | $20/mo |
| Backend hosting | Railway (Pro: $20/mo) | $20/mo |
| PostgreSQL | Railway (included) or Supabase (free) | $0-10/mo |
| Redis | Upstash (free tier: 10K commands/day) | $0/mo |
| LLM APIs | OpenAI + Anthropic | ~$50-200/mo (beta) |
| Monitoring | Sentry + PostHog + Grafana Cloud (free tiers) | $0/mo |
| Email | SendGrid (free: 100 emails/day) | $0/mo |
| Domain + DNS | Cloudflare | $10/yr |
| **Total** | | **~$100-250/mo** |

---

## 5. Technical Standards & Quality Gates

### Code Standards

| Language | Linter | Formatter | Type Checker |
|---|---|---|---|
| TypeScript | ESLint (flat config) | Prettier | `tsc --strict` |
| Python | Ruff (linter + formatter) | Ruff | mypy (strict) |

### PR Requirements

- 1 approval from designated reviewer (domain-specific):
  - ML code → Meera S. approves
  - Frontend → Vikram D. or Neha R. cross-review
  - Backend/infra → Karthik M. or Aravind K. approves
  - Schema changes → Aravind K. approves
- All CI checks green
- No `TODO` without a linked GitHub issue
- Test coverage: >80% for new code (not enforced globally during MVP)

### Commit Convention

```
type(scope): description

Types: feat, fix, refactor, test, docs, chore, perf
Scopes: triage, matching, api, web, ml, infra

Examples:
feat(triage): add duplicate detection with pgvector similarity search
fix(matching): exclude dormant repos from contributor recommendations
test(ml): add golden set evaluation for issue classifier
```

---

## 6. Infrastructure & DevOps

### Environment Strategy

| Environment | Purpose | URL | Deploy Trigger |
|---|---|---|---|
| **Local** | Development | localhost:3000 (web), localhost:8000 (api) | Manual |
| **Staging** | Integration testing | staging.contribhub.dev | Auto on merge to `main` |
| **Production** | Live users | contribhub.dev | Manual tag/release |

### Secrets Management

| Secret | Storage | Rotation |
|---|---|---|
| GitHub App private key | Railway env vars → AWS Secrets Manager (post-MVP) | 90 days |
| Webhook secret | Railway env vars | 90 days |
| Database URL | Railway auto-configured | Never (managed) |
| LLM API keys | Railway env vars | 90 days |
| JWT signing key | Railway env vars | 180 days |

### Disaster Recovery

| Scenario | RTO | RPO | Procedure |
|---|---|---|---|
| Database corruption | <1 hour | <24 hours | Restore from Railway daily backup |
| API service crash | <5 min | 0 (stateless) | Railway auto-restart |
| Redis failure | <10 min | <1 hour | Reconnect; re-process from dead-letter queue |
| GitHub API outage | N/A | 0 | Queue all webhook events; process when restored |
| LLM API outage | <1 min | 0 | Circuit breaker → queue for retry; skip response drafting |

---

## 7. Cost & Budget Projections

### Monthly Engineering Costs (MVP Phase)

| Category | Item | Monthly Cost |
|---|---|---|
| **Infrastructure** | Vercel Pro | $20 |
| | Railway Pro (API + workers + DB + Redis) | $20-50 |
| | Domain (Cloudflare) | ~$1 |
| **AI/ML** | OpenAI API (embeddings + classification fallback) | $50-150 |
| | Anthropic API (response drafting) | $30-100 |
| **Monitoring** | Sentry (free tier) | $0 |
| | PostHog (free tier) | $0 |
| | Grafana Cloud (free tier) | $0 |
| **Dev Tools** | GitHub (free for public repos) | $0 |
| | MLflow (self-hosted on Railway) | $0 |
| | Linear (project management, free for small teams) | $0 |
| **Total** | | **$120-320/mo** |

### LLM Cost Model at Scale

| Scale | Issues/Day | Classification Cost | Embedding Cost | Drafting Cost | Total/Day | Total/Month |
|---|---|---|---|---|---|---|
| **Beta** (500 repos) | 500 | $0.15 (SetFit, self-hosted) | $0.065 | $5 (50% need drafts) | $5.22 | **$157** |
| **Growth** (5K repos) | 5,000 | $1.50 | $0.65 | $50 | $52.15 | **$1,565** |
| **Scale** (50K repos) | 50,000 | $15 | $6.50 | $500 | $521.50 | **$15,645** |

**With caching (60-80% reduction):** Scale cost drops to ~$3,100-6,300/mo.
**With fine-tuned classifier (self-hosted):** Classification cost → near zero. Total at scale: ~$2,000-4,000/mo.

### Team Compensation Budget (if hiring)

| Role | Type | Monthly Cost |
|---|---|---|
| CTO / Tech Lead | Co-founder (equity-heavy) | $8K-12K + 5-10% equity |
| Head of AI/ML | Full-time or contract | $15K-20K + 0.5-1% equity |
| Sr. Full-Stack #1 | Full-time or contract | $12K-18K + 0.25-0.5% equity |
| Sr. Full-Stack #2 | Full-time or contract | $12K-18K + 0.25-0.5% equity |
| Sr. Backend/Infra | Full-time or contract | $12K-18K + 0.25-0.5% equity |
| ML Engineer | Full-time or contract | $10K-15K + 0.1-0.25% equity |
| **Total (6 engineers)** | | **$69K-101K/mo** |

*Note: Ranges reflect US remote rates. India-based engineers reduce costs by 40-60% with comparable skill levels.*

---

## Appendix: Key Technology Decisions Summary

| Decision Area | Choice | Alternative Considered | Why This Won |
|---|---|---|---|
| Monorepo | Turborepo | Nx, Lerna | Faster builds, simpler config, Vercel-native |
| Frontend | Next.js 15 (App Router) | Remix, SvelteKit | RSC for dashboard performance, largest ecosystem |
| UI | shadcn/ui | Tremor, Radix | Smallest bundle (50KB), full customization |
| Backend | FastAPI | Express, NestJS | Best Python ML integration, auto-docs |
| Database | PostgreSQL + pgvector | MongoDB, Supabase | Relational + vector in one DB, proven at scale |
| Task Queue | Dramatiq + BullMQ | Celery, RabbitMQ | Dramatiq: 10x faster than RQ. BullMQ: native TS. |
| Classifier | SetFit → DeBERTa-v3 | GPT-4 fine-tuning, BERT | Best accuracy/cost ratio. 100x cheaper than LLM at scale. |
| Embeddings | text-embedding-3-large | Cohere, BGE-M3 | Top MTEB, flexible dimensions, best API ergonomics |
| Vector Store | pgvector → Qdrant | Pinecone, Weaviate | Zero new infra initially. Qdrant when >10M vectors. |
| Hosting | Vercel + Railway | AWS, GCP, Fly.io | Best DX, lowest ops overhead, cheapest for seed stage |
| Monitoring | Sentry + PostHog + Grafana | Datadog, New Relic | All have generous free tiers. OpenTelemetry for portability. |
| MLOps | MLflow + Evidently + DVC | W&B, Neptune | Free, self-hosted, sufficient for team of 2 ML engineers. |
| Git Strategy | Trunk-based + feature flags | Git Flow | Faster iteration, fewer merge conflicts, continuous deployment. |
| Sprint Methodology | Modified 2-week sprints | Shape Up, Kanban | Structure without ceremony overhead. Switch to Shape Up post-MVP. |
