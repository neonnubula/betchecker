# Quick Start - Testing the API Integration

## ✅ Ready to Test!

The frontend API integration is complete and ready for testing. Here's how to get started:

## Step 1: Start the Backend Server

Open a terminal and navigate to the backend directory:

```bash
cd BetChecker-BackEnd
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

✅ **Backend is running when you see this!**

## Step 2: Start the Frontend Dev Server

Open a **new terminal** and navigate to the frontend directory:

```bash
cd BetChecker-FrontEnd
npm run dev
```

You should see output like:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:8080/
  ➜  Network: use --host to expose
```

✅ **Frontend is running when you see this!**

## Step 3: Test the API Integration

1. **Open your browser** and navigate to:
   ```
   http://localhost:8080/test-api
   ```

2. **Fill in the form:**
   - Player Name: `Scott Pendlebury` (or any player in your database)
   - Statistic: Select `Disposals` or `Goals`
   - Threshold: Enter a number (e.g., `23.5`)

3. **Click "Get Statistics"** to fetch the data

4. **You should see:**
   - Loading state while fetching
   - Results showing "Games Over" and "Games Under" counts
   - Total games count

## Troubleshooting

### Backend not responding?
- Check that the backend server is running on port 8000
- Try accessing http://localhost:8000/docs to see the API documentation
- Check terminal for any error messages

### Frontend shows CORS error?
- The backend has CORS enabled, so this shouldn't happen
- If it does, make sure the backend is running on port 8000
- Check browser console for detailed error messages

### Player not found?
- Make sure the player name matches exactly as stored in the database
- Check the database for available players
- Try "Scott Pendlebury" (case-sensitive)

### Network error?
- Ensure both servers are running
- Check that ports 8000 (backend) and 8080 (frontend) are not blocked
- Check browser console for detailed error messages

## What's Been Implemented

✅ Type-safe API client (`src/lib/api/`)  
✅ React hook (`src/hooks/usePlayerStats.ts`)  
✅ Example component (`src/components/PlayerStatsDemo.tsx`)  
✅ Test page (`src/pages/TestAPI.tsx`)  
✅ Route configured (`/test-api`)  
✅ Error handling  
✅ Loading states  

## Next Steps

After testing, you can:
1. Integrate the `usePlayerStats` hook into your own components
2. Customize the UI to match your design
3. Add additional features (filters, date ranges, etc.)
4. Set up production API URL in environment variables

## API Documentation

- Full API guide: `API_INTEGRATION_GUIDE.md`
- Backend API spec: `BetChecker-BackEnd/FRONTEND_API_INSTRUCTIONS.md`
- Interactive API docs: http://localhost:8000/docs (when backend is running)

