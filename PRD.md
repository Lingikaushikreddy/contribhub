# ContribHub — Intelligent Contributor Triage & Community Orchestrator
## Product Requirements Document (PRD)

**Document Version:** 1.0
**Status:** Draft — Founder Review
**Owner:** Kaushik Reddy, CEO & Founder
**Last Updated:** March 13, 2026

---

## Table of Contents

1. [Executive Summary & Vision](#1-executive-summary--vision)
2. [Problem Statement](#2-problem-statement)
3. [User Personas](#3-user-personas)
4. [Market Analysis](#4-market-analysis)
5. [Competitive Landscape](#5-competitive-landscape)
6. [Goals & Non-Goals](#6-goals--non-goals)
7. [Success Metrics & KPIs](#7-success-metrics--kpis)
8. [Proposed Solution](#8-proposed-solution)
9. [Feature Requirements](#9-feature-requirements)
10. [MVP vs Full Product Scope](#10-mvp-vs-full-product-scope)
11. [Technical Architecture & Constraints](#11-technical-architecture--constraints)
12. [Design & UX Requirements](#12-design--ux-requirements)
13. [Go-to-Market Strategy](#13-go-to-market-strategy)
14. [Business Model & Pricing](#14-business-model--pricing)
15. [Risks, Assumptions & Dependencies](#15-risks-assumptions--dependencies)
16. [Timeline & Milestones](#16-timeline--milestones)
17. [Appendix](#17-appendix)

---

## 1. Executive Summary & Vision

### The Future Press Release (Amazon Working Backwards)

> **ContribHub Launches AI-Powered Platform That Matches Open-Source Contributors to Projects — Cutting Maintainer Triage Time by 70%**
>
> *San Francisco, CA — ContribHub, the intelligent open-source orchestration platform, today announced general availability of its dual-sided marketplace that uses AI to automatically triage GitHub issues for maintainers while intelligently matching contributors to projects that fit their skill level, interests, and career goals.*
>
> *"Before ContribHub, I spent 15+ hours a week just categorizing issues and asking reporters for reproduction steps," said a lead maintainer of a 40K-star project. "Now the AI handles 90% of that, and the contributors showing up actually have the right skills for the issues they pick up. My merge rate has tripled."*
>
> *For contributors, ContribHub eliminates the frustration of discovering that a "good first issue" actually requires 3 years of systems programming knowledge, or that the repository hasn't had a commit in 18 months. The platform's Skill-Issue Matching Engine analyzes codebase complexity, prerequisite knowledge, and project health to surface genuinely accessible opportunities.*

### Vision Statement

ContribHub exists to **fix the broken bridge between open-source maintainers drowning in operational overhead and contributors struggling to find meaningful projects** — by deploying AI agents that handle triage drudgery and a matching engine that treats contributor growth as a first-class outcome.

### Strategic Alignment

- **Market timing:** GitHub's Agentic Workflows (Feb 2026) validated the category but remains in limited technical preview — the window to build a superior, community-centric product is now.
- **Secular trends:** 180M+ GitHub developers (growing 1/second), AI code tooling market exploding from $7.4B → $24B by 2030, maintainer burnout at crisis levels (60% quit or considered quitting).
- **Founder-market fit:** Deep experience in AI infrastructure (Aegis) and production GitHub integrations.

---

## 2. Problem Statement

### The Maintainer Crisis

Open-source maintainers are the unpaid backbone of the global software supply chain. Their situation has reached a breaking point:

| Data Point | Source |
|---|---|
| **60%** of maintainers are unpaid | Tidelift 2024 Survey (n=400+) |
| **60%** have quit or considered quitting | Tidelift 2024 |
| **44%** cite burnout as primary reason | Tidelift 2024 |
| **61%** of unpaid maintainers work solo | Tidelift 2024 |
| **50%** of maintainer time goes to day-to-day maintenance (not new features) | Tidelift/Sonar |
| **60%** of maintainers want help with issue triage | Tidelift 2024 |
| **30%** need duplicate detection specifically | Tidelift 2024 |

Maintainers receive bug reports with no version numbers, no reproduction steps, no expected vs. actual behavior. The Rails core team (~7 people) managed ~700 issues where each question took 5-10 minutes but volume made it "unreasonable" (GitHub Blog). They spend more time chasing details than solving problems.

### The Contributor Paradox

On the other side, an unprecedented wave of developers wants to contribute but can't find the right entry points:

| Data Point | Source |
|---|---|
| **255,000** first-time contributors in March 2025 alone (single-month record) | GitHub Octoverse 2025 |
| **Only 14%** of "good first issues" are actually solved by newcomers | ACM Study (n=9,368 GFIs, 816 projects) |
| **40.9%** of GFIs are never solved by newcomers at all | ACM Study |
| **67%** of GitHub projects are dormant | Livable Software |
| **59.7%** of projects lose 30%+ of contributors annually | CMU STRUDEL Lab |
| Junior dev job postings **dropped ~40%** vs. pre-2022 levels | Nucamp 2026 Report |

Existing discovery platforms (CodeTriage, Up For Grabs, Good First Issues) are **static aggregators** — they list issues by label without analyzing actual difficulty, project health, or contributor fit. They routinely surface abandoned repositories and mislabeled issues.

### Why Now

1. **AI maturity:** Auto-labeling accuracy has reached 92% in production; semantic duplicate detection hits 84-97% F1 — the technology is ready.
2. **GitHub validation:** GitHub's own Agentic Workflows (Feb 2026) proves the category, but it's a horizontal feature, not a focused product.
3. **Economic pressure:** Junior devs face a 40% tighter job market; open-source contributions are now a key hiring differentiator.
4. **Corporate OSPO budgets:** Median organization invests $520K/year in open-source (Linux Foundation 2024) — there's paying demand.

---

## 3. User Personas

### Primary Persona 1: The Overwhelmed Maintainer

**Name:** Priya, 34, Lead Maintainer of an open-source observability framework (22K GitHub stars)
**Team:** 3 core maintainers, ~40 occasional contributors
**Context:** Works full-time at a startup; maintains the project evenings/weekends

- **Goals:** Reduce triage burden from 15 hrs/week to <3 hrs; attract quality contributors who can eventually become co-maintainers; keep the project alive without burning out.
- **Pain Points:** 70% of new issues are missing reproduction steps or are duplicates. "Good first issue" labels are arbitrary — she doesn't have time to assess true difficulty. She's lost 3 promising contributors because they picked issues that were too hard and got discouraged.
- **Current Workflow:** Manually reads every issue → asks for details → labels → assigns priority → responds. Uses Stale Bot to auto-close inactive issues (a blunt instrument that angers users).
- **Quote:** *"I didn't start this project to become a customer support agent. I want to write code."*

### Primary Persona 2: The Aspiring Contributor

**Name:** Arjun, 23, Recent CS graduate in Bangalore, looking for his first developer role
**Context:** Strong in Python/JavaScript, some React experience. Has completed tutorials but no real-world project experience. Needs portfolio pieces that demonstrate collaboration skills.

- **Goals:** Build a credible open-source contribution portfolio; learn real-world engineering practices (code review, testing, CI/CD); get noticed by potential employers.
- **Pain Points:** Spent 3 weeks searching Good First Issues across 20+ repos — 6 were abandoned, 4 required deep domain knowledge (despite the label), 3 had PRs already in progress, and 2 maintainers never responded. Wasted 40+ hours with zero merged PRs to show.
- **Current Workflow:** Browses GitHub Explore → filters by "good first issue" label → reads README → tries to understand codebase → gives up or submits low-quality PR.
- **Quote:** *"Every 'beginner-friendly' issue I find either requires 5 years of experience or the repo is dead. I just want to contribute somewhere my PR will actually get reviewed."*

### Secondary Persona: The Engineering Manager at an Enterprise OSPO

**Name:** Sarah, 38, Director of Open Source Program Office at a Fortune 500 fintech
**Context:** Manages corporate policy on open-source contributions. Budget of $500K/year. Needs to track which employees contribute to which projects and ensure compliance.

- **Goals:** Identify high-impact projects for corporate sponsorship; direct engineering time toward strategically important OSS dependencies; measure contribution ROI.
- **Pain Points:** No visibility into which of their 200 OSS dependencies need help; can't efficiently match internal engineers to external projects; compliance tracking is manual.
- **Quote:** *"We have 50 engineers who want to contribute upstream, but we can't figure out where to point them."*

---

## 4. Market Analysis

### TAM / SAM / SOM (Bottom-Up)

#### Total Addressable Market (TAM): $4.2B

| Segment | Calculation | Market Size |
|---|---|---|
| **AI Issue Triage** (maintainer side) | 28M active public repos × 15% with regular issues × $50/mo avg | $2.52B |
| **Contributor Matching** (contributor side) | 180M developers × 5% active contributors × $5/mo avg | $540M |
| **Enterprise OSPO Tools** | 50,000 orgs with OSS programs × $24K/yr avg | $1.2B |
| **Total TAM** | | **$4.26B** |

#### Serviceable Addressable Market (SAM): $680M

Filtered by: English-language repos, projects with >100 stars, developers in US/EU/India, companies with >200 employees.

| Segment | Calculation | Market Size |
|---|---|---|
| **AI Issue Triage** | 800K qualifying repos × $40/mo avg | $384M |
| **Contributor Matching** | 4M active job-seeking contributors × $3/mo avg | $144M |
| **Enterprise OSPO** | 6,000 qualifying orgs × $25K/yr avg | $150M |
| **Total SAM** | | **$678M** |

#### Serviceable Obtainable Market (SOM): $8.5M (18 months)

| Segment | Calculation | Revenue |
|---|---|---|
| **Free tier repos** (growth engine) | 50,000 repos (free) | $0 |
| **Paid maintainer plans** | 2,000 repos × $120/mo avg | $2.88M |
| **Contributor Pro** | 15,000 contributors × $8/mo | $1.44M |
| **Enterprise contracts** | 20 orgs × $210K/yr avg | $4.20M |
| **Total SOM (18-month)** | | **$8.52M ARR** |

### Market Tailwinds

1. **AI Code Tools:** $7.37B (2025) → $23.97B (2030), 26.6% CAGR (Grand View Research)
2. **Open-Source Services:** $38B (2025) → $44B (2026), 16-19% CAGR (Mordor Intelligence)
3. **GitHub Actions usage:** 11.5B minutes in 2025 (+35% YoY), 71M jobs/day
4. **Enterprise OSS adoption:** 96% of organizations increased or maintained OSS use (Canonical 2025)
5. **GitHub Copilot proving willingness to pay:** 4.7M paid subscribers, $10-39/user/month

---

## 5. Competitive Landscape

### Direct Competitors

| Player | What They Do | Strength | Weakness |
|---|---|---|---|
| **GitHub Agentic Workflows** | AI auto-triage in GitHub Actions (technical preview, Feb 2026) | Native GitHub integration, massive distribution | Preview-only, horizontal feature (not focused product), no contributor matching |
| **CodeTriage** | Lists repos by open issue count | Simple, established | Static aggregator, no AI, no skill matching, no health scoring |
| **OpenSauced** | Contributor analytics and discovery | Developer insights, OSCR rating | Analytics-focused, not a matching marketplace |
| **Up For Grabs / Good First Issues** | Curated issue lists | Community-driven, free | No AI, no difficulty validation, surfaces dead repos |
| **CodeRabbit** | AI-powered PR code review | $15M ARR, 2M+ repos, $550M valuation | PR review only — doesn't touch issue triage or contributor matching |

### Where ContribHub Wins

```
                    Issue Triage Intelligence
                           ▲
                           │
                    ContribHub ★
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    GitHub Agentic    CodeRabbit       Aptu/Bots
     Workflows            │               │
           │               │               │
           └───────────────┼───────────────┘
                           │
    CodeTriage ────────────┼──────────── OpenSauced
    Up For Grabs           │
    Good First Issues      │
                           ▼
                Contributor Matching Intelligence
```

**ContribHub is the only platform that occupies BOTH axes** — intelligent issue triage for maintainers AND intelligent contributor matching. Every competitor addresses one side or the other, never both.

### Moat Assessment

| Moat Type | ContribHub Strategy |
|---|---|
| **Data Network Effects** | Every issue triaged improves the AI model. Every successful match improves the recommendation engine. More maintainers → more issues → better matching → more contributors → faster resolution → more maintainers. |
| **Switching Costs** | Deep integration into GitHub workflows (Actions, webhooks, issue templates). Historical triage data becomes valuable institutional knowledge. Contributor reputation scores are non-portable. |
| **Proprietary Data** | Issue-resolution outcome data (which contributors successfully resolved which issue types), codebase complexity graphs, contributor skill trajectories — none of this exists in any other system. |
| **Brand/Community** | First-mover in the "contributor orchestrator" category. Community-driven contributor reputation system creates belonging. |

---

## 6. Goals & Non-Goals

### Goals

| # | Goal | Business Outcome |
|---|---|---|
| G1 | Reduce maintainer triage time by 70% within 90 days of adoption | Retention: maintainers stay active, projects survive |
| G2 | Achieve 3x higher first-PR merge rate for matched contributors vs. organic discovery | Growth: contributors succeed → word-of-mouth → viral adoption |
| G3 | Reach 50,000 repos and 100,000 contributors in 12 months | Scale: build the data flywheel |
| G4 | Close 20 enterprise OSPO contracts within 18 months | Revenue: path to $8.5M ARR |
| G5 | Become the default "CONTRIBUTING.md → ContribHub" link in top 1,000 GitHub projects | Distribution: organic acquisition channel |

### Non-Goals (Explicit)

| # | Non-Goal | Rationale |
|---|---|---|
| NG1 | We will NOT build a full code review tool | CodeRabbit ($550M valuation) owns this. We complement, not compete. |
| NG2 | We will NOT support GitLab/Bitbucket in V1 | GitHub has 180M developers. Focus beats fragmentation. |
| NG3 | We will NOT build a job board or hiring platform | This is a contributor growth platform, not a recruiter tool. Hiring features would poison community trust. |
| NG4 | We will NOT replace GitHub Issues/Projects | We augment the existing workflow, not create a parallel system. |
| NG5 | We will NOT handle payment/bounty systems in V1 | Complexity explosion. Integrate with existing bounty platforms (Algora, Bountysource) instead. |
| NG6 | We will NOT build a mobile app | Contributors and maintainers work on desktop. Web-first. |

---

## 7. Success Metrics & KPIs

### North Star Metric

**Successful Matches per Month** — defined as a contributor matched by ContribHub who has their PR merged within 30 days.

### Primary Metrics

| Metric | Baseline (Industry) | Target (6 months) | Target (12 months) |
|---|---|---|---|
| **Maintainer triage time saved** | 15 hrs/week | 10 hrs/week saved (70%) | 12 hrs/week saved (80%) |
| **AI auto-label accuracy** | 78% (zero-shot) | 92% | 95% |
| **Duplicate detection precision** | 60% (GenAI baseline) | 85% | 92% |
| **First-PR merge rate (matched)** | 14% (GFI industry avg) | 42% (3x) | 55% (4x) |
| **Contributor 90-day retention** | 11-31% (industry) | 45% | 60% |
| **Time to first meaningful PR** | Weeks (organic) | <72 hours | <48 hours |
| **Repos onboarded** | 0 | 20,000 | 50,000 |
| **Active contributors** | 0 | 40,000 | 100,000 |
| **Enterprise contracts** | 0 | 5 | 20 |
| **ARR** | $0 | $1.2M | $8.5M |

### Health Metrics

| Metric | Target |
|---|---|
| Maintainer NPS | >50 |
| Contributor NPS | >60 |
| AI false positive rate (labels) | <5% |
| Median response draft time | <60 seconds |
| System uptime | 99.9% |

---

## 8. Proposed Solution

### Solution Overview

ContribHub is a **dual-sided AI orchestration platform** deployed as a GitHub App + web dashboard:

**For Maintainers** — an AI-powered GitHub Action that:
- Automatically triages incoming issues by analyzing semantic content, codebase context, and historical patterns
- Appends categorical labels (bug/feature/question/docs), priority (P0-P3), and complexity scores
- Identifies and links duplicate submissions with confidence scores
- Drafts suggested responses (requesting reproduction steps, thanking reporters, explaining workarounds)
- Surfaces which issues are genuinely suitable for newcomers based on actual codebase analysis (not just labels)
- Generates weekly triage reports with burndown analytics

**For Contributors** — an intelligent matching engine that:
- Builds a skill profile from their GitHub activity, language proficiency, and self-declared interests
- Analyzes issue difficulty using AST complexity analysis, file coupling, prerequisite knowledge inference, and historical resolution patterns
- Scores project health (commit frequency, response time, merge rate, contributor retention) to filter out dead repos
- Recommends issues ranked by fit: skill match × interest alignment × project health × growth potential
- Provides guided onboarding: "Here's the issue, here's the relevant code, here's what you need to know to solve it"
- Tracks their growth trajectory and progressively suggests more challenging contributions

**The Flywheel:** Better triage → cleaner issues → better matching → higher merge rates → happier maintainers who stay active → more healthy projects → more contributor matches → more data → better AI.

---

## 9. Feature Requirements

### Epic 1: AI Issue Triage Engine (Maintainer Side)

#### F1.1 — Semantic Issue Analysis
**User Story:** As a maintainer, I want incoming issues automatically analyzed so that I spend time solving problems, not categorizing them.

**Acceptance Criteria:**
- When a new issue is created, the system analyzes title + body within 30 seconds
- System assigns category labels: `bug`, `feature-request`, `question`, `documentation`, `enhancement`, `chore`
- System assigns priority: `P0-critical`, `P1-high`, `P2-medium`, `P3-low`
- System assigns complexity score: `beginner` (1-2), `intermediate` (3-5), `advanced` (6-8), `expert` (9-10)
- Complexity score is based on actual codebase analysis (files likely affected, cyclomatic complexity, dependency depth)
- All auto-labels include a confidence percentage; labels below 70% confidence are marked as `needs-review`
- Maintainer can correct labels; corrections feed back into the model

**Priority:** Must Have (MVP)

#### F1.2 — Duplicate Detection
**User Story:** As a maintainer, I want duplicate issues automatically identified so that discussion stays consolidated.

**Acceptance Criteria:**
- System compares new issues against open issues using semantic similarity (not just keyword matching)
- When similarity score >80%, system comments on the new issue: "This may be related to #[number] — [linked title]. If this is a duplicate, the maintainer will consolidate these issues."
- When similarity score >95%, system auto-labels as `possible-duplicate` and notifies maintainer
- Maintainer can confirm (auto-close with link) or dismiss (issue excluded from future duplicate matches against this pair)
- F1 score target: >85% within 90 days of deployment on a given repo

**Priority:** Must Have (MVP)

#### F1.3 — Intelligent Response Drafting
**User Story:** As a maintainer, I want draft responses generated for common issue patterns so that I can respond in seconds instead of minutes.

**Acceptance Criteria:**
- System drafts a response based on issue type:
  - **Bug missing info:** Asks for OS, version, reproduction steps, expected/actual behavior
  - **Feature request:** Acknowledges, asks for use case, links to related discussions
  - **Question:** Points to relevant docs/wiki pages with specific section links
  - **Duplicate:** Links to original issue with summary of current status
- Drafts are posted as a PR review suggestion (maintainer approves/edits/discards before posting)
- Response drafts are NEVER auto-posted — always require maintainer approval
- Tone is configurable: formal, friendly, minimal

**Priority:** Must Have (MVP)

#### F1.4 — Issue Quality Scoring
**User Story:** As a maintainer, I want issues scored for completeness so that I can prioritize well-documented reports.

**Acceptance Criteria:**
- System scores each issue 0-100 on completeness: reproduction steps, environment info, error logs, screenshots, expected vs. actual behavior
- Issues scoring <40 get a polite auto-comment requesting missing information (using the repo's issue template as the standard)
- Issues scoring >80 get a `well-documented` label as positive reinforcement
- Scoring criteria are visible to reporters so they can self-improve

**Priority:** Should Have (V1.1)

#### F1.5 — Triage Dashboard & Analytics
**User Story:** As a maintainer, I want a dashboard showing triage metrics so that I can understand my project's health.

**Acceptance Criteria:**
- Weekly email digest: new issues, resolved, average response time, top contributors
- Dashboard shows: issue volume trends, category breakdown, mean time to first response, mean time to close, contributor activity heatmap
- Exportable reports for OSPO compliance

**Priority:** Should Have (V1.1)

---

### Epic 2: Contributor Matching Engine (Contributor Side)

#### F2.1 — Skill Profile Builder
**User Story:** As a contributor, I want the platform to understand my skills so that I get relevant issue recommendations.

**Acceptance Criteria:**
- System analyzes GitHub profile: languages used, repo contributions, PR complexity, review activity
- Contributor can self-declare: interests (domains like web, ML, DevOps), preferred languages, experience level
- Skill graph is built using knowledge-graph embeddings (inspired by LinkedIn's Skills Graph architecture)
- Profile updates automatically as contributor activity changes
- Contributor can see and edit their inferred skill profile

**Priority:** Must Have (MVP)

#### F2.2 — Issue-Skill Matching
**User Story:** As a contributor, I want to see issues that match my current skill level and interests so that I can contribute successfully.

**Acceptance Criteria:**
- System recommends top 10 issues daily, ranked by composite score: skill match (40%) × project health (25%) × interest alignment (20%) × growth stretch (15%)
- Each recommendation includes: issue summary, estimated difficulty, prerequisite skills, estimated time investment, project health score, recent maintainer response time
- Contributor can thumbs-up/thumbs-down recommendations to improve future matches
- Zero recommendations from repos with <1 commit in last 90 days (dormant filter)
- Zero recommendations from issues with existing open PRs (claimed filter)

**Priority:** Must Have (MVP)

#### F2.3 — Project Health Scoring
**User Story:** As a contributor, I want to know if a project is healthy before I invest time contributing.

**Acceptance Criteria:**
- Health score (0-100) based on CHAOSS-inspired metrics:
  - Commit frequency (last 90 days)
  - PR review turnaround time (median)
  - Issue response time (median)
  - Contributor retention rate (12-month)
  - Release cadence
  - Community files present (CONTRIBUTING.md, CODE_OF_CONDUCT.md, issue templates)
- Score displayed prominently on every project and issue recommendation
- Projects scoring <30 are excluded from contributor recommendations
- Methodology is transparent and publicly documented

**Priority:** Must Have (MVP)

#### F2.4 — Guided Contribution Onboarding
**User Story:** As a first-time contributor, I want step-by-step guidance for my chosen issue so that I can submit a quality PR.

**Acceptance Criteria:**
- When a contributor selects an issue, system generates a "Contribution Brief":
  - Relevant source files to read (with direct GitHub links)
  - Key functions/classes involved
  - Related tests to understand expected behavior
  - Setup instructions (extracted from CONTRIBUTING.md + Dockerfile analysis)
  - Suggested approach (high-level, not code)
- Brief is generated within 60 seconds
- Brief is presented in a clean, distraction-free reading view
- Links to the project's CONTRIBUTING.md and development setup docs

**Priority:** Should Have (V1.1)

#### F2.5 — Contributor Reputation & Growth Tracking
**User Story:** As a contributor, I want to track my growth and build a portable reputation so that my contributions are recognized.

**Acceptance Criteria:**
- Contribution history: issues attempted, PRs merged, review feedback received
- Skill progression: visualization of skills gained over time
- Growth trajectory: system suggests progressively harder issues as skills improve
- Public profile page (opt-in) that can be linked from resumes/portfolios
- No leaderboards or competitive ranking — growth is personal, not competitive

**Priority:** Could Have (V1.2)

---

### Epic 3: Platform & Integration

#### F3.1 — GitHub App Installation
**User Story:** As a maintainer, I want to install ContribHub in 2 clicks and have it working immediately.

**Acceptance Criteria:**
- GitHub Marketplace listing with one-click install
- OAuth flow grants required permissions: issues (read/write), pull requests (read), repository contents (read)
- Default configuration works out-of-the-box; advanced config via `.contribhub.yml` in repo root
- First triage results appear within 5 minutes of installation on existing open issues

**Priority:** Must Have (MVP)

#### F3.2 — Configuration & Customization
**User Story:** As a maintainer, I want to customize triage behavior to match my project's conventions.

**Acceptance Criteria:**
- `.contribhub.yml` supports:
  - Custom label taxonomy (mapping ContribHub categories to project-specific labels)
  - Auto-response tone (formal/friendly/minimal)
  - Duplicate detection sensitivity threshold (0-100)
  - Excluded labels (issues with certain labels are skipped)
  - Team member allowlist (skip triage for trusted reporters)
- Changes take effect on next issue event (no restart needed)

**Priority:** Must Have (MVP)

#### F3.3 — Web Dashboard
**User Story:** As a user (maintainer or contributor), I want a web dashboard for features that don't fit in GitHub's UI.

**Acceptance Criteria:**
- GitHub OAuth login (no separate account creation)
- Maintainer view: triage analytics, configuration UI, AI accuracy feedback
- Contributor view: skill profile, issue recommendations, contribution history, growth tracking
- Responsive web design (desktop-first, functional on tablet)

**Priority:** Must Have (MVP)

---

## 10. MVP vs Full Product Scope

### MVP (Weeks 1-12) — "Prove the Triage"

**Goal:** Validate that AI triage saves maintainer time and that skill-based matching increases PR merge rates.

**Scope:**
- AI Issue Triage: auto-labeling (F1.1), duplicate detection (F1.2), response drafting (F1.3)
- Contributor Matching: skill profiling (F2.1), issue-skill matching (F2.2), project health scoring (F2.3)
- Platform: GitHub App (F3.1), basic config (F3.2), web dashboard (F3.3)
- Free for all users during MVP beta

**Success Criteria for MVP:**
- 500+ repos installed
- 5,000+ contributors signed up
- Auto-label accuracy >88%
- 3x improvement in matched contributor merge rate vs. organic
- Qualitative: 10+ maintainer testimonials

### V1.1 (Months 4-6) — "Deepen Value"

- Issue quality scoring (F1.4)
- Triage dashboard & analytics (F1.5)
- Guided contribution onboarding (F2.4)
- Paid plans launch (maintainer Pro, contributor Pro)
- Enterprise pilot program begins

### V1.2 (Months 7-12) — "Scale & Monetize"

- Contributor reputation system (F2.5)
- Enterprise OSPO dashboard (multi-repo management, compliance reporting, contribution tracking)
- API access for programmatic integration
- Webhook notifications (Slack, Discord, email)
- Advanced AI: auto-assign issues to specific contributors, PR quality prediction
- Bounty platform integrations (Algora, Open Collective)

### V2.0 (Months 13-18) — "Platform Effects"

- Maintainer-to-maintainer collaboration (shared triage rules, cross-project insights)
- Organization-level analytics (CNCF, Apache Foundation dashboards)
- GitLab support
- Contributor mentorship matching (pair experienced contributors with newcomers)
- Open API ecosystem for third-party extensions

---

## 11. Technical Architecture & Constraints

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GITHUB ECOSYSTEM                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Issues   │  │  Pull Reqs   │  │  Repo Contents    │  │
│  └─────┬────┘  └──────┬───────┘  └────────┬──────────┘  │
│        │               │                   │             │
│        └───────────────┼───────────────────┘             │
│                        │ Webhooks + GitHub API           │
└────────────────────────┼────────────────────────────────┘
                         ▼
┌────────────────────────────────────────────────────────────┐
│                   CONTRIBHUB PLATFORM                      │
│                                                            │
│  ┌──────────────┐    ┌─────────────────────────────────┐   │
│  │  Webhook      │    │       AI/ML Pipeline             │   │
│  │  Gateway      │───▶│  ┌────────────┐  ┌───────────┐ │   │
│  │  (FastAPI)    │    │  │ Classifier  │  │ Embeddings│ │   │
│  └──────────────┘    │  │ (Labels,    │  │ (Issue    │ │   │
│                       │  │  Priority,  │  │  vectors, │ │   │
│                       │  │  Complexity)│  │  dedup)   │ │   │
│                       │  └────────────┘  └───────────┘ │   │
│                       │  ┌────────────┐  ┌───────────┐ │   │
│                       │  │ Response   │  │ Complexity │ │   │
│                       │  │ Drafter    │  │ Analyzer   │ │   │
│                       │  │ (LLM)     │  │ (AST/Code) │ │   │
│                       │  └────────────┘  └───────────┘ │   │
│                       └─────────────────────────────────┘   │
│                                                            │
│  ┌──────────────┐    ┌─────────────────────────────────┐   │
│  │  Matching     │    │       Data Layer                 │   │
│  │  Engine       │    │  ┌────────────┐  ┌───────────┐ │   │
│  │  (Skill ×    │    │  │ PostgreSQL │  │ Vector DB │ │   │
│  │   Issue ×    │    │  │ (Users,    │  │ (Qdrant/  │ │   │
│  │   Health)    │    │  │  Repos,    │  │  Pinecone)│ │   │
│  └──────────────┘    │  │  Issues)   │  │           │ │   │
│                       │  └────────────┘  └───────────┘ │   │
│  ┌──────────────┐    │  ┌────────────┐  ┌───────────┐ │   │
│  │  Web App      │    │  │ Redis      │  │ S3/GCS    │ │   │
│  │  (Next.js)    │    │  │ (Cache,    │  │ (Logs,    │ │   │
│  │               │    │  │  Queues)   │  │  Models)  │ │   │
│  └──────────────┘    │  └────────────┘  └───────────┘ │   │
│                       └─────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **API Gateway** | Python FastAPI | Async, high performance, excellent for webhook processing |
| **AI/ML** | OpenAI GPT-4o / Claude API + fine-tuned models | GPT-4o for classification (68.5% baseline, tunable to 92%+); Claude for response drafting |
| **Embeddings** | OpenAI text-embedding-3-large + Qdrant | Semantic search for duplicate detection and skill matching |
| **Code Analysis** | Tree-sitter (AST parsing) + custom complexity scorer | Language-agnostic codebase complexity analysis |
| **Web Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS | Fast SSR, modern DX, consistent with modern dev tooling |
| **Database** | PostgreSQL 16 (Supabase) | Relational data, full-text search, proven at scale |
| **Vector Store** | Qdrant (self-hosted) or Pinecone (managed) | Purpose-built for similarity search at scale |
| **Cache/Queue** | Redis + BullMQ | Job queue for async issue processing, caching for API rate limits |
| **Infrastructure** | Vercel (frontend) + Railway/Fly.io (API) + GCP (ML) | Cost-efficient, auto-scaling, developer-friendly |
| **CI/CD** | GitHub Actions | Dogfooding — we use what our users use |
| **Monitoring** | Sentry (errors) + PostHog (analytics) + Grafana (infra) | Full observability stack |

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| **Triage latency** | <30 seconds from issue creation to labels applied |
| **Duplicate detection latency** | <60 seconds |
| **Response draft generation** | <15 seconds |
| **API uptime** | 99.9% (43 min downtime/month max) |
| **Concurrent repos** | Support 50,000 repos with spiky webhook traffic |
| **GitHub API rate management** | Stay within 5,000 req/hr/user with intelligent batching and caching |
| **Data retention** | Issue metadata: indefinite. Full issue text: 90 days (re-fetch from GitHub on demand) |
| **Security** | SOC 2 Type I by Month 9. No storage of source code — only AST metadata and embeddings |
| **Privacy** | GDPR compliant. Contributor profiles are opt-in. Right to deletion honored within 72 hours |

### Key Technical Constraints

1. **GitHub API Rate Limits:** 5,000 requests/hour (authenticated). Must use webhooks (not polling), aggressive caching, and GraphQL batching.
2. **No Source Code Storage:** ContribHub NEVER stores raw source code. Only AST-derived metadata and embeddings. This eliminates IP liability and simplifies security posture.
3. **LLM Cost Management:** At 50K repos with 10 issues/day average = 500K issue analyses/day. Must use tiered approach: fast classifier (fine-tuned BERT) for labeling, LLM only for response drafting.
4. **Webhook Reliability:** GitHub webhooks have no guaranteed delivery. Must implement idempotent processing and periodic reconciliation.

---

## 12. Design & UX Requirements

### Key User Flows

#### Flow 1: Maintainer Installs ContribHub (2 minutes)

```
GitHub Marketplace → "Install" → Select repos → Authorize permissions
→ ContribHub processes existing open issues (background, <5 min)
→ Maintainer receives first triage summary email within 1 hour
→ Next new issue: auto-labeled within 30 seconds
```

#### Flow 2: Issue Gets Triaged (30 seconds, zero maintainer action)

```
Reporter creates issue → GitHub webhook fires
→ ContribHub AI analyzes title + body + repo context
→ Labels applied: [bug] [P2-medium] [complexity:beginner]
→ Duplicate check: no match found
→ Draft response created (visible only to maintainer via dashboard)
→ If issue quality <40: polite comment requesting missing info (auto-posted if maintainer enabled)
→ Issue added to contributor matching pool with complexity score
```

#### Flow 3: Contributor Finds and Completes Their First Contribution (< 72 hours)

```
Contributor signs up via GitHub OAuth → Skill profile auto-built (30 sec)
→ Contributor reviews/edits interests and experience level
→ Dashboard shows top 10 recommended issues
→ Each issue card shows: project name, health score ●●●●○, difficulty ██░░░,
   estimated time (2-4 hrs), prerequisite skills, maintainer response time (avg 6 hrs)
→ Contributor clicks "I'll take this" → guided onboarding brief generated
→ Brief shows: relevant files, key functions, related tests, setup steps
→ Contributor submits PR → maintainer reviews → PR merged
→ ContribHub logs successful match → skill profile updated → harder issues recommended next time
```

### Design Principles

1. **GitHub-native feel:** UI should feel like a natural extension of GitHub, not a separate product. Use GitHub's color palette and typography conventions.
2. **Zero-config start:** Everything works out of the box. Configuration is for power users.
3. **Transparency over magic:** Always show why the AI made a decision (confidence scores, reasoning). Maintainers must trust the system.
4. **Contributor dignity:** Never gamify contributions with competitive leaderboards. Growth is personal. No "top contributor" badges that create unhealthy pressure.
5. **Minimal surface area:** Maintainers interact primarily through GitHub (comments, labels). The web dashboard is supplementary, not required.

---

## 13. Go-to-Market Strategy

### Phase 1: "Single Player Mode" Launch (Months 1-3)

**Strategy:** Launch the maintainer triage tool as a free, standalone GitHub Action. No marketplace, no contributor matching. Pure value delivery to one side first.

**Tactics:**
- Open-source the GitHub Action core (builds trust with OSS community)
- Target 50 high-profile maintainers personally (warm outreach via Twitter/Mastodon, GitHub Sponsors networks)
- Publish "How We Reduced Triage Time by 70% on a 20K-Star Repo" case study
- Submit to Hacker News, Product Hunt, DevTools Weekly
- Reach: 5,000 repo installs (free)

**Why Single Player Mode:** NFX research shows this is 10x more capital-efficient than other marketplace launch strategies. By giving maintainers a standalone tool that works without contributors, we build supply-side lock-in before needing demand.

### Phase 2: "Light the Match" — Contributor Side (Months 4-6)

**Strategy:** Launch contributor matching using the data and repos already onboarded.

**Tactics:**
- Contributor beta waitlist (build anticipation)
- Partner with coding bootcamps (Lambda School/Bloom, 100Devs, Odin Project) — their students are our exact persona
- Content marketing: "How to Get Your First Open-Source PR Merged in 48 Hours" blog series
- GitHub Education partnership (student developer packs)
- Reach: 40,000 contributors, 20,000 repos

### Phase 3: "Enterprise Flywheel" (Months 7-12)

**Strategy:** Launch enterprise OSPO tier targeting corporate open-source programs.

**Tactics:**
- Present at Open Source Summit, KubeCon, FOSDEM
- Partner with Linux Foundation / TODO Group for distribution
- OSPO-specific features: multi-repo dashboards, compliance reporting, contribution attribution
- Direct sales to Fortune 500 OSPOs (median budget: $520K/year)
- Target: 10 enterprise contracts, $2M ARR

### Phase 4: "Category King" (Months 13-18)

**Strategy:** Establish ContribHub as the industry standard for open-source community orchestration.

**Tactics:**
- CNCF / Apache Foundation integrations (project-level dashboards)
- Google Summer of Code partnership (official matching tool)
- API ecosystem launch (third-party extensions)
- Series A fundraise on strong metrics
- Target: $8.5M ARR, 50,000 repos, 100,000 contributors

### Distribution Channels

| Channel | Cost | Expected Impact |
|---|---|---|
| GitHub Marketplace listing | Free (25% commission on sales) | Primary discovery channel |
| Open-source GitHub Action | Free (engineering time) | Trust building, organic adoption |
| Content marketing (blog, Twitter) | $2K/month | Developer awareness |
| Conference talks (OSS Summit, KubeCon) | $15K/event | Enterprise credibility |
| Coding bootcamp partnerships | Revenue share | Contributor acquisition |
| Hacker News / Product Hunt launch | Free | Spike traffic, early adopters |
| GitHub Education | Partnership | Student contributor pipeline |

---

## 14. Business Model & Pricing

### Pricing Philosophy

**Free for open-source. Paid for scale and enterprise.**

Following the CodeRabbit playbook: free for OSS builds the data flywheel and community goodwill. Paid tiers for teams and enterprises who need advanced features, SLAs, and compliance.

### Pricing Tiers

| Tier | Price | Target | Includes |
|---|---|---|---|
| **Community (Free)** | $0 | Individual maintainers, small OSS projects | AI triage (up to 100 issues/month), basic labels, duplicate detection, contributor matching (basic) |
| **Maintainer Pro** | $29/repo/month | Popular OSS projects, small teams | Unlimited issues, response drafting, quality scoring, triage analytics, priority support, custom label taxonomies |
| **Contributor Pro** | $9/month | Job-seeking developers | Advanced skill analytics, priority matching, guided onboarding briefs, portfolio page, growth tracking |
| **Team** | $149/month (up to 10 repos) | Organizations with multiple OSS projects | Everything in Maintainer Pro + team analytics, shared triage rules, Slack/Discord integration |
| **Enterprise** | Custom ($15K-$50K/year) | Fortune 500 OSPOs, foundations | Everything in Team + SSO/SAML, compliance reporting, SLA (99.95%), dedicated support, API access, custom integrations, on-prem option |

### Unit Economics (Steady State)

| Metric | Value |
|---|---|
| **LLM cost per issue triage** | $0.003 (classifier) + $0.02 (response draft) = $0.023 |
| **Average issues per repo/month** | ~30 (across all sizes) |
| **Cost per repo/month** | ~$0.69 (AI) + $0.50 (infra) = $1.19 |
| **Maintainer Pro ARPU** | $29/month |
| **Gross margin** | ~96% |
| **CAC (estimated)** | $50 (community), $5,000 (enterprise) |
| **LTV (Maintainer Pro, 24mo avg)** | $696 |
| **LTV:CAC ratio** | 14:1 (community) |

---

## 15. Risks, Assumptions & Dependencies

### Assumptions

| # | Assumption | If Wrong... |
|---|---|---|
| A1 | Maintainers will trust AI-generated labels enough to adopt | Product fails — must build confidence through transparency and human-in-the-loop |
| A2 | Contributors will use a new platform vs. just browsing GitHub directly | Need overwhelming value (3x better outcomes) to change behavior |
| A3 | "Good first issue" mislabeling is a significant enough pain point | Validate with user interviews before building complexity scoring |
| A4 | Enterprise OSPOs will pay $15-50K/year for contributor orchestration | Validate with 5 design-partner conversations before building enterprise features |
| A5 | GitHub won't build a competing first-party product that makes us obsolete | Mitigate by moving fast, owning the community layer GitHub won't build |

### Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **GitHub builds native competitor** | Medium | High | Move fast, own contributor community and cross-project matching (GitHub won't build a marketplace). Build switching costs via historical data and reputation. |
| **AI accuracy insufficient** | Low | High | Start with fine-tuned classifiers (proven 92%+). Human-in-the-loop for all responses. Accuracy improves with data volume. |
| **Open-source community backlash** ("AI replacing community interaction") | Medium | Medium | Always human-in-the-loop. Open-source the triage action. Transparent AI reasoning. Position as "giving maintainers time back" not "automating community away." |
| **GitHub API rate limits block scale** | Medium | Medium | Aggressive caching, webhook-first architecture, GraphQL batching. Request higher rate limits as GitHub partner. |
| **LLM costs spike at scale** | Low | Medium | Use fine-tuned BERT for classification (cheap). LLM only for response drafting. Costs decrease with model commoditization. |
| **Cold start problem** (contributor side) | High | Medium | Single-player mode first (maintainer tool works without contributors). Seed with bootcamp partnerships. |

### Dependencies

| Dependency | Risk Level | Contingency |
|---|---|---|
| GitHub API availability | Low | Circuit breaker pattern, queue failed webhooks for retry |
| OpenAI / Anthropic API | Low | Multi-provider abstraction (swap models without code changes) |
| Qdrant/vector DB | Low | Self-hosted, can migrate to Pinecone or pgvector |
| GitHub Marketplace approval | Medium | Direct installation via GitHub App (bypass Marketplace if needed) |

### Open Questions

1. Should we allow maintainers to auto-post AI responses, or always require approval? (Leaning toward approval-required for trust.)
2. How do we handle private repos? (Enterprise only, with strict data isolation.)
3. Should contributor profiles be public by default or opt-in? (Leaning opt-in for privacy.)
4. What's the right threshold for "dormant repo" filtering? (<1 commit/90 days? <1 commit/180 days?)
5. Should we integrate with existing bounty platforms from Day 1, or is that V2?

---

## 16. Timeline & Milestones

### Phase 1: MVP Build (Weeks 1-12)

| Week | Milestone | Deliverable |
|---|---|---|
| 1-2 | **Foundation** | GitHub App skeleton, webhook gateway, CI/CD pipeline, database schema |
| 3-4 | **AI Triage Core** | Issue classifier (fine-tuned), label applicator, GitHub API integration |
| 5-6 | **Duplicate Detection** | Embedding pipeline, vector similarity search, duplicate linking |
| 7-8 | **Response Drafting** | LLM integration, template system, maintainer approval flow |
| 9-10 | **Contributor Engine** | Skill profile builder, project health scorer, matching algorithm |
| 11 | **Web Dashboard** | Next.js app, GitHub OAuth, maintainer + contributor views |
| 12 | **Beta Launch** | GitHub Marketplace listing, 50 beta maintainers, public announcement |

### Key Decision Points

| Date | Decision | Criteria |
|---|---|---|
| Week 6 | Go/no-go on public beta | >88% label accuracy on 10 test repos |
| Week 12 | Go/no-go on contributor matching launch | >500 repos installed, >3x merge rate improvement |
| Month 6 | Go/no-go on enterprise | >5 qualified enterprise leads |
| Month 9 | Go/no-go on Series A fundraise | >$1M ARR trajectory, >30K repos |

### Fundraising Timeline

| Stage | Amount | Timing | Use of Funds |
|---|---|---|---|
| **Pre-seed / Bootstrap** | $0-150K (self-funded + angels) | Months 1-6 | MVP build, initial hiring (1 ML engineer) |
| **Seed** | $1.5-3M | Month 6-9 (post PMF signals) | Team (5-8 engineers), enterprise sales, SOC 2 |
| **Series A** | $8-15M | Month 15-18 (post $5M ARR) | Scale engineering, international expansion, GitLab support |

---

## 17. Appendix

### A. Key Research Sources

| Source | Key Data Point |
|---|---|
| GitHub Octoverse 2025 | 180M+ developers, 1.12B contributions, 518.7M PRs merged |
| Tidelift 2024 Survey (n=400+) | 60% maintainers unpaid, 60% quit/considered quitting, 60% want triage help |
| ACM GFI Study (n=9,368 GFIs) | Only 14% of "good first issues" solved by newcomers |
| CMU STRUDEL Lab | 59.7% of projects lose 30%+ contributors annually |
| CodeRabbit metrics | $15M ARR, 2M+ repos, $550M valuation — validates AI dev tools market |
| NFX Marketplace Tactics | Single-player mode is 10x more capital efficient |
| Linux Foundation 2024 | Median OSPO investment: $520K/year |
| Grand View Research | AI code tools market: $7.37B → $23.97B by 2030 |

### B. Glossary

| Term | Definition |
|---|---|
| **Triage** | The process of categorizing, prioritizing, and routing incoming issues |
| **GFI** | Good First Issue — a GitHub label intended to mark beginner-friendly issues |
| **OSPO** | Open Source Program Office — a corporate team managing OSS strategy |
| **CHAOSS** | Community Health Analytics in Open Source Software (Linux Foundation project) |
| **AST** | Abstract Syntax Tree — a structured representation of source code |
| **Embedding** | A numerical vector representation of text/code for similarity comparison |
| **DP-SGD** | Differentially Private Stochastic Gradient Descent |

### C. Configuration Example (`.contribhub.yml`)

```yaml
version: 1
triage:
  enabled: true
  labels:
    categories: [bug, feature, question, docs, chore]
    priorities: [P0-critical, P1-high, P2-medium, P3-low]
    complexity: [beginner, intermediate, advanced, expert]
  auto_label_confidence_threshold: 0.70
  duplicate_detection:
    enabled: true
    similarity_threshold: 0.80
  response_drafts:
    enabled: true
    tone: friendly  # formal | friendly | minimal
    auto_post_quality_requests: false
  excluded_labels: [wontfix, invalid]
  trusted_reporters: [user1, user2]  # skip quality checks for these users

matching:
  enabled: true
  exclude_dormant_days: 90
  exclude_claimed_issues: true
```

### D. Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-03-13 | Initial PRD — full scope definition |

---

*This PRD is a living document. It will evolve as we validate assumptions through user research, beta testing, and market feedback. All stakeholders are encouraged to comment directly.*
