import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    if (!process.env.RESEND_API_KEY) {
      return res.status(200).json({
        success: false,
        message: 'Resend not configured yet. Add RESEND_API_KEY to enable.',
      });
    }

    const { to, subject, text } = req.body || {};

    // Scaffold only: no-op if missing params
    if (!to || !subject || !text) {
      return res.status(200).json({
        success: true,
        message: 'Resend scaffold working. Provide { to, subject, text } to send.',
      });
    }

    // Optional: Uncomment to actually send when ready
    // const result = await resend.emails.send({ from: 'onboarding@resend.dev', to, subject, text });

    return res.json({ success: true, message: 'Email send scaffold ready.' });
  } catch (error) {
    console.error('Resend error:', error);
    return res.status(500).json({ error: 'Internal server error', details: error.message });
  }
}


