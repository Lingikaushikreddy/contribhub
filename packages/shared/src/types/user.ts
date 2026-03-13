/**
 * User domain types for ContribHub.
 * Mirrors the API schema at apps/api/app/schemas/user.py
 */

export enum UserRole {
  ADMIN = 'admin',
  MAINTAINER = 'maintainer',
  CONTRIBUTOR = 'contributor',
}

export interface User {
  id: string;
  github_id: number;
  username: string;
  email: string | null;
  avatar_url: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  bio: string | null;
  location: string | null;
  website: string | null;
  twitter: string | null;
  languages: string[];
  skills: string[];
  availability_hours_per_week: number | null;
  experience_level: ExperienceLevel;
  total_contributions: number;
  repos_contributed_to: number;
  match_opt_in: boolean;
  created_at: string;
  updated_at: string;
}

export enum ExperienceLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
}

export interface UserCreate {
  github_id: number;
  username: string;
  email: string | null;
  avatar_url: string;
}

export interface UserUpdate {
  email?: string | null;
  avatar_url?: string;
  role?: UserRole;
}

export interface UserProfileUpdate {
  bio?: string | null;
  location?: string | null;
  website?: string | null;
  twitter?: string | null;
  languages?: string[];
  skills?: string[];
  availability_hours_per_week?: number | null;
  experience_level?: ExperienceLevel;
  match_opt_in?: boolean;
}
