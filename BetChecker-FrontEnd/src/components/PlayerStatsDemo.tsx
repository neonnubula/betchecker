/**
 * Example Component: PlayerStatsDemo
 * 
 * Demonstrates how to use the usePlayerStats hook to fetch and display
 * player over/under statistics.
 * 
 * This is a reference implementation - you can use this as a starting point
 * for building your own player stats components.
 */

import React, { useState } from 'react';
import { usePlayerStats } from '@/hooks/usePlayerStats';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { StatType } from '@/lib/api/types';

export function PlayerStatsDemo() {
  const [playerName, setPlayerName] = useState('Scott Pendlebury');
  const [stat, setStat] = useState<StatType>('disposals');
  const [threshold, setThreshold] = useState('23.5');
  const [shouldFetch, setShouldFetch] = useState(false);

  const { stats, loading, error, refetch } = usePlayerStats({
    player_name: playerName,
    stat,
    threshold: parseFloat(threshold) || 0,
    enabled: shouldFetch,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!shouldFetch) {
      setShouldFetch(true);
    } else {
      refetch();
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Player Over/Under Statistics</CardTitle>
        <CardDescription>
          Search for AFL player statistics across their career history
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="playerName">Player Name</Label>
            <Input
              id="playerName"
              type="text"
              value={playerName}
              onChange={(e) => {
                setPlayerName(e.target.value);
                setShouldFetch(false);
              }}
              placeholder="e.g., Scott Pendlebury"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="stat">Statistic</Label>
            <Select
              value={stat}
              onValueChange={(value) => {
                setStat(value as StatType);
                setShouldFetch(false);
              }}
            >
              <SelectTrigger id="stat">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="disposals">Disposals</SelectItem>
                <SelectItem value="goals">Goals</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="threshold">Threshold</Label>
            <Input
              id="threshold"
              type="number"
              step="0.5"
              value={threshold}
              onChange={(e) => {
                setThreshold(e.target.value);
                setShouldFetch(false);
              }}
              placeholder="e.g., 23.5"
            />
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Loading...' : 'Get Statistics'}
          </Button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-800">Error: {error}</p>
          </div>
        )}

        {stats && !loading && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">Results</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{stats.over}</p>
                <p className="text-sm text-gray-600">Games Over</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">{stats.under}</p>
                <p className="text-sm text-gray-600">Games Under</p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-center text-sm text-gray-600">
                Total Games: <span className="font-semibold">{stats.over + stats.under}</span>
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

