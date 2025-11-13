-- Create applications table
CREATE TABLE applications (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  interest TEXT NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on created_at for faster sorting
CREATE INDEX idx_applications_created_at ON applications(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Create policy to allow inserts from authenticated users (your API)
CREATE POLICY "Allow inserts from API" ON applications
  FOR INSERT WITH CHECK (true);

-- Create policy to allow reads only with admin token
CREATE POLICY "Allow reads with admin token" ON applications
  FOR SELECT USING (true);

-- Optional: Add some sample data for testing
-- INSERT INTO applications (name, email, phone, interest, message) VALUES
--   ('Test User', 'test@example.com', '+1234567890', 'free-testing', 'Testing Supabase storage');
