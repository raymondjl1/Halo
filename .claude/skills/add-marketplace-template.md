---
name: add-marketplace-template
description: Create a new workflow template for the Halo marketplace. Triggers when building pre-built workflow definitions for halo_market.
---

# Add Marketplace Template

## Steps

1. **Define the workflow** — what business problem does this template solve?
   - Name, description, category
   - Required integrations (Google, Microsoft, Email, etc.)
   - Step-by-step process with expected inputs/outputs

2. **Build the workflow definition JSON**:
   ```json
   {
     "name": "Invoice Processing",
     "description": "Extract, validate, and route invoices for approval",
     "category": "finance",
     "required_integrations": ["email", "google"],
     "steps": [
       {"name": "Receive Document", "type": "action", "config": {...}},
       {"name": "Classify Document", "type": "ai", "config": {...}, "output_schema": {...}},
       {"name": "Extract Fields", "type": "ai", "config": {...}, "output_schema": {...}},
       {"name": "Validate", "type": "rule", "config": {...}},
       {"name": "Route for Approval", "type": "approval", "config": {...}},
       {"name": "Process Invoice", "type": "action", "config": {...}}
     ],
     "connections": [...]
   }
   ```

3. **Create `halo.template` data record** (XML or Python seed):
   - Name, description, category, required_integrations
   - workflow_definition (the JSON above)

4. **Test end-to-end**: install template → configure integrations → execute → verify all steps pass.

5. **Write documentation** for the template (user-facing):
   - What it does
   - Required integrations
   - Configuration steps
   - Expected results

6. **Add to seed script**: `scripts/seed_templates.py`
