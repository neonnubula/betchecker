/**
 * API Configuration
 * 
 * Manages the base URL for API requests in development and production environments.
 */

const isDevelopment = import.meta.env.DEV;
const isProduction = import.meta.env.PROD;

/**
 * Get the API base URL based on the current environment
 */
export const getApiBaseUrl = (): string => {
  // In development, use localhost:8000
  if (isDevelopment) {
    return 'http://localhost:8000';
  }
  
  // In production, use environment variable or fallback
  // TODO: Set this in your production environment variables
  return import.meta.env.VITE_API_BASE_URL || '[Your production URL]';
};

/**
 * API base URL for use in fetch requests
 */
export const API_BASE_URL = getApiBaseUrl();

