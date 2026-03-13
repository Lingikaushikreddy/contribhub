/**
 * API response wrapper types for ContribHub.
 * Used across all API endpoints for consistent response shapes.
 */

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string | null;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: PaginationMeta;
  message: string | null;
  timestamp: string;
}

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ApiError {
  success: false;
  error: {
    code: ApiErrorCode;
    message: string;
    details: Record<string, unknown> | null;
    request_id: string;
  };
  timestamp: string;
}

export enum ApiErrorCode {
  BAD_REQUEST = 'BAD_REQUEST',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  RATE_LIMITED = 'RATE_LIMITED',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  GITHUB_API_ERROR = 'GITHUB_API_ERROR',
  AI_SERVICE_ERROR = 'AI_SERVICE_ERROR',
}

export interface PaginationParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SearchParams extends PaginationParams {
  q?: string;
  filters?: Record<string, string | string[]>;
}

export interface BatchResponse<T> {
  success: boolean;
  results: BatchResult<T>[];
  total: number;
  succeeded: number;
  failed: number;
  timestamp: string;
}

export interface BatchResult<T> {
  index: number;
  success: boolean;
  data: T | null;
  error: string | null;
}
