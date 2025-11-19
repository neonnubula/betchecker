# Frontend API Integration Guide

This guide explains how to use the BetChecker API integration in the frontend application.

## Overview

The API integration provides:
- **Type-safe API client** with TypeScript support
- **React hooks** for easy component integration
- **Error handling** with custom error types
- **Configuration** for development and production environments

## File Structure

```
src/
├── lib/
│   └── api/
│       ├── config.ts      # API base URL configuration
│       ├── types.ts       # TypeScript type definitions
│       ├── client.ts      # API client functions
│       └── index.ts       # Module exports
├── hooks/
│   └── usePlayerStats.ts  # React hook for player stats
└── components/
    └── PlayerStatsDemo.tsx # Example component
```

## Quick Start

### Using the React Hook (Recommended)

```tsx
import { usePlayerStats } from '@/hooks/usePlayerStats';

function MyComponent() {
  const { stats, loading, error } = usePlayerStats({
    player_name: 'Scott Pendlebury',
    stat: 'disposals',
    threshold: 23.5,
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!stats) return null;

  return (
    <div>
      <p>Over: {stats.over} games</p>
      <p>Under: {stats.under} games</p>
    </div>
  );
}
```

### Using the API Client Directly

```tsx
import { getPlayerOverUnder } from '@/lib/api';

async function fetchStats() {
  try {
    const stats = await getPlayerOverUnder({
      player_name: 'Scott Pendlebury',
      stat: 'disposals',
      threshold: 23.5,
    });
    console.log(`Over: ${stats.over}, Under: ${stats.under}`);
  } catch (error) {
    if (error instanceof ApiClientError) {
      console.error('API Error:', error.message);
    }
  }
}
```

## API Reference

### Types

#### `OverUnderParams`
Request parameters for the over/under endpoint:

```typescript
interface OverUnderParams {
  player_name?: string;    // Player's full name (exactly one of player_name or player_id required)
  player_id?: number;      // Player ID (exactly one of player_name or player_id required)
  stat: 'disposals' | 'goals';  // Statistic type
  threshold: number;       // Threshold value (e.g., 23.5)
  strict_over?: boolean;   // Optional: if true, over uses `>`, under uses `<=`
}
```

#### `OverUnderResponse`
Response from the API:

```typescript
interface OverUnderResponse {
  over: number;   // Number of games where stat was over threshold
  under: number;  // Number of games where stat was under threshold
}
```

### Functions

#### `getPlayerOverUnder(params: OverUnderParams): Promise<OverUnderResponse>`

Fetches over/under statistics for a player.

**Parameters:**
- `params.player_name` or `params.player_id` (exactly one required)
- `params.stat` - Must be `'disposals'` or `'goals'`
- `params.threshold` - Numeric threshold value
- `params.strict_over` - Optional boolean

**Returns:** Promise resolving to `OverUnderResponse`

**Throws:** `ApiClientError` if the request fails

### Hooks

#### `usePlayerStats(options: UsePlayerStatsOptions)`

React hook for fetching player statistics.

**Parameters:**
- Same as `OverUnderParams`, plus:
  - `enabled?: boolean` - Whether to automatically fetch on mount (default: `true`)

**Returns:**
```typescript
{
  stats: OverUnderResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}
```

## Configuration

### Development

The API automatically uses `http://localhost:8000` in development mode.

### Production

Set the `VITE_API_BASE_URL` environment variable:

```bash
VITE_API_BASE_URL=https://your-api-domain.com
```

Or update `src/lib/api/config.ts` to set your production URL.

### Vite Proxy (Optional)

The `vite.config.ts` includes a proxy configuration for `/search` that forwards to `http://localhost:8000`. This is optional since the backend has CORS enabled, but can be useful for avoiding CORS issues during development.

## Production Deployment

### Deploying the API to Railway

1. Connect your Git repository to Railway and set the project root to `BetChecker-BackEnd`.
2. Use `pip install -r requirements.txt` as the build command and `uvicorn app.main:app --host 0.0.0.0 --port $PORT` as the start command.
3. Add an environment variable `DB_PATH=BetChecker-BackEnd/BetChecker-PlayerDatabase/afl_stats.db`.
4. Once deployed, note the generated domain (for example, `https://betchecker-backend.up.railway.app`).

### Deploying the Frontend to Vercel

1. In Vercel, import the same Git repository and set the project root to `BetChecker-FrontEnd`.
2. Use the default Vite settings: build command `npm run build` and output directory `dist`.
3. Add an environment variable `VITE_API_BASE_URL` with the Railway domain from the backend deployment.
4. Deploy and verify that network requests in the browser target the Railway URL (visible in the DevTools Network tab).

### Post-Deployment Checklist

- Confirm the backend `/docs` endpoint loads over the Railway domain.
- Open the Vercel deployment and trigger a search; results should match the backend responses.
- Update `src/lib/api/config.ts` or project environment variables if the backend domain changes.

## Error Handling

The API client throws `ApiClientError` instances with:
- `message`: Error message
- `statusCode`: HTTP status code (if available)
- `response`: Full error response object

```tsx
import { ApiClientError } from '@/lib/api';

try {
  const stats = await getPlayerOverUnder(params);
} catch (error) {
  if (error instanceof ApiClientError) {
    console.error('Status:', error.statusCode);
    console.error('Message:', error.message);
  }
}
```

## Example Component

See `src/components/PlayerStatsDemo.tsx` for a complete example component that demonstrates:
- Form inputs for player name, stat, and threshold
- Loading states
- Error handling
- Displaying results

## Testing

To test the API integration:

1. **Start the backend server:**
   ```bash
   cd BetChecker-BackEnd
   source .venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend dev server:**
   ```bash
   cd BetChecker-FrontEnd
   npm run dev
   ```

3. **Use the example component** or create your own component using the hook.

## Backend API Documentation

For complete backend API documentation, see:
- `BetChecker-BackEnd/FRONTEND_API_INSTRUCTIONS.md`
- Interactive API docs: http://localhost:8000/docs (when backend is running)

