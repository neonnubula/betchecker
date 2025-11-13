import React from 'react';
import { PlayerStatsDemo } from '@/components/PlayerStatsDemo';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

/**
 * Test page for BetChecker API integration
 * 
 * This page demonstrates the API integration with a working example.
 * Navigate to /test-api to see it in action.
 */
const TestAPI = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 py-12 sm:py-16">
        <div className="container px-4 sm:px-6 lg:px-8 mx-auto">
          <div className="mb-8 text-center">
            <h1 className="text-3xl sm:text-4xl font-bold mb-4">
              BetChecker API Test
            </h1>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Test the player over/under statistics API integration. 
              Make sure the backend server is running on port 8000.
            </p>
          </div>
          
          <PlayerStatsDemo />
          
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h2 className="font-semibold mb-2">Testing Instructions:</h2>
            <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
              <li>Ensure the backend server is running: <code className="bg-gray-100 px-1 rounded">uvicorn app.main:app --reload --port 8000</code></li>
              <li>Enter a player name (e.g., "Scott Pendlebury")</li>
              <li>Select a statistic type (Disposals or Goals)</li>
              <li>Enter a threshold value (e.g., 23.5)</li>
              <li>Click "Get Statistics" to fetch the data</li>
            </ol>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default TestAPI;

