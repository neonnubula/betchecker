/**
 * React Hook for fetching player over/under statistics
 * 
 * Provides a convenient way to fetch and manage player stats in React components.
 */

import { useState, useEffect } from 'react';
import { getPlayerOverUnder } from '@/lib/api/client';
import type { OverUnderParams, OverUnderResponse } from '@/lib/api/types';
import { ApiClientError } from '@/lib/api/client';

interface UsePlayerStatsOptions extends OverUnderParams {
  /** Whether to automatically fetch when component mounts */
  enabled?: boolean;
}

interface UsePlayerStatsReturn {
  /** The over/under statistics */
  stats: OverUnderResponse | null;
  /** Whether the request is currently in progress */
  loading: boolean;
  /** Error message if the request failed */
  error: string | null;
  /** Function to manually refetch the stats */
  refetch: () => Promise<void>;
}

/**
 * Hook for fetching player over/under statistics
 * 
 * @param options - Request parameters and options
 * @returns Object containing stats, loading state, error, and refetch function
 * 
 * @example
 * ```tsx
 * function PlayerStatsComponent() {
 *   const { stats, loading, error } = usePlayerStats({
 *     player_name: 'Scott Pendlebury',
 *     stat: 'disposals',
 *     threshold: 23.5
 *   });
 * 
 *   if (loading) return <div>Loading...</div>;
 *   if (error) return <div>Error: {error}</div>;
 *   if (!stats) return null;
 * 
 *   return (
 *     <div>
 *       <p>Over: {stats.over} games</p>
 *       <p>Under: {stats.under} games</p>
 *       <p>Total: {stats.over + stats.under} games</p>
 *     </div>
 *   );
 * }
 * ```
 */
export function usePlayerStats(
  options: UsePlayerStatsOptions
): UsePlayerStatsReturn {
  const {
    player_name,
    player_id,
    stat,
    threshold,
    strict_over,
    enabled = true,
  } = options;

  const [stats, setStats] = useState<OverUnderResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    // Validate required parameters
    if (!stat || threshold === undefined) {
      return;
    }

    // Check that exactly one identifier is provided
    const hasPlayerName = player_name !== undefined && player_name !== '';
    const hasPlayerId = player_id !== undefined;
    
    if (!hasPlayerName && !hasPlayerId) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await getPlayerOverUnder({
        player_name,
        player_id,
        stat,
        threshold,
        strict_over,
      });
      
      setStats(result);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message);
      } else {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      }
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (enabled) {
      fetchStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [player_name, player_id, stat, threshold, strict_over, enabled]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
}

