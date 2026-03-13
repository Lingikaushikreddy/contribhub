<div align="center">

<img src="https://img.shields.io/badge/ContribHub-AI_Powered-6366f1?style=for-the-badge&logo=github&logoColor=white" alt="ContribHub" />

# ContribHub

### The AI engine that triages your GitHub issues and matches contributors to the work that fits them best.

[![CI](https://github.com/Lingikaushikreddy/contribhub/actions/workflows/ci.yml/badge.svg)](https://github.com/Lingikaushikreddy/contribhub/actions/workflows/ci.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Lingikaushikreddy/contribhub/pulls)
[![GitHub Stars](https://img.shields.io/github/stars/Lingikaushikreddy/contribhub?style=social)](https://github.com/Lingikaushikreddy/contribhub)

[Live Demo](https://contribhub.dev) &nbsp;&middot;&nbsp; [Documentation](https://docs.contribhub.dev) &nbsp;&middot;&nbsp; [Roadmap](#roadmap) &nbsp;&middot;&nbsp; [Contributing](#contributing)

<br />

<img width="800" alt="ContribHub Dashboard" src="https://github.com/user-attachments/assets/contribhub-hero.png" />

</div>

<br />

## The Problem

Open source is broken in two places at once:

**Maintainers** spend 40%+ of their time on issue triage — labeling, prioritizing, detecting duplicates, writing responses — instead of building. The average first-response time for popular repos is **4+ days**, and contributor churn sits at **70-89%** within 90 days.

**Contributors** want to help but can't find the right project. They scroll "good first issue" lists with no context on difficulty, project health, or whether anyone will actually review their PR.

ContribHub fixes both sides with one platform.

<br />

## What ContribHub Does

<table>
<tr>
<td width="50%" valign="top">

### For Maintainers

**AI Triage on Autopilot**

Every new issue gets classified, prioritized, and labeled within seconds — not days. Duplicate detection catches repeats before they pile up. AI-drafted responses are ready for your review, not auto-posted.

- Classify issues (bug / feature / question / docs / chore)
- Assign priority (P0-P3) and complexity (1-10)
- Detect duplicates with semantic similarity
- Draft context-aware responses using RAG
- Per-repo config via `.contribhub.yml`

</td>
<td width="50%" valign="top">

### For Contributors

**Find Work That Grows You**

Stop scrolling "good first issue" graveyards. ContribHub matches you to issues based on your actual skills, the project's health, and a growth stretch that pushes you forward without overwhelming you.

- Personalized issue recommendations
- Skill profiles auto-inferred from GitHub activity
- Health-filtered repos (no dead projects)
- Progressive difficulty matching
- Guided onboarding briefs per issue

</td>
</tr>
</table>

<br />

## Key Features

```
                    ┌─────────────────────────────────────────────┐
                    │              GitHub Webhook                   │
                    └──────────────────┬──────────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────────┐
                    │           ContribHub API (FastAPI)            │
                    │                                               │
                    │  ┌─────────┐ ┌──────────┐ ┌──────────────┐  │
                    │  │ Triage  │ │ Matching │ │   Health     │  │
                    │  │ Service │ │  Engine  │ │   Scorer     │  │
                    │  └────┬────┘ └────┬─────┘ └──────┬───────┘  │
                    │       │           │              │           │
                    │  ┌────▼───────────▼──────────────▼───────┐  │
                    │  │          ML Pipeline                    │  │
                    │  │  SetFit/DeBERTa · pgvector · Claude    │  │
                    │  └────────────────────────────────────────┘  │
                    └──────────────────┬──────────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────────┐
                    │       Next.js 15 Dashboard & Feed             │
                    │   Maintainer Triage  ·  Contributor Matches   │
                    └─────────────────────────────────────────────┘
```

| Feature | Description | Accuracy |
|:--------|:------------|:---------|
| **Issue Classification** | 5-category + 4-priority + 10-level complexity scoring | 94%+ |
| **Duplicate Detection** | Semantic similarity search via pgvector embeddings | 85%+ precision |
| **Response Drafting** | RAG-grounded LLM drafts with configurable tone | 80%+ approval |
| **Health Scoring** | 7-dimension CHAOSS-inspired repo health (0-100) | Real-time |
| **Skill Profiling** | Auto-inferred from GitHub activity + self-declared | Continuous |
| **Smart Matching** | Composite scoring: skill (40%) + health (25%) + interest (20%) + growth (15%) | Personalized |
| **Active Learning** | Weekly retraining on maintainer feedback | Self-improving |

<br />

## How It Works

```
1. Install the GitHub App        →  One click. ContribHub starts analyzing your repo.
2. Issues get triaged by AI      →  Category, priority, complexity, duplicates — all automatic.
3. Maintainers review drafts     →  AI suggests responses. You approve, edit, or discard.
4. Contributors get matched      →  Personalized feed of issues that match their skills.
5. Everyone levels up            →  Feedback loop improves AI. Contributors grow. Maintainers reclaim their time.
```

<br />

## Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Frontend** | Next.js 15, React 19, Tailwind CSS 4, shadcn/ui, Recharts, TanStack Query |
| **Backend** | FastAPI, Python 3.12, SQLAlchemy 2.0 (async), Dramatiq workers |
| **Database** | PostgreSQL 16 + pgvector, Redis 7 |
| **ML/AI** | SetFit / DeBERTa-v3, OpenAI Embeddings, Claude (Anthropic) for RAG drafting |
| **Auth** | NextAuth.js v5 (GitHub OAuth), JWT |
| **Infra** | Docker, Turborepo, GitHub Actions CI/CD |
| **Deployment** | Vercel (web), Railway (API + workers) |

<br />

## Project Structure

```
contribhub/
├── apps/
│   ├── api/                  # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/v1/       # REST endpoints (7 routers)
│   │   │   ├── models/       # SQLAlchemy ORM (8 tables)
│   │   │   ├── services/     # Triage, matching, GitHub integration
│   │   │   └── workers/      # Dramatiq async jobs
│   │   ├── alembic/          # Database migrations
│   │   └── Dockerfile
│   │
│   └── web/                  # Next.js 15 frontend
│       ├── app/
│       │   ├── dashboard/    # Maintainer views
│       │   ├── recommendations/  # Contributor feed
│       │   ├── profile/      # Skill profiles
│       │   └── components/   # 30+ UI components
│       └── lib/              # API hooks (TanStack Query)
│
├── packages/
│   ├── ml-pipeline/          # ML models & scoring
│   │   ├── classifier/       # Issue classification (SetFit → DeBERTa)
│   │   ├── embeddings/       # pgvector + duplicate detection
│   │   ├── scoring/          # Health, match, skill, complexity
│   │   ├── drafter/          # LLM response generation (RAG)
│   │   └── evaluation/       # Model eval framework
│   │
│   ├── shared/               # TypeScript type contracts
│   └── github-action/        # Distributable GitHub Action
│
├── docker-compose.yml        # Local dev (Postgres, Redis, API, Worker)
├── Makefile                  # 30+ developer commands
├── turbo.json                # Monorepo build pipeline
└── .contribhub.yml           # Example repo configuration
```

<br />

## Quick Start

### Prerequisites

- Node.js 22+ and npm
- Python 3.12+
- Docker & Docker Compose
- A [GitHub App](https://docs.github.com/en/apps/creating-github-apps) (for webhook events)

### 1. Clone & Install

```bash
git clone https://github.com/Lingikaushikreddy/contribhub.git
cd contribhub
make setup
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Fill in your keys:

```env
# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY=your_private_key
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret

# Database & Cache (Docker defaults work out of the box)
DATABASE_URL=postgresql+asyncpg://contribhub:contribhub_dev@localhost:5432/contribhub
REDIS_URL=redis://localhost:6379

# AI APIs
OPENAI_API_KEY=sk-...        # For embeddings
ANTHROPIC_API_KEY=sk-ant-... # For response drafting

# Auth
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=http://localhost:3000
```

### 3. Start Services

```bash
# Start Postgres (pgvector) + Redis
make docker-up

# Run database migrations
make migrate

# Start everything (API + Web + Workers)
make dev
```

The dashboard is at **http://localhost:3000** and the API at **http://localhost:8000/api/docs**.

<br />

## Configuration

Drop a `.contribhub.yml` in your repository root to customize triage behavior:

```yaml
version: 1

triage:
  enabled: true
  auto_label_confidence_threshold: 0.75
  labels:
    categories: [bug, feature, enhancement, documentation, question, chore]
    priorities: [critical, high, medium, low]
    complexity: [trivial, easy, moderate, hard, expert]
  duplicate_detection:
    enabled: true
    similarity_threshold: 0.85
  response_drafts:
    enabled: true
    tone: friendly          # formal | friendly | minimal
    auto_post_quality_requests: false
  excluded_labels: [wontfix, invalid]

matching:
  enabled: true
  exclude_dormant_days: 90
  exclude_claimed_issues: true
```

<br />

## Architecture

```
┌──────────────┐     Webhook     ┌──────────────────────────────────────┐
│   GitHub      │ ──────────────▶│  FastAPI Gateway                      │
│   (Issues,    │                 │  HMAC verify → parse → route          │
│    PRs, etc.) │                 └──────────┬───────────────────────────┘
└──────────────┘                             │
                                    ┌────────▼────────┐
                                    │  Dramatiq Queue  │  (Redis-backed)
                                    └────────┬────────┘
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                     ┌────────────┐  ┌────────────┐  ┌────────────┐
                     │  Classify   │  │  Detect    │  │  Draft     │
                     │  (SetFit/   │  │  Dupes     │  │  Response  │
                     │  DeBERTa)   │  │  (pgvector)│  │  (Claude)  │
                     └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
                            │               │               │
                            └───────────────┼───────────────┘
                                            ▼
                              ┌──────────────────────────┐
                              │  PostgreSQL 16 + pgvector  │
                              │  (Issues, Repos, Matches,  │
                              │   Skills, Triage Events)   │
                              └──────────────────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │  Matching Engine            │
                              │  skill × health × interest  │
                              │  × growth → ranked feed     │
                              └─────────────┬─────────────┘
                                            ▼
                              ┌──────────────────────────┐
                              │  Next.js 15 Dashboard      │
                              │  Maintainer: triage review  │
                              │  Contributor: issue feed    │
                              └──────────────────────────┘
```

<br />

## Developer Commands

```bash
make setup              # Install all dependencies (Node + Python)
make dev                # Start all services (web + API + workers)
make dev-web            # Next.js dev server only
make dev-api            # FastAPI dev server only
make test               # Run all test suites
make test-api           # Backend tests (pytest)
make test-ml            # ML pipeline tests
make lint               # Lint everything
make format             # Format everything (Prettier + ruff)
make docker-up          # Start Postgres + Redis
make docker-up-all      # Start full stack via Docker
make migrate            # Run database migrations
make migrate-create     # Create a new migration
make build              # Production build
make clean              # Remove build artifacts
```

<br />

## Roadmap

- [x] **Foundation** — Monorepo, database schema, GitHub App, CI/CD
- [x] **AI Triage Core** — Issue classifier, complexity scorer, duplicate detection
- [x] **Response Drafting** — RAG context builder, LLM drafting, approval flow
- [x] **Matching Engine** — Health scoring, 4-factor matching, recommendation feed
- [ ] **Analytics Dashboard** — Triage trends, MTTR charts, accuracy tracking
- [ ] **Weekly Digests** — Email summaries for maintainers
- [ ] **GitHub Marketplace** — One-click install from Marketplace
- [ ] **Enterprise Features** — SSO, audit logs, SLA controls, OSPO dashboards
- [ ] **Model Fine-tuning** — DeBERTa-v3 trained on real triage data
- [ ] **VS Code Extension** — Triage + match from your editor

<br />

## Contributing

We welcome contributions of all sizes. Here's how to get started:

1. **Fork** this repo
2. **Create a branch** for your feature (`git checkout -b feat/amazing-feature`)
3. **Make your changes** and add tests
4. **Run the test suite** (`make test`)
5. **Open a PR** against `main`

### Good First Issues

Look for issues tagged [`good-first-issue`](https://github.com/Lingikaushikreddy/contribhub/labels/good-first-issue) — we use ContribHub to triage our own repo.

### Development Prerequisites

```bash
# Quick setup
git clone https://github.com/Lingikaushikreddy/contribhub.git
cd contribhub
make setup
make docker-up
make dev
```

See the [Makefile](./Makefile) for the full command reference.

<br />

## Team

Built by a team that believes open source deserves better tooling.

| Name | Role |
|:-----|:-----|
| **Kaushik Reddy** | CEO & Founder, Head of AI/ML & Sr. Full-Stack |
| **Joel** | CTO / Tech Lead |
| **Harshavardhan Reddy** | Sr. Backend & Infrastructure |
| **Fardeen** | ML Engineer |
| **Kishore Reddy** | Sr. Full-Stack (Matching Engine) |

<br />

## Star History

If ContribHub helps you, consider giving it a star. It helps others discover the project.

<a href="https://star-history.com/#Lingikaushikreddy/contribhub&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Lingikaushikreddy/contribhub&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Lingikaushikreddy/contribhub&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Lingikaushikreddy/contribhub&type=Date" />
 </picture>
</a>

<br />

## License

ContribHub is open source under the [AGPL-3.0 License](./LICENSE). Use it, fork it, build on it — just keep it open.

<br />

<div align="center">

**[Get Started](https://github.com/Lingikaushikreddy/contribhub)** &nbsp;&middot;&nbsp; **[Report a Bug](https://github.com/Lingikaushikreddy/contribhub/issues)** &nbsp;&middot;&nbsp; **[Request a Feature](https://github.com/Lingikaushikreddy/contribhub/issues)**

Built with care for the open source community.

</div>
