# Halo v2 — Runbook

## Common Tasks

### Start Development Environment
```sh
docker compose -f docker-compose.dev.yml up -d
docker compose exec odoo odoo -d halo_dev --dev=all
# Access at http://localhost:8069 (admin/admin)
```

### Install / Update a Module
```sh
# Install
docker compose exec odoo odoo -d halo_dev -i halo_engine --stop-after-init
# Update
docker compose exec odoo odoo -d halo_dev -u halo_engine --stop-after-init
# Install all Halo modules
docker compose exec odoo odoo -d halo_dev -i halo_base,halo_engine,halo_ai,halo_integrations,halo_knowledge,halo_license,halo_market,halo_mobile,halo_website --stop-after-init
```

### Run Tests
```sh
# Single module
docker compose exec odoo odoo -d halo_test -i halo_engine --test-enable --stop-after-init
# All modules
docker compose exec odoo odoo -d halo_test -i halo_base,halo_engine,halo_ai,halo_integrations,halo_knowledge,halo_license,halo_market,halo_mobile --test-enable --stop-after-init
```

### Lint & Format
```sh
ruff check addons/
ruff format addons/
```

### View Logs
```sh
docker compose logs -f odoo                          # App logs
docker compose logs -f odoo 2>&1 | grep ERROR        # Errors only
docker compose logs -f ollama                        # AI inference logs
docker compose logs -f db                            # PostgreSQL
```

### Database Operations
```sh
docker compose exec db psql -U odoo -d halo_dev                          # DB shell
docker compose exec db pg_dump -U odoo halo_dev > backup_$(date +%Y%m%d).sql  # Backup
docker compose exec db psql -U odoo -d halo_dev < backup.sql             # Restore
```

### GPU / AI
```sh
nvidia-smi                                           # GPU status
docker compose exec ollama ollama list                # Loaded models
docker compose exec ollama ollama pull mistral:latest  # Pull model
curl http://localhost:11434/api/tags                  # Test Ollama API
```

### Release
```sh
git tag v2.X.Y && git push origin v2.X.Y             # Triggers CI deploy
```

---

## Troubleshooting

### Odoo Won't Start
1. Check logs: `docker compose logs odoo`
2. Common causes: missing Python dependency, bad addon, DB connection refused
3. Fix: `docker compose exec odoo pip install {package}` or fix the addon code
4. Nuclear: `docker compose down && docker compose up -d`

### Tests Failing
1. Read the traceback in test output
2. If DB-related: ensure test database exists and is clean
3. If module-related: check `__manifest__.py` dependencies
4. Run single test: `docker compose exec odoo odoo -d halo_test -i halo_engine --test-tags=TestHaloWorkflow --stop-after-init`

### AI Provider Not Responding
See skill: `.claude/skills/debug-ai-provider.md`

### Workflow Execution Stuck
See skill: `.claude/skills/debug-workflow.md`

### Stripe Webhook Not Processing
1. Check Stripe Dashboard → Developers → Webhooks → Event log
2. Check Odoo logs: `docker compose logs odoo | grep stripe`
3. Verify webhook signing secret in Odoo system parameters
4. Test with Stripe CLI: `stripe listen --forward-to localhost:8069/halo/stripe/webhook`

### Docker Out of Disk Space
```sh
docker system df                                     # Check usage
docker system prune -a                               # Clean unused images/containers
docker volume prune                                  # Clean unused volumes (CAREFUL)
```

---

## Emergency Procedures

### Full Stack Restart
```sh
docker compose down
docker compose up -d
```

### Database Emergency Backup
```sh
docker compose exec db pg_dump -U odoo halo > /tmp/emergency_$(date +%Y%m%d_%H%M%S).sql
```

### Rollback a Release
```sh
# Pin to specific version
docker compose pull halo/odoo:v2.X.Y  # Previous version
docker compose up -d
```

### Reset Development Database
```sh
docker compose exec db dropdb -U odoo halo_dev
docker compose exec db createdb -U odoo halo_dev
docker compose exec odoo odoo -d halo_dev -i halo_base,halo_engine,halo_ai,halo_integrations,halo_knowledge,halo_license,halo_market,halo_mobile,halo_website --stop-after-init
```
