## Boilerplate Template

Overview

- Vite + React + TypeScript + Tailwind + shadcn-ui.
- Structure and CSS are preserved. Only text content has been replaced with placeholders.

Getting Started

1. Install Node.js 18+.
2. Install dependencies: `npm i`
3. Run dev server: `npm run dev`

Deployment (Vercel)

- This repository includes `vercel.json` for API functions and CORS headers.
- Connect the repo to Vercel and import. No changes required for a basic deploy.
- Add environment variables in Vercel dashboard as needed (see below).

Environment Variables (document only)

- SUPABASE_URL: Your Supabase URL.
- SUPABASE_ANON_KEY: Your Supabase anon key.
- ADMIN_TOKEN: Bearer token to read submissions via `api/applications.js`.
- RESEND_API_KEY: Resend API key to enable email sends via `api/send-email.js`.

Integrations

- Supabase: `api/submit-application.js` inserts form submissions into `applications` table (see `supabase-setup.sql`).
- Resend: `api/send-email.js` scaffold is present and returns a helpful message until configured.

Customization Checklist

- Replace placeholder copy in components with your product messaging.
- Replace `public/hero-background.png` with your OG/Twitter image (1200x630).
- Update `index.html` meta tags (title, description, keywords, author, URLs).
- See `IMAGE_GUIDE.md` for a list of images and guidance.

Notes on Routes and Structure

- All routes, IDs, and structure remain unchanged to avoid breaking references.
- Add new API routes under `api/` without renaming existing ones.

