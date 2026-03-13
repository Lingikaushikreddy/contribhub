"use client";

import { useState } from "react";
import { Compass, Filter } from "lucide-react";
import { Select } from "../components/ui/Select";
import { IssueRecommendationCard } from "../components/features/IssueRecommendationCard";
import { mockRecommendations, mockIssues } from "@/lib/mock-data";
import type { Recommendation, IssueComplexity } from "@/lib/types";

// Extend with more sample recommendations for a fuller page
const extendedRecommendations: Recommendation[] = [
  ...mockRecommendations,
  {
    id: "rec-6",
    issue: {
      ...mockIssues[2],
      id: "issue-200",
      number: 1300,
      title: "Improve accessibility for screen readers",
      category: "feature",
      complexity: "medium",
      priority: "P2",
      repoName: "acme/frontend",
      labels: ["accessibility", "ui/ux"],
    },
    matchScore: 91,
    healthLevel: 5,
    difficulty: 3,
    estimatedMinutes: 150,
    prerequisites: ["React", "ARIA", "WAI-WCAG"],
    maintainerResponseTime: "< 3 hours",
    repoAvatarUrl: "https://avatars.githubusercontent.com/u/2?v=4",
  },
  {
    id: "rec-7",
    issue: {
      ...mockIssues[0],
      id: "issue-201",
      number: 1301,
      title: "Add rate limiting to public API endpoints",
      category: "security",
      complexity: "hard",
      priority: "P1",
      repoName: "acme/backend-api",
      labels: ["security", "api"],
    },
    matchScore: 76,
    healthLevel: 4,
    difficulty: 4,
    estimatedMinutes: 300,
    prerequisites: ["Rate Limiting", "Redis", "API Design"],
    maintainerResponseTime: "< 6 hours",
    repoAvatarUrl: "https://avatars.githubusercontent.com/u/1?v=4",
  },
  {
    id: "rec-8",
    issue: {
      ...mockIssues[4],
      id: "issue-202",
      number: 1302,
      title: "Write integration tests for OAuth flow",
      category: "chore",
      complexity: "easy",
      priority: "P3",
      repoName: "acme/sdk",
      labels: ["testing", "oauth"],
    },
    matchScore: 85,
    healthLevel: 5,
    difficulty: 2,
    estimatedMinutes: 90,
    prerequisites: ["Jest", "OAuth2", "TypeScript"],
    maintainerResponseTime: "< 1 hour",
    repoAvatarUrl: "https://avatars.githubusercontent.com/u/4?v=4",
  },
  {
    id: "rec-9",
    issue: {
      ...mockIssues[3],
      id: "issue-203",
      number: 1303,
      title: "Optimize Docker image size for CI pipeline",
      category: "chore",
      complexity: "medium",
      priority: "P2",
      repoName: "acme/infra",
      labels: ["docker", "ci/cd"],
    },
    matchScore: 70,
    healthLevel: 4,
    difficulty: 3,
    estimatedMinutes: 120,
    prerequisites: ["Docker", "CI/CD", "Multi-stage Builds"],
    maintainerResponseTime: "< 4 hours",
    repoAvatarUrl: "https://avatars.githubusercontent.com/u/6?v=4",
  },
  {
    id: "rec-10",
    issue: {
      ...mockIssues[1],
      id: "issue-204",
      number: 1304,
      title: "Migrate Storybook to v8 with Vite builder",
      category: "chore",
      complexity: "medium",
      priority: "P3",
      repoName: "acme/frontend",
      labels: ["storybook", "migration"],
    },
    matchScore: 79,
    healthLevel: 5,
    difficulty: 3,
    estimatedMinutes: 180,
    prerequisites: ["Storybook", "Vite", "React"],
    maintainerResponseTime: "< 3 hours",
    repoAvatarUrl: "https://avatars.githubusercontent.com/u/2?v=4",
  },
];

const DOMAIN_OPTIONS = [
  "Web Development",
  "ML/AI",
  "DevOps",
  "Security",
  "Mobile",
  "Data",
  "Developer Tools",
  "Databases",
];

