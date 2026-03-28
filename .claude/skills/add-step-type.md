---
name: add-step-type
description: Add a new workflow step type to the halo_engine module. Triggers when creating new step types for the workflow builder.
---

# Add Workflow Step Type

## Steps

1. **Add type to selection field** on `halo.workflow.step`:
   ```python
   step_type = fields.Selection([
       ...existing types...,
       ('new_type', 'New Type'),
   ])
   ```

2. **Implement execution method** on `halo.execution`:
   ```python
   def _execute_new_type_step(self, step, step_input):
       """Execute a new_type step."""
       # Implementation here
       return result
   ```

3. **Add to execution dispatcher** in `_execute_step()`:
   ```python
   case 'new_type':
       result = self._execute_new_type_step(step, step_input)
   ```

4. **Add configuration fields** (if needed) to `step.config_json` schema.

5. **Add builder UI** — OWL 2 component or view extension for step configuration panel.

6. **Add icon and label** in the builder palette view.

7. **Write tests**:
   - Test execution with valid input
   - Test execution with invalid input
   - Test within a complete workflow
   - Test edge cases (timeout, missing config, etc.)

8. **Run tests**:
   ```sh
   docker compose exec odoo odoo -d halo_test -i halo_engine --test-enable --stop-after-init
   ```
