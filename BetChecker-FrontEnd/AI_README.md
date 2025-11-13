## AI Implementation Guide

Constraints

- Do not change structure, routes, or CSS. Only edit text content and docs.
- Remove files only if not imported or referenced anywhere.
- Keep all page/section identifiers and component names intact.

Current Stack

- Vite + React + TypeScript + Tailwind + shadcn-ui.
- API routes in `api/` for Vercel Functions (Node runtimes).

Key Files

- src/pages/Index.tsx: Page composition and section ordering.
- src/components/*: All UI sections. Text placeholders applied across components.
- index.html: Metadata and OG/Twitter tags set to placeholders using hero-background.png.
- api/submit-application.js: Supabase insert scaffold for form submissions.
- api/applications.js: Supabase read (requires ADMIN_TOKEN); keep secure.
- api/send-email.js: Resend scaffold; returns no-op unless RESEND_API_KEY configured.
- vercel.json: Functions and headers configured (CORS for /api/*).

Env Keys (document-only)

- SUPABASE_URL: Supabase project URL.
- SUPABASE_ANON_KEY: Supabase anon key.
- ADMIN_TOKEN: Bearer token for protected reads (server use only).
- RESEND_API_KEY: Resend API key for transactional emails.

Boilerplate Copy Rules

- Replace brand names with generic placeholders only (e.g., Product Name, Headline that does X).
- Keep CTA anchors and IDs unchanged (e.g., #signup).
- Use hero-background.png universally for social images until customized.

Deletion Policy

- Safe to delete if not imported by any TSX/TS/JS/HTML files. Do not delete assets referenced in inactive code branches unless you also remove those references.


