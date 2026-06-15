Tailwind Migration Plan
-----------------------

Goal
- Replace legacy CSS with Tailwind for faster development and consistent design tokens.

Phases
1. Add Tailwind as a dev dependency and configure `tailwind.config.js`.
2. Create design tokens and map existing colors from `static/css/style.css`.
3. Migrate components incrementally: navbar, tweet card, forms.
4. Use `@apply` to reuse common classes and create component partials.

Notes
- Keep legacy styles until feature parity is reached; progressively switch templates.
