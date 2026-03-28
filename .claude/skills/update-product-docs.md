---
name: update-product-docs
description: Update product documentation (requirements, architecture, dev guide) to match current code. Triggers when documents/Halo v2/ files drift from implementation.
---

# Update Product Documentation

## Steps

1. **Identify the drift**: compare current code to the relevant document section.

2. **Update the document** — keep the same structure, update only what changed.

3. **Common updates**:
   - New model added → update architecture.md §4 (module table) and §6 (data models)
   - New endpoint added → update requirements.md (functional requirements)
   - New command needed → update software_development.md §2 (commands)
   - New workflow added → update automated_development.md if CI-related

4. **Don't add filler** — documents should be concise and accurate.

5. **Mark genuinely unknown sections** with `[TODO: ...]`.

6. **Submit PR** for review.
