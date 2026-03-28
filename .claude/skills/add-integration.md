---
name: add-integration
description: Add a new external service integration (OAuth, API) to halo_integrations. Triggers when adding Google, Microsoft, LinkedIn, X, or other third-party connectors.
---

# Add Integration

## Steps

1. **Add integration type** to `halo.integration` selection:
   ```python
   integration_type = fields.Selection([
       ...existing...,
       ('new_service', 'New Service'),
   ])
   ```

2. **Create OAuth controller** in `halo_integrations/controllers/`:
   - Authorization URL generation endpoint
   - Callback handler at `/halo/oauth/callback/{service}`
   - Token exchange and storage

3. **Create action methods** on `halo.integration`:
   ```python
   def _action_new_service_send_message(self, params):
       """Send a message via New Service."""
       # OAuth token refresh check
       # API call
       # Return structured result
   ```

4. **Register actions** in `halo.integration.action` data records (XML).

5. **Add UI** in integration settings view (XML form view).

6. **Store tokens securely**: use `groups='base.group_system'` on token fields.

7. **Add token refresh** to the hourly ir.cron.

8. **Test OAuth flow** end-to-end:
   - Authorization redirect
   - Callback handling
   - Token storage
   - Action execution
   - Token refresh

9. **Write tests** with mocked OAuth responses.
