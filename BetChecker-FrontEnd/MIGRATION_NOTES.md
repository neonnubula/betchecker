# Migration Notes: Static site → Lovable React Template

This doc captures our current content, images, tokens, and the sticky behavior so we can rebuild the site inside the cloned Lovable React/Tailwind app at vendor/pulse-template/.

## Repo layout
- Static prototype (reference): index.html, styles.css, scripts.js, assets/images/*
- Target app (source of truth): vendor/pulse-template/ (Vite + React + Tailwind + shadcn-ui)

---
## A) Content and sections
1) Header
- Brand: Hackademia
- Nav: Home, About, Contact, GitHub (external)

2) Hero
- Eyebrow: Academia, hacked
- H1: Hackademia: Write smarter. Stay safe.
- Lede: The safe cheat code for academic writing… without sacrificing your education or your future.
- CTA: Request Testing Access → #beta
- Media: hero robot image; gradient bg behind region

3) Why Hackademia (sticky stacked cards)
- Title: Why Hackademia
- Card 1: This is the Only AI Tool Built for Academic Integrity.
- Card 2: We’re building skills that last, not quick fixes
- Card 3: We’re making AI tools shame-free and transparent
- Behavior: cards stack as you scroll (pure CSS sticky)

4) Banner
- Built for Academic Excellence

5) Experience
- H2/lede
- Media frame
- H3 + paragraph

6) Academic Arsenal
- 6 feature cards (titles/descriptions from static)

7) Testimonials
- 4 quotes (Emily, Marcus, Priya, Ahmed)

8) Beta Form
- Required fields: name, email, phone (+country), reason; button + status

9) Footer
- © YEAR Hackademia

---
## B) Images
Place in template at public/assets/images/:
- hero-robot.png (alt: Futuristic robot)
- hero-gradient.png
- vision-blue-1.png (decorative)
- vision-orange-1.png (decorative)
- vision-blue-2.png (decorative)

---
## C) Design tokens (dark neon)
- bg: #0b0a1d; surface: #12122b; surface-2: #16163a
- text: #e6eaf3; muted: #a4a9c4; border: #26284a
- brand: #ff36a3; brand-2: #2dd4ff
- shadow presets: shadow-1, shadow-2, shadow-lifted (see static styles.css)
- Fonts: Inter (UI), Playfair for accents

---
## D) Sticky behavior (CSS baseline)
Container (scoped to Why only):

.staggered .stacked { height: 320vh; }

Cards:

.staggered .vision-card { position: sticky; top: 0; height: 100vh; }
.staggered .vision-card:nth-child(1) { top: 0;    z-index: 1; margin-top: 0; }
.staggered .vision-card:nth-child(2) { top: 48px; z-index: 2; margin-top: 100vh; }
.staggered .vision-card:nth-child(3) { top: 96px; z-index: 3; margin-top: 200vh; }

Notes:
- Adjust tops (48/96) to change how much the previous card’s top edge peeks.
- If content is short, keep 100vh; otherwise 75–80vh.

---
## E) Mapping to React/Tailwind
Components under src/:
- components/Nav.tsx
- components/Hero.tsx
- components/WhySticky.tsx
- components/Banner.tsx
- components/Experience.tsx
- components/Arsenal.tsx
- components/Testimonials.tsx
- components/BetaForm.tsx

Styling:
- Extend tokens in tailwind.config.ts (colors, shadows)
- Use Tailwind utilities for sticky: container h-[320vh], cards sticky top-[Xpx] h-screen

Assets:
- Copy images → public/assets/images/, refer via /assets/images/...

Accessibility & performance:
- loading="lazy" / decoding="async" on non-hero media
- aria-hidden on decorative bg images

---
## F) Migration steps
1) Images
- [ ] Create vendor/pulse-template/public/assets/images/
- [ ] Copy images listed above

2) Tailwind tokens
- [ ] Extend theme colors/shadows

3) Components
- [ ] Implement sections and replace text
- [ ] Build WhySticky per CSS baseline

4) Form UX
- [ ] Client-side validation & status; later connect endpoint

5) QA
- [ ] Desktop/mobile parity; scroll behavior verified

6) Run/Publish
- [ ] cd vendor/pulse-template && npm i && npm run dev
- [ ] Publish via Lovable/Netlify/Vercel

---
## G) Decisions
- Source of truth: the Lovable React app
- Static stays for reference only
- Sticky: CSS-only with staged margins and staggered tops
