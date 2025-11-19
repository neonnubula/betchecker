/**
 * API Client for BetChecker Backend
 * 
 * Provides functions to interact with the FastAPI backend.
 */

import { API_BASE_URL } from './config';
import type { OverUnderParams, OverUnderResponse, ApiError } from './types';

/**
 * Custom error class for API errors
 */
export class ApiClientError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: ApiError
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

/**
 * Fetches over/under game counts for a player's statistic across their full career history.
 * 
 * @param params - Request parameters
 * @returns Promise resolving to over/under counts
 * @throws {ApiClientError} If the request fails
 * 
 * @example
 * ```typescript
 * const stats = await getPlayerOverUnder({
 *   player_name: 'Scott Pendlebury',
 *   stat: 'disposals',
 *   threshold: 23.5
 * });
 * console.log(`Over: ${stats.over}, Under: ${stats.under}`);
 * ```
 */
export async function getPlayerOverUnder(
  params: OverUnderParams
): Promise<OverUnderResponse> {
  // Validate that exactly one of player_name or player_id is provided
  const hasPlayerName = params.player_name !== undefined && params.player_name !== '';
  const hasPlayerId = params.player_id !== undefined;
  
  if (!hasPlayerName && !hasPlayerId) {
    throw new ApiClientError('Provide exactly one of player_id or player_name');
  }
  
  if (hasPlayerName && hasPlayerId) {
    throw new ApiClientError('Provide exactly one of player_id or player_name');
  }
  
  // Build query parameters
  const queryParams = new URLSearchParams();
  
  if (params.player_name) {
    queryParams.append('player_name', params.player_name);
  }
  
  if (params.player_id !== undefined) {
    queryParams.append('player_id', params.player_id.toString());
  }
  
  queryParams.append('stat', params.stat);
  queryParams.append('threshold', params.threshold.toString());
  
  if (params.strict_over !== undefined) {
    queryParams.append('strict_over', params.strict_over.toString());
  }
  
  const url = `${API_BASE_URL}/search/over-under?${queryParams.toString()}`;
  
  // Log the URL in development for debugging
  if (import.meta.env.DEV) {
    console.log('API Request URL:', url);
    console.log('API Base URL:', API_BASE_URL);
  }
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Check if response is JSON before parsing
    const contentType = response.headers.get('content-type');
    let data;
    
    if (!contentType || !contentType.includes('application/json')) {
      const text = await response.text();
      console.error('Non-JSON response received:', text.substring(0, 200));
      console.error('API URL attempted:', url);
      throw new ApiClientError(
        `Expected JSON but received ${contentType || 'unknown content type'}. Check that VITE_API_BASE_URL is set correctly. Current API URL: ${url}`,
        response.status
      );
    }
    
    data = await response.json();
    
    if (!response.ok) {
      const error: ApiError = data;
      throw new ApiClientError(
        error.detail || 'Request failed',
        response.status,
        error
      );
    }
    
    return data as OverUnderResponse;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    
    // Handle network errors and JSON parse errors
    if (error instanceof SyntaxError && error.message.includes('JSON')) {
      throw new ApiClientError(
        `Invalid response from API. Make sure VITE_API_BASE_URL is set to your Railway backend URL (currently: ${API_BASE_URL})`,
        undefined
      );
    }
    
    throw new ApiClientError(
      error instanceof Error ? error.message : 'Network error occurred',
      undefined,
      undefined
    );
  }
}

