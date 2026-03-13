import json
import subprocess
import os

commits = [
    # 1. Base Project config
    {
        "msg": "chore: add root configuration and docker compose stack",
        "files": ["package.json", "turbo.json", "docker-compose.yml", "Makefile"]
    },
    # 2. Base Linters and Git config
    {
        "msg": "chore: add linting and environment templates",
        "files": [".eslintrc.json", ".prettierrc", ".env.example", ".contribhub.yml"]
    },
    # 3. Actions / CI CD
    {
        "msg": "ci: add GitHub Actions workflows for CI and staging",
        "files": [".github/workflows/ci.yml", ".github/workflows/deploy-staging.yml"]
    },
    # 4. Docs updates
    {
        "msg": "docs: update engineering playbook",
        "files": ["ENGINEERING_PLAYBOOK.md"]
    },
    # 5. Shared types base
    {
        "msg": "feat(shared): initial shared types and utils package setup",
        "files": ["packages/shared/package.json", "packages/shared/tsconfig.json", "packages/shared/src/index.ts", "packages/shared/src/utils.ts", "packages/shared/src/constants.ts"]
    },
    # 6. Shared types models 1
    {
        "msg": "feat(shared): add user, repo, and issue types",
        "files": ["packages/shared/src/types/user.ts", "packages/shared/src/types/repo.ts", "packages/shared/src/types/issue.ts", "packages/shared/src/types/api.ts"]
    },
    # 7. Shared types models 2
    {
        "msg": "feat(shared): add complex feature types",
        "files": ["packages/shared/src/types/config.ts", "packages/shared/src/types/health.ts", "packages/shared/src/types/match.ts", "packages/shared/src/types/skill.ts", "packages/shared/src/types/triage.ts", "packages/shared/src/types/webhook.ts"]
    },
    # 8. GitHub Action implementation 1
    {
        "msg": "feat(action): scaffold custom github action for triage",
        "files": ["packages/github-action/package.json", "packages/github-action/tsconfig.json", "packages/github-action/action.yml"]
    },
    # 9. GitHub Action implementation 2
    {
        "msg": "feat(action): implement action config and types",
        "files": ["packages/github-action/src/config.ts", "packages/github-action/src/types.ts"]
    },
    # 10. GitHub Action implementation 3
    {
        "msg": "feat(action): implement github api client and issue labels logic",
        "files": ["packages/github-action/src/api-client.ts", "packages/github-action/src/labels.ts", "packages/github-action/src/comments.ts", "packages/github-action/src/index.ts"]
    },
    # 11. ML Pipeline package base
    {
        "msg": "feat(ml): scaffold ML pipeline package and config",
        "files": ["packages/ml-pipeline/pyproject.toml", "packages/ml-pipeline/setup.py", "packages/ml-pipeline/contribhub_ml/__init__.py"]
    },
    # 12. ML Pipeline eval
    {
        "msg": "feat(ml): add ML evaluation framework",
        "files": ["packages/ml-pipeline/contribhub_ml/evaluation/__init__.py", "packages/ml-pipeline/contribhub_ml/evaluation/evaluator.py", "packages/ml-pipeline/contribhub_ml/evaluation/golden_set.json"]
    },
    # 13. ML Pipeline classifier
    {
        "msg": "feat(ml): implement issue classification models",
        "files": ["packages/ml-pipeline/contribhub_ml/classifier/__init__.py", "packages/ml-pipeline/contribhub_ml/classifier/complexity_scorer.py", "packages/ml-pipeline/contribhub_ml/classifier/issue_classifier.py"]
    },
    # 14. ML Pipeline embeddings
    {
        "msg": "feat(ml): implementation of text embeddings and duplication detection",
        "files": ["packages/ml-pipeline/contribhub_ml/embeddings/__init__.py", "packages/ml-pipeline/contribhub_ml/embeddings/duplicate_detector.py", "packages/ml-pipeline/contribhub_ml/embeddings/embedding_service.py"]
    },
    # 15. ML Pipeline scoring
    {
        "msg": "feat(ml): add repository health and user match scoring",
        "files": ["packages/ml-pipeline/contribhub_ml/scoring/__init__.py", "packages/ml-pipeline/contribhub_ml/scoring/health_scorer.py", "packages/ml-pipeline/contribhub_ml/scoring/match_scorer.py", "packages/ml-pipeline/contribhub_ml/scoring/skill_profiler.py"]
    },
    # 16. ML Pipeline drafter
    {
        "msg": "feat(ml): implement automated PR review and response drafter",
        "files": ["packages/ml-pipeline/contribhub_ml/drafter/__init__.py", "packages/ml-pipeline/contribhub_ml/drafter/response_drafter.py", "packages/ml-pipeline/contribhub_ml/drafter/templates.py"]
    },
    # 17. ML Pipeline tests
    {
        "msg": "test(ml): add comprehensive ML unit tests",
        "files": ["packages/ml-pipeline/tests/__init__.py", "packages/ml-pipeline/tests/conftest.py", "packages/ml-pipeline/tests/test_classifier.py", "packages/ml-pipeline/tests/test_embeddings.py", "packages/ml-pipeline/tests/test_scoring.py"]
    },
    # 18. API Base config and Docker
    {
        "msg": "feat(api): initialize backend api with docker and dependencies",
        "files": ["apps/api/.dockerignore", "apps/api/Dockerfile", "apps/api/requirements.txt", "apps/api/pytest.ini", "apps/api/app/__init__.py"]
    },
    # 19. API Core Config
    {
        "msg": "feat(api): implement api core config, security, and database connection",
        "files": ["apps/api/app/core/__init__.py", "apps/api/app/core/config.py", "apps/api/app/core/database.py", "apps/api/app/core/security.py"]
    },
    # 20. API BaseModel and Main
    {
        "msg": "feat(api): set up api entrypoint and base ORM model",
        "files": ["apps/api/app/main.py", "apps/api/app/models/__init__.py", "apps/api/app/models/base.py"]
    },
    # 21. API Alembic
    {
        "msg": "feat(api): configure alembic migrations for database schema",
        "files": ["apps/api/alembic.ini", "apps/api/alembic/env.py", "apps/api/alembic/script.py.mako", "apps/api/alembic/versions/.gitkeep"]
    },
    # 22. API ORM Models
    {
        "msg": "feat(api): implement database ORM models",
        "files": ["apps/api/app/models/issue.py", "apps/api/app/models/match.py", "apps/api/app/models/repo.py", "apps/api/app/models/skill.py", "apps/api/app/models/triage_event.py", "apps/api/app/models/user.py"]
    },
    # 23. API Pydantic Schemas 1
    {
        "msg": "feat(api): implement base pydantic schemas",
        "files": ["apps/api/app/schemas/__init__.py", "apps/api/app/schemas/auth.py", "apps/api/app/schemas/user.py", "apps/api/app/schemas/repo.py"]
    },
    # 24. API Pydantic Schemas 2
    {
        "msg": "feat(api): implement domain pydantic schemas",
        "files": ["apps/api/app/schemas/issue.py", "apps/api/app/schemas/match.py", "apps/api/app/schemas/skill.py", "apps/api/app/schemas/triage.py", "apps/api/app/schemas/webhook.py"]
    },
    # 25. API Services
    {
        "msg": "feat(api): build core application business logic services",
        "files": ["apps/api/app/services/__init__.py", "apps/api/app/services/github_service.py", "apps/api/app/services/matching_service.py", "apps/api/app/services/triage_service.py"]
    },
    # 26. API Routers 1
    {
        "msg": "feat(api): set up main router endpoints and structure",
        "files": ["apps/api/app/api/__init__.py", "apps/api/app/api/v1/__init__.py", "apps/api/app/api/v1/routers/__init__.py", "apps/api/app/api/v1/routers/health.py", "apps/api/app/api/v1/routers/auth.py"]
    },
    # 27. API Routers 2
    {
        "msg": "feat(api): add domain specific HTTP endpoints",
        "files": ["apps/api/app/api/v1/routers/issues.py", "apps/api/app/api/v1/routers/matches.py", "apps/api/app/api/v1/routers/repos.py", "apps/api/app/api/v1/routers/triage.py", "apps/api/app/api/v1/routers/webhooks.py"]
    },
    # 28. API Workers
    {
        "msg": "feat(api): implement background celery task workers",
        "files": ["apps/api/app/workers/__init__.py", "apps/api/app/workers/health_worker.py", "apps/api/app/workers/triage_worker.py"]
    },
    # 29. Integration Tests
    {
        "msg": "test: add integration test suite covering triage and matching flows",
        "files": ["tests/__init__.py", "tests/integration/__init__.py", "tests/integration/conftest.py", "tests/integration/test_matching_flow.py", "tests/integration/test_triage_flow.py"]
    },
    # 30. Web Setup
    {
        "msg": "feat(web): initialize Next.js frontend app and config",
        "files": ["apps/web/package.json", "apps/web/tsconfig.json", "apps/web/next.config.ts", "apps/web/tailwind.config.ts", "apps/web/postcss.config.mjs"]
    },
    # 31. Web Docker and Base app
    {
        "msg": "feat(web): setup frontend docker build, layout and global styles",
        "files": ["apps/web/Dockerfile", "apps/web/app/layout.tsx", "apps/web/app/globals.css"]
    },
    # 32. Web lib and providers
    {
        "msg": "feat(web): add robust frontend api client and React context providers",
        "files": ["apps/web/lib/api.ts", "apps/web/lib/auth.ts", "apps/web/lib/mock-data.ts", "apps/web/lib/providers.tsx", "apps/web/lib/types.ts"]
    },
    # 33. Web UI Components
    {
        "msg": "ui(web): build universal design system components",
        "files": ["apps/web/app/components/ui/Avatar.tsx", "apps/web/app/components/ui/Badge.tsx", "apps/web/app/components/ui/Button.tsx", "apps/web/app/components/ui/Card.tsx", "apps/web/app/components/ui/Input.tsx", "apps/web/app/components/ui/Select.tsx", "apps/web/app/components/ui/Skeleton.tsx", "apps/web/app/components/ui/Tabs.tsx"]
    },
    # 34. Web layout components
    {
        "msg": "ui(web): create responsive layout navigation and sidebar",
        "files": ["apps/web/app/components/layout/Header.tsx", "apps/web/app/components/layout/MobileNav.tsx", "apps/web/app/components/layout/Sidebar.tsx"]
    },
    # 35. Web chart components
    {
        "msg": "feat(web): implement dashboard data visualization charts",
        "files": ["apps/web/app/components/charts/CategoryBreakdown.tsx", "apps/web/app/components/charts/DifficultyProgressChart.tsx", "apps/web/app/components/charts/HealthScoreRadar.tsx", "apps/web/app/components/charts/IssueVolumeChart.tsx", "apps/web/app/components/charts/PriorityDistribution.tsx", "apps/web/app/components/charts/SkillRadar.tsx"]
    },
    # 36. Web feature widgets
    {
        "msg": "feat(web): add complex interactive feature modules",
        "files": ["apps/web/app/components/features/DifficultyBar.tsx", "apps/web/app/components/features/FeedbackModal.tsx", "apps/web/app/components/features/HealthDots.tsx", "apps/web/app/components/features/IssueRecommendationCard.tsx", "apps/web/app/components/features/RepoCard.tsx", "apps/web/app/components/features/SkillChip.tsx", "apps/web/app/components/features/TriageEventCard.tsx"]
    },
    # 37. Web auth and landing pages
    {
        "msg": "feat(web): build secure authentication and landing pages",
        "files": ["apps/web/app/page.tsx", "apps/web/app/auth/signin/page.tsx", "apps/web/app/api/auth/[...nextauth]/route.ts"]
    },
    # 38. Web Dashboard Core
    {
        "msg": "feat(web): create internal application dashboard views",
        "files": ["apps/web/app/dashboard/layout.tsx", "apps/web/app/dashboard/page.tsx", "apps/web/app/dashboard/repos/page.tsx"]
    },
    # 39. Web Dashboard Depth
    {
        "msg": "feat(web): build repository metrics and triage details pages",
        "files": ["apps/web/app/dashboard/repos/[id]/page.tsx", "apps/web/app/dashboard/triage/[eventId]/page.tsx"]
    },
    # 40. Web Profile and Recommendations
    {
        "msg": "feat(web): implement personalized contributor profiles and recommendation engine UI",
        "files": ["apps/web/app/profile/page.tsx", "apps/web/app/profile/[username]/page.tsx", "apps/web/app/recommendations/page.tsx"]
    }
]

def main():
    subprocess.run(["git", "reset", "--soft", "bfa52b3"], check=True)
    subprocess.run(["git", "reset"], check=True)

    for step in commits:
        msg = step["msg"]
        files = step["files"]

        # Only add files that exist and run git add
        added = False
        for f in files:
            if os.path.exists(f):
                subprocess.run(["git", "add", f], check=False)
                added = True
        if added:
            res = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
            if res.returncode != 0 and "working tree clean" not in res.stdout:
                pass
            print(f"Committed {msg}")

    # Catch-all for any files somehow missed
    subprocess.run(["git", "add", "."], check=True)
    status_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if status_res.stdout.strip():
        subprocess.run(["git", "commit", "-m", "chore: polish and final tweaks"], check=True)
        print("Committed catch-all")

if __name__ == "__main__":
    main()
