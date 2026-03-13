"use client";

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";
import type {
  TriageStats,
  Repo,
  Issue,
  IssueFilters,
  TriageEvent,
  Recommendation,
  RecommendationFilters,
  SkillProfile,
  FeedbackPayload,
  TriageConfig,
} from "./types";

// ─── Base API Client ────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api";

async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(error.message || `API Error: ${res.status}`);
  }

  return res.json();
}

// ─── Query Keys ─────────────────────────────────────────────────────────────

export const queryKeys = {
  triageStats: (repoId?: string) => ["triageStats", repoId] as const,
  repos: () => ["repos"] as const,
  repo: (id: string) => ["repo", id] as const,
  repoIssues: (repoId: string, filters?: IssueFilters) =>
    ["repoIssues", repoId, filters] as const,
  triageEvents: (repoId: string) => ["triageEvents", repoId] as const,
  triageEvent: (eventId: string) => ["triageEvent", eventId] as const,
  triageConfig: (repoId: string) => ["triageConfig", repoId] as const,
  recommendations: (filters?: RecommendationFilters) =>
    ["recommendations", filters] as const,
  skillProfile: () => ["skillProfile"] as const,
  publicProfile: (username: string) => ["publicProfile", username] as const,
};

// ─── Query Hooks ────────────────────────────────────────────────────────────

export function useTriageStats(repoId?: string) {
  return useQuery<TriageStats>({
    queryKey: queryKeys.triageStats(repoId),
    queryFn: () =>
      apiFetch<TriageStats>(
        `/triage/stats${repoId ? `?repoId=${repoId}` : ""}`
      ),
  });
}

export function useRepos() {
  return useQuery<Repo[]>({
    queryKey: queryKeys.repos(),
    queryFn: () => apiFetch<Repo[]>("/repos"),
  });
}

export function useRepo(id: string) {
  return useQuery<Repo>({
    queryKey: queryKeys.repo(id),
    queryFn: () => apiFetch<Repo>(`/repos/${id}`),
    enabled: !!id,
  });
}

export function useRepoIssues(repoId: string, filters?: IssueFilters) {
  const params = new URLSearchParams();
  if (filters?.category) params.set("category", filters.category);
  if (filters?.priority) params.set("priority", filters.priority);
  if (filters?.complexity) params.set("complexity", filters.complexity);
  if (filters?.state) params.set("state", filters.state);
  if (filters?.search) params.set("search", filters.search);
  const qs = params.toString();

  return useQuery<Issue[]>({
    queryKey: queryKeys.repoIssues(repoId, filters),
    queryFn: () =>
      apiFetch<Issue[]>(`/repos/${repoId}/issues${qs ? `?${qs}` : ""}`),
    enabled: !!repoId,
  });
}

export function useTriageEvents(repoId: string) {
  return useQuery<TriageEvent[]>({
    queryKey: queryKeys.triageEvents(repoId),
    queryFn: () => apiFetch<TriageEvent[]>(`/repos/${repoId}/triage-events`),
    enabled: !!repoId,
  });
}

export function useTriageEvent(eventId: string) {
  return useQuery<TriageEvent>({
    queryKey: queryKeys.triageEvent(eventId),
    queryFn: () => apiFetch<TriageEvent>(`/triage/events/${eventId}`),
    enabled: !!eventId,
  });
}

export function useTriageConfig(repoId: string) {
  return useQuery<TriageConfig>({
    queryKey: queryKeys.triageConfig(repoId),
    queryFn: () => apiFetch<TriageConfig>(`/repos/${repoId}/triage-config`),
    enabled: !!repoId,
  });
}

export function useRecommendations(filters?: RecommendationFilters) {
  const params = new URLSearchParams();
  if (filters?.language) params.set("language", filters.language);
  if (filters?.difficulty) params.set("difficulty", filters.difficulty);
  if (filters?.domain) params.set("domain", filters.domain);
  const qs = params.toString();

  return useQuery<Recommendation[]>({
    queryKey: queryKeys.recommendations(filters),
    queryFn: () =>
      apiFetch<Recommendation[]>(
        `/recommendations${qs ? `?${qs}` : ""}`
      ),
  });
}

export function useSkillProfile() {
  return useQuery<SkillProfile>({
    queryKey: queryKeys.skillProfile(),
    queryFn: () => apiFetch<SkillProfile>("/profile"),
  });
}

export function usePublicProfile(username: string) {
  return useQuery<SkillProfile>({
    queryKey: queryKeys.publicProfile(username),
    queryFn: () => apiFetch<SkillProfile>(`/profile/${username}`),
    enabled: !!username,
  });
}

// ─── Mutation Hooks ─────────────────────────────────────────────────────────

export function useApproveResponse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (eventId: string) =>
      apiFetch(`/triage/events/${eventId}/approve`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["triageEvents"] });
      queryClient.invalidateQueries({ queryKey: ["triageStats"] });
    },
  });
}

export function useDiscardResponse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (eventId: string) =>
      apiFetch(`/triage/events/${eventId}/discard`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["triageEvents"] });
    },
  });
}

export function useEditAndApproveResponse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      eventId,
      editedResponse,
    }: {
      eventId: string;
      editedResponse: string;
    }) =>
      apiFetch(`/triage/events/${eventId}/approve`, {
        method: "POST",
        body: JSON.stringify({ editedResponse }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["triageEvents"] });
      queryClient.invalidateQueries({ queryKey: ["triageStats"] });
    },
  });
}

export function useSubmitFeedback() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: FeedbackPayload) =>
      apiFetch("/recommendations/feedback", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });
}

export function useAcceptRecommendation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recommendationId: string) =>
      apiFetch(`/recommendations/${recommendationId}/accept`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (updates: Partial<SkillProfile>) =>
      apiFetch("/profile", {
        method: "PATCH",
        body: JSON.stringify(updates),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["skillProfile"] });
    },
  });
}

export function useUpdateTriageConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      repoId,
      config,
    }: {
      repoId: string;
      config: Partial<TriageConfig>;
    }) =>
      apiFetch(`/repos/${repoId}/triage-config`, {
        method: "PATCH",
        body: JSON.stringify(config),
      }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.triageConfig(variables.repoId),
      });
    },
  });
}
