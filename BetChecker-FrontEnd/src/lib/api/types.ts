/**
 * TypeScript types for the BetChecker API
 */

/**
 * Statistic types supported by the API
 */
export type StatType = 'disposals' | 'goals';

/**
 * Request parameters for the over/under endpoint
 */
export interface OverUnderParams {
  /** Player's full name (e.g., "Scott Pendlebury") */
  player_name?: string;
  /** Player ID number */
  player_id?: number;
  /** Statistic type: "disposals" or "goals" */
  stat: StatType;
  /** The threshold value (e.g., 23.5) */
  threshold: number;
  /** If true: over uses `>`, under uses `<=`. If false: over uses `>=`, under uses `<` */
  strict_over?: boolean;
}

/**
 * Response from the over/under endpoint
 */
export interface OverUnderResponse {
  /** Number of games where the stat was over the threshold */
  over: number;
  /** Number of games where the stat was under the threshold */
  under: number;
}

/**
 * API error response
 */
export interface ApiError {
  detail: string;
}

