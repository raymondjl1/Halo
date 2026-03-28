---
name: fix-bug
description: Fix a bug in Halo v2. Triggers when working on issues labeled claude-fix or investigating failures in any halo_* module.
---

# Fix Bug

## Steps

1. **Read the bug report** — understand symptoms, steps to reproduce, expected vs actual behavior.

2. **Reproduce** — if possible, write a test that demonstrates the bug (should fail).

3. **Root-cause analysis**:
   - Check relevant module's `CLAUDE.md` for known complexity
   - Read the code path from trigger to failure
   - Check Odoo logs: `docker compose logs -f odoo | grep ERROR`
   - For AI issues: check `halo.ai.provider` circuit breaker state
   - For execution issues: check `halo.execution` + `halo.execution.step` records
   - For billing issues: check Stripe Dashboard + `halo.license` records

4. **Fix the bug** — minimal change, address root cause not symptoms.

5. **Verify the test now passes**.

6. **Run full module tests**:
   ```sh
   docker compose exec odoo odoo -d halo_test -i {module} --test-enable --stop-after-init
   ```

7. **Lint**:
   ```sh
   ruff check addons/
   ```

8. **Create PR** with: root cause, fix description, test added.