export default function RecommendationsPage() {
  const [language, setLanguage] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [selectedDomains, setSelectedDomains] = useState<Set<string>>(
    new Set()
  );
  const [visibleCount, setVisibleCount] = useState(6);

  const toggleDomain = (domain: string) => {
    setSelectedDomains((prev) => {
      const next = new Set(prev);
      if (next.has(domain)) {
        next.delete(domain);
      } else {
        next.add(domain);
      }
      return next;
    });
  };

  const filtered = extendedRecommendations.filter((rec) => {
    if (language && rec.issue.repoName) {
      // Filter by language of the repo
      const langMap: Record<string, string[]> = {
        TypeScript: ["acme/backend-api", "acme/frontend", "acme/sdk"],
        Python: ["acme/ml-pipeline"],
        HCL: ["acme/infra"],
        MDX: ["acme/docs"],
      };
      const repos = langMap[language] || [];
      if (repos.length > 0 && !repos.includes(rec.issue.repoName)) {
        return false;
      }
    }
    if (difficulty) {
      const diffMap: Record<string, number[]> = {
        trivial: [1],
        easy: [1, 2],
        medium: [2, 3],
        hard: [3, 4],
        expert: [4, 5],
      };
      const levels = diffMap[difficulty] || [];
      if (levels.length > 0 && !levels.includes(rec.difficulty)) {
        return false;
      }
    }
    return true;
  });

  const visible = filtered.slice(0, visibleCount);
  const hasMore = visibleCount < filtered.length;

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
          Recommendations
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          Issues matched to your skills and interests. The higher the match
          score, the better fit for you.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-4 items-start">
        <div className="w-full sm:w-48">
          <Select
            label="Language"
            placeholder="All Languages"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            options={[
              { value: "TypeScript", label: "TypeScript" },
              { value: "Python", label: "Python" },
              { value: "Go", label: "Go" },
              { value: "Rust", label: "Rust" },
              { value: "HCL", label: "HCL" },
              { value: "MDX", label: "MDX" },
            ]}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select
            label="Difficulty"
            placeholder="All Difficulties"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            options={[
              { value: "trivial", label: "Trivial" },
              { value: "easy", label: "Easy" },
              { value: "medium", label: "Medium" },
              { value: "hard", label: "Hard" },
              { value: "expert", label: "Expert" },
            ]}
          />
        </div>
        <div className="w-full sm:flex-1">
          <label className="block text-sm font-medium text-zinc-300 mb-1.5">
            Domains
          </label>
          <div className="flex flex-wrap gap-2">
            {DOMAIN_OPTIONS.map((domain) => (
              <button
                key={domain}
                onClick={() => toggleDomain(domain)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                  selectedDomains.has(domain)
                    ? "border-indigo-500 bg-indigo-500/15 text-indigo-400"
                    : "border-zinc-700 bg-zinc-800 text-zinc-400 hover:border-zinc-600"
                }`}
              >
                {domain}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      {visible.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {visible.map((rec) => (
              <IssueRecommendationCard key={rec.id} recommendation={rec} />
            ))}
          </div>

          {/* Load More */}
          {hasMore && (
            <div className="flex justify-center pt-4">
              <button
                onClick={() => setVisibleCount((c) => c + 6)}
                className="px-6 py-2.5 rounded-lg border border-zinc-700 bg-zinc-800 text-sm font-medium text-zinc-300 hover:bg-zinc-700 hover:text-zinc-100 transition-colors"
              >
                Load More
              </button>
            </div>
          )}
        </>
      ) : (
        /* Empty State */
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-14 h-14 rounded-full bg-zinc-800 flex items-center justify-center mb-4">
            <Compass className="w-6 h-6 text-zinc-500" />
          </div>
          <p className="text-base font-medium text-zinc-300">
            No recommendations yet
          </p>
          <p className="text-sm text-zinc-500 mt-1 max-w-sm">
            Complete your skill profile to get matched with issues that fit
            your expertise and interests!
          </p>
        </div>
      )}
    </div>
  );
}
