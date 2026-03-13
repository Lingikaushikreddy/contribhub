"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "../../components/ui/Input";
import { RepoCard } from "../../components/features/RepoCard";
import { mockRepos } from "@/lib/mock-data";

export default function ReposPage() {
  const [search, setSearch] = useState("");

  const filteredRepos = mockRepos.filter(
    (repo) =>
      repo.name.toLowerCase().includes(search.toLowerCase()) ||
      repo.fullName.toLowerCase().includes(search.toLowerCase()) ||
      repo.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
          Repositories
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          Manage your connected repositories and view their health scores.
        </p>
      </div>

      {/* Search */}
      <div className="max-w-md">
        <Input
          placeholder="Search repositories..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          icon={<Search className="w-4 h-4" />}
        />
      </div>

      {/* Repo Grid */}
      {filteredRepos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredRepos.map((repo) => (
            <RepoCard key={repo.id} repo={repo} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-12 h-12 rounded-full bg-zinc-800 flex items-center justify-center mb-4">
            <Search className="w-5 h-5 text-zinc-500" />
          </div>
          <p className="text-sm font-medium text-zinc-300">
            No repositories found
          </p>
          <p className="text-xs text-zinc-500 mt-1">
            Try adjusting your search query.
          </p>
        </div>
      )}
    </div>
  );
}
