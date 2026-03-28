---
name: debug-workflow
description: Debug a failed workflow execution in halo_engine. Triggers when investigating execution failures, stuck workflows, or step errors.
---

# Debug Workflow Execution

## Steps

1. **Find the execution record**:
   - Odoo backend → Halo → Executions → filter by status = 'failed' or 'interrupted'
   - Or via shell: `self.env['halo.execution'].search([('status', '=', 'failed')])`

2. **Check execution steps**:
   - Open execution → Step History tab
   - Find the failed step (status = 'failed')
   - Read `error_message`, `input_data`, `output_data`

3. **For AI step failures**:
   - Check `ai_model`, `ai_prompt`, `ai_response` fields on the step record
   - Check `confidence_score` — was it below threshold?
   - Check `validation_result` — did structured output fail schema validation?
   - Check provider circuit breaker: `self.env['halo.ai.provider'].search([])`

4. **Check logs**:
   ```sh
   docker compose logs -f odoo 2>&1 | grep "halo_engine\|halo_ai"
   docker compose logs -f ollama    # If local AI
   ```

5. **Check queue_job**:
   - Odoo backend → Settings → Technical → Queue → Jobs
   - Find the job → read exception info

6. **Common issues**:
   | Symptom | Cause | Fix |
   |---------|-------|-----|
   | Step stuck in 'running' | Job crashed, no cleanup | Retry job or reset execution |
   | AI step 'failed' | Provider timeout / circuit open | Check provider health, restart Ollama |
   | Validation failed | AI returned wrong schema | Check output schema definition, adjust prompt |
   | Approval timeout | No one approved | Resend notification, check user email |

7. **Recovery**: If execution can be resumed from last completed step:
   ```python
   execution.action_retry()  # Resumes from failed step
   ```
