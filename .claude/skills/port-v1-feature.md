---
name: port-v1-feature
description: Port a feature from Halo v1 (Flask/raw SQL) to Halo v2 (Odoo). Triggers when migrating functionality from the original HaloApp codebase.
---

# Port v1 Feature to v2

## Context

Halo v1 is at `/home/halo_user/HaloApp/`. It uses Flask, raw SQL (psycopg2), Celery, and vanilla HTML/JS.
Halo v2 uses Odoo CE 18 ORM, queue_job, and OWL 2.

## Steps

1. **Read v1 code** — understand the feature completely:
   - Route handler in `application/routes/`
   - DB operations in `application/services/postgres_client.py`
   - Service logic in `application/services/` or `application/scripts/`
   - Frontend in `application/static/snippets/` and `application/static/src/js/`

2. **Map to v2 architecture**:

   | v1 Pattern | v2 Equivalent |
   |-----------|---------------|
   | Flask route | Odoo controller (`@http.route`) or Odoo view action |
   | `postgres_client.py` SQL function | Odoo model method (ORM) |
   | `cursor.execute()` | `self.env['model'].search/create/write()` |
   | Celery task | `queue_job` with `with_delay()` |
   | `celery_beat` schedule | Odoo `ir.cron` |
   | HTML snippet + JS file | Odoo XML view + OWL 2 component |
   | Flask session | Odoo session (automatic) |
   | Connection pool | Odoo ORM (automatic) |

3. **Create the Odoo model** with equivalent fields (translate SQL columns to Odoo fields).

4. **Implement business logic** as model methods — NOT in controllers.

5. **Create views** (form, list, kanban) in XML.

6. **Add security rules** (ir.model.access.csv + record rules).

7. **Write tests** that verify behavior matches v1.

8. **If porting integration code** (Google, Microsoft, etc.):
   - Read `application/scripts/integrations/{service}.py`
   - Port to `halo_integrations` model with ORM token storage
   - Keep OAuth flow logic, replace HTTP client with `httpx`
