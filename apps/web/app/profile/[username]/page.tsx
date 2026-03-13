import { Github, Calendar, GitPullRequest, CheckCircle, FolderGit2, Flame, TrendingUp, ExternalLink } from "lucide-react";
import { Avatar } from "../../components/ui/Avatar";
import { Card, CardHeader, CardBody } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { SkillChip } from "../../components/features/SkillChip";
import { SkillRadar } from "../../components/charts/SkillRadar";
import { DifficultyProgressChart } from "../../components/charts/DifficultyProgressChart";
import { mockSkillProfile } from "@/lib/mock-data";

interface PublicProfilePageProps {
  params: Promise<{ username: string }>;
}

export default async function PublicProfilePage({ params }: PublicProfilePageProps) {
  const { username } = await params;

  // In production, fetch from API. For now, use mock data.
  const profile = { ...mockSkillProfile, username };
  const allSkills = profile.skills.flatMap((cat) => cat.skills);

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      {/* Profile Header */}
      <Card>
        <div className="flex flex-col sm:flex-row items-start gap-5">
          <Avatar
            src={profile.avatarUrl}
            alt={profile.username}
            size="xl"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
                {profile.username}
              </h1>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[11px] font-medium text-emerald-400">
                Public
              </span>
            </div>
            <p className="text-sm text-zinc-400 mb-3">{profile.bio}</p>
            <div className="flex flex-wrap items-center gap-4 text-xs text-zinc-500">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" />
                Member since Jan 2024
              </div>
              <div className="flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5 text-orange-400" />
                <span>{profile.currentStreak} day streak</span>
              </div>
              <div className="flex items-center gap-1.5">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                <span>Longest: {profile.longestStreak} days</span>
              </div>
            </div>
          </div>
          <div className="shrink-0">
            <a
              href={`https://github.com/${profile.username}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button
                variant="secondary"
                size="sm"
                icon={<Github className="w-4 h-4" />}
              >
                View on GitHub
              </Button>
            </a>
          </div>
        </div>
      </Card>

      {/* Contribution Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-indigo-500/10">
              <GitPullRequest className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-100">
                {profile.totalContributions}
              </p>
              <p className="text-xs text-zinc-500">PRs Merged</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/10">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-100">
                {profile.contributions.length}
              </p>
              <p className="text-xs text-zinc-500">Issues Resolved</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-amber-500/10">
              <FolderGit2 className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-100">
                {new Set(profile.contributions.map((c) => c.repoName)).size}
              </p>
              <p className="text-xs text-zinc-500">Repos Contributed To</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Skills Section */}
      <Card>
        <CardHeader
          title="Skills"
          description="Skill proficiency organized by category"
        />
        <CardBody>
          <div className="space-y-5">
            {profile.skills.map((category) => (
              <div key={category.name}>
                <h4 className="text-sm font-semibold text-zinc-300 mb-2">
                  {category.name}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {category.skills.map((skill) => (
                    <SkillChip
                      key={skill.name}
                      name={skill.name}
                      proficiency={skill.proficiency}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Language Proficiency + Skill Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Language Proficiency */}
        <Card>
          <CardHeader
            title="Language Proficiency"
            description="Lines of code written and proficiency level"
          />
          <CardBody>
            <div className="space-y-4">
              {profile.languages.map((lang) => (
                <div key={lang.language}>
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: lang.color }}
                      />
                      <span className="text-sm font-medium text-zinc-200">
                        {lang.language}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-zinc-500">
                        {(lang.linesWritten / 1000).toFixed(0)}k lines
                      </span>
                      <span className="text-xs font-mono font-semibold text-zinc-300 w-10 text-right">
                        {lang.proficiency}%
                      </span>
                    </div>
                  </div>
                  <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${lang.proficiency}%`,
                        backgroundColor: lang.color,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Skill Radar */}
        <Card>
          <CardHeader
            title="Skill Radar"
            description="Visual overview of top skills"
          />
          <CardBody>
            <SkillRadar skills={allSkills.slice(0, 8)} />
          </CardBody>
        </Card>
      </div>

      {/* Interests */}
      <Card>
        <CardHeader
          title="Interests"
          description="Domains this contributor is interested in"
        />
        <CardBody>
          <div className="flex flex-wrap gap-2">
            {profile.domains.map((domain) => (
              <span
                key={domain}
                className="px-3 py-1.5 rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-sm font-medium text-indigo-400"
              >
                {domain}
              </span>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* Difficulty Progress Chart */}
      <Card>
        <CardHeader
          title="Difficulty Growth"
          description="How the complexity of contributions has evolved over time"
        />
        <CardBody>
          <DifficultyProgressChart contributions={profile.contributions} />
        </CardBody>
      </Card>

      {/* Recent Contributions */}
      <Card>
        <CardHeader
          title="Recent Contributions"
          description="Latest resolved issues across open source projects"
        />
        <CardBody>
          <div className="divide-y divide-zinc-800/50">
            {profile.contributions.map((contrib) => (
              <div
                key={contrib.id}
                className="flex items-center justify-between py-3 first:pt-0 last:pb-0"
              >
                <div className="min-w-0 flex-1">
                  <a
                    href={contrib.htmlUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-medium text-zinc-200 hover:text-indigo-400 transition-colors truncate block"
                  >
                    {contrib.issueTitle}
                  </a>
                  <p className="text-xs text-zinc-500 mt-0.5 font-mono">
                    {contrib.repoName}
                  </p>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-4">
                  <Badge
                    color={
                      contrib.difficulty === "expert"
                        ? "red"
                        : contrib.difficulty === "hard"
                          ? "orange"
                          : contrib.difficulty === "medium"
                            ? "yellow"
                            : contrib.difficulty === "easy"
                              ? "green"
                              : "emerald"
                    }
                  >
                    {contrib.difficulty}
                  </Badge>
                  <span className="text-xs text-zinc-500">
                    {new Date(contrib.completedAt).toLocaleDateString(
                      "en-US",
                      { month: "short", day: "numeric" }
                    )}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
