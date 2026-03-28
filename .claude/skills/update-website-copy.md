---
name: update-website-copy
description: Update customer-facing website copy on the Halo landing page, pricing page, or feature pages. Triggers when editing addons/halo_website/ views or marketing text.
---

# Update Website Copy

## Before Starting
Read `docs/style-guide.md` and `documents/halo_v2_business_plan.md` Section 11 (The Pitch).

## Steps

1. **Identify the page**: landing (`halo_landing_page.xml`), pricing (`halo_pricing_page.xml`), or other.

2. **Edit the Odoo website XML template** in `addons/halo_website/views/`.

3. **Follow content rules**:
   - "Halo" (capital H, one word)
   - "workflow" not "process"
   - "reliable" / "same every time" not "deterministic"
   - "your servers" not "on-premise"
   - No unsubstantiated claims (no uptime guarantees, no compliance certs)
   - No competitor names
   - Pricing must match Stripe: Free $0, Pro $49, Business $149, Enterprise $299

4. **Preview**: run dev mode and check the page in browser.

5. **Mobile check**: verify responsive layout on mobile viewport.

6. **Submit PR** — Jeff approves all customer-facing copy changes.
