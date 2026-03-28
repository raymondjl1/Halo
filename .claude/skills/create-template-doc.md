---
name: create-template-doc
description: Create documentation for a marketplace workflow template. Triggers when documenting templates in documents/templates/ or halo_market data.
---

# Create Template Documentation

## Steps

1. **Read the template definition** (JSON workflow in `halo.template` record or seed script).

2. **Write documentation** at `documents/templates/{template-name}.md`:
   ```markdown
   # {Template Name}

   ## What It Does
   [1-2 sentences: the business outcome]

   ## Required Integrations
   - [List each: Google Sheets, Email, etc.]

   ## How It Works
   1. [Step 1: what happens]
   2. [Step 2: what happens]
   ...

   ## Configuration
   - [What the user needs to set up before running]

   ## Example
   [Concrete example of input → output]
   ```

3. **Use customer-friendly language** — no technical jargon. The reader is a small business owner.

4. **Include a screenshot or diagram** if helpful (describe where to add it).

5. **Verify the template works end-to-end** before documenting — never document untested templates.
