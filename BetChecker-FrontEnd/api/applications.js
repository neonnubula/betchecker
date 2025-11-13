import { createClient } from '@supabase/supabase-js';

// Create Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  // SECURITY: Check for authorization header
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ 
      error: 'Unauthorized',
      message: 'Access token required'
    });
  }
  
  const token = authHeader.substring(7); // Remove 'Bearer ' prefix
  
  // SECURITY: Check if token matches expected value
  const expectedToken = process.env.ADMIN_TOKEN || 'your-secret-admin-token';
  
  if (token !== expectedToken) {
    return res.status(403).json({ 
      error: 'Forbidden',
      message: 'Invalid access token'
    });
  }
  
  try {
    // Get all applications from Supabase
    const { data: applications, error } = await supabase
      .from('applications')
      .select('*')
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error('Supabase error:', error);
      throw error;
    }
    
    console.log('Retrieved applications:', applications.length);
    
    res.json({ 
      success: true, 
      count: applications.length,
      applications: applications
    });
    
  } catch (error) {
    console.error('API error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to retrieve applications',
      details: error.message
    });
  }
}
