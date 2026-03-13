import { mockTriageStats } from "@/lib/mock-data";
import { StatCard } from "../components/ui/Card";
import { Card, CardHeader, CardBody } from "../components/ui/Card";
import { CategoryBadge, PriorityBadge } from "../components/ui/Badge";
import { IssueVolumeChart } from "../components/charts/IssueVolumeChart";
import { CategoryBreakdown } from "../components/charts/CategoryBreakdown";
import { PriorityDistribution } from "../components/charts/PriorityDistribution";
import {
  BarChart3,
  Target,
  Clock,
  Users,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";
import clsx from "clsx";

async function getTriageStats() {
  // In production, this would fetch from the API
  return mockTriageStats;
}

export default async function DashboardPage() {
  const stats = await getTriageStats();

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          Overview of your triage pipeline and contributor activity.
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Issues Triaged"
          value={stats.totalTriaged}
          change="+12.3% from last month"
          changeType="positive"
          icon={<BarChart3 className="w-5 h-5" />}
        />
        <StatCard
          label="AI Accuracy"
          value={`${stats.aiAccuracy}%`}
          change="+1.8% from last month"
          changeType="positive"
          icon={<Target className="w-5 h-5" />}
        />
        <StatCard
          label="Avg Response Time"
          value={`${stats.avgResponseTime}m`}
          change="-0.5m from last month"
          changeType="positive"
          icon={<Clock className="w-5 h-5" />}
        />
        <StatCard
          label="Active Contributors"
          value={stats.activeContributors}
          change="+342 this week"
          changeType="positive"
          icon={<Users className="w-5 h-5" />}
        />
      </div>

      {/* Issue Volume Chart */}
      <Card>
        <CardHeader
          title="Issue Volume"
          description="Issues triaged per day over the last 30 days"
        />
        <CardBody>
          <IssueVolumeChart data={stats.issueVolume} />
        </CardBody>
      </Card>

      {/* Category & Priority side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Category Breakdown" description="Distribution of issue categories" />
          <CardBody>
            <CategoryBreakdown data={stats.categoryBreakdown} />
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Priority Distribution" description="Issues by priority level" />
          <CardBody>
            <PriorityDistribution data={stats.priorityDistribution} />
          </CardBody>
        </Card>
      </div>

      {/* Recent Triage Events Table */}
      <Card>
        <CardHeader
          title="Recent Triage Events"
          description="Latest 10 triage actions performed by the AI"
          action={
            <Link
              href="/dashboard/repos"
              className="text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              View all repos
            </Link>
          }
        />
        <CardBody>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-zinc-800">
                  <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                    Issue
                  </th>
                  <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="pb-3 text-xs font-medium text-zinc-500 uppercase tracking-wider text-right">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/50">
                {stats.recentEvents.map((event) => (
                  <tr
                    key={event.id}
                    className="hover:bg-zinc-800/30 transition-colors group"
                  >
                    <td className="py-3 pr-4">
                      <Link
                        href={`/dashboard/triage/${event.id}`}
                        className="block"
                      >
                        <p className="text-sm font-medium text-zinc-200 group-hover:text-indigo-400 transition-colors truncate max-w-[320px]">
                          {event.issueTitle}
                        </p>
                        <p className="text-xs text-zinc-500 mt-0.5 font-mono">
                          {event.repoName} #{event.issueNumber}
                        </p>
                      </Link>
                    </td>
                    <td className="py-3 pr-4">
                      <CategoryBadge category={event.category} />
                    </td>
                    <td className="py-3 pr-4">
                      <PriorityBadge priority={event.priority} />
                    </td>
                    <td className="py-3 pr-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                          <div
                            className={clsx(
                              "h-full rounded-full",
                              event.confidence >= 90
                                ? "bg-emerald-500"
                                : event.confidence >= 75
                                  ? "bg-yellow-500"
                                  : "bg-orange-500"
                            )}
                            style={{ width: `${event.confidence}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono text-zinc-400">
                          {event.confidence.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      <span className="text-xs text-zinc-500">
                        {formatDistanceToNow(new Date(event.createdAt), {
                          addSuffix: true,
                        })}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
