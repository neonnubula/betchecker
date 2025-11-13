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

  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    console.log('API route called with method:', req.method);
    console.log('Request body:', req.body);
    
    const { name, email, phone, interest, message } = req.body;
    
    // Basic validation
    if (!name || !email || !phone || !interest || !message) {
      return res.status(400).json({ 
        error: 'Validation failed', 
        details: ['All fields are required'] 
      });
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ 
        error: 'Validation failed', 
        details: ['Invalid email format'] 
      });
    }
    
    // Phone validation
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
    if (!phoneRegex.test(cleanPhone) || cleanPhone.length < 7 || cleanPhone.length > 15) {
      return res.status(400).json({ 
        error: 'Validation failed', 
        details: ['Invalid phone number format'] 
      });
    }
    
    // Create application object
    const application = {
      name: name,
      email: email,
      phone: phone,
      interest: interest,
      message: message,
      created_at: new Date().toISOString()
    };
    
    // Log the application for storage
    console.log('=== NEW APPLICATION SUBMISSION ===');
    console.log('Name:', name);
    console.log('Email:', email);
    console.log('Phone:', phone);
    console.log('Interest:', interest);
    console.log('Message:', message);
    console.log('==================================');
    
    // Store in Supabase
    try {
      const { data, error } = await supabase
        .from('applications')
        .insert([application])
        .select();
      
      if (error) {
        console.error('Supabase storage error:', error);
        throw error;
      }
      
      console.log('Application stored in Supabase successfully:', data);
    } catch (supabaseError) {
      console.error('Supabase storage error:', supabaseError);
      // Continue even if Supabase fails - we still have the logs
    }
    
    console.log('Application processed successfully:', { email });
    
    res.json({ 
      success: true, 
      message: 'Application submitted successfully! We will review and get back to you within 2-3 business days.',
      emailSent: false
    });
    
  } catch (error) {
    console.error('API error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: 'Failed to process application',
      details: error.message
    });
  }
}
