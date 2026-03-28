# Halo v2

## Purpose

Halo v2 is a deterministic AI workflow engine built on Odoo CE 18. Small businesses build reliable, auditable workflows through a no-code visual interface. The workflow structure is deterministic (same input → same path → same output). AI provides intelligence within bounded steps — with structured output enforcement, guardrails, and human-in-the-loop escalation.

**Stack:** Odoo CE 18 (Python/OWL 2) · PostgreSQL 16 · Redis 7 · Ollama (local AI) · Claude/OpenAI API (cloud AI) · Stripe Billing · Docker Compose · Android (Kotlin/Compose)

**Revenue model:** Free ($0, 3 workflows) · Pro ($49/mo) · Business ($149/mo) · Enterprise ($299/mo)

## Repo Map

```
halo-v2/
├── addons/                     # Odoo custom modules (THE PRODUCT)
│   ├── halo_base/              # Shared models, config, utilities
│   ├── halo_engine/            # ★ Workflow builder + execution engine (CORE IP)
│   ├── halo_ai/                # ★ Model router, structured output, guardrails, circuit breaker
│   ├── halo_integrations/      # Google, Microsoft, LinkedIn, X, Email, Webhooks (OAuth)
│   ├── halo_knowledge/         # Document upload, embedding, RAG, agents, conversations
│   ├── halo_license/           # ★ Stripe sync, tier enforcement, usage metering
│   ├── halo_market/            # Workflow template marketplace
│   ├── halo_mobile/            # REST API for Android app, FCM push
│   └── halo_website/           # Landing page, pricing, blog, onboarding wizard
├── android/                    # Android app (Kotlin + Jetpack Compose)
├── docker/                     # Dockerfile, nginx.conf, odoo.conf
├── scripts/                    # migrate_v1.py, seed_templates.py
├── tests/                      # Integration tests outside Odoo
├── documents/                  # Product docs (requirements, architecture, business plan)
├── .github/workflows/          # CI, deploy, claude-implement, claude-fix, claude-review, maintenance
├── docker-compose.yml          # Production
├── docker-compose.dev.yml      # Development
└── .env.example                # Environment variable template (NEVER commit .env)
```

★ = Critical modules — read their local CLAUDE.md before modifying.

## Key Files

| Working In | Read First |
|-----------|-----------|
| Any Odoo module | This file + that module's `CLAUDE.md` |
| `halo_engine` | `documents/Halo v2/architecture.md` §5.1 |
| `halo_ai` | `documents/Halo v2/architecture.md` §5.2 |
| `halo_license` | `documents/Halo v2/architecture.md` §6.3 |
| `halo_integrations` | `documents/Halo v2/architecture.md` §9 |
| `android/` | `documents/Halo v2/software_development.md` §5 |
| `.github/workflows/` | `documents/Halo v2/automated_development.md` |
| Website/marketing content | `documents/halo_v2_business_plan.md` §11 (The Pitch) |
| Pricing/tier changes | `documents/Halo v2/requirements.md` §2.3 |

## Documentation

| Document | Purpose |
|----------|---------|
| `documents/Halo v2/requirements.md` | What to build — 120+ functional requirements |
| `documents/Halo v2/architecture.md` | How it's structured — modules, data flow, ADRs |
| `documents/Halo v2/software_development.md` | How to build it — standards, patterns, testing |
| `documents/Halo v2/automated_development.md` | CI/CD pipeline, Claude Code agents, quality gates |
| `documents/halo_v2_business_plan.md` | Why — market analysis, revenue model, go-to-market |
| `docs/style-guide.md` | Voice, tone, terminology for all content |
| `docs/runbook.md` | Commands, troubleshooting, emergency procedures |

## Rules & Commands

### Daily Commands

```sh
docker compose -f docker-compose.dev.yml up -d                    # Start dev
docker compose exec odoo odoo -d halo_dev --dev=all               # Dev mode
docker compose exec odoo odoo -d halo_test -i halo_engine --test-enable --stop-after-init  # Test
docker compose logs -f odoo                                        # Logs
ruff check addons/ && ruff format addons/                          # Lint + format
docker compose exec ollama ollama list                             # AI models
nvidia-smi                                                         # GPU
git tag v2.X.Y && git push origin v2.X.Y                          # Release
```

### Odoo Conventions

- **All DB access via Odoo ORM** — never raw SQL, never `self.env.cr.execute()`
- Model names: `halo.{domain}.{entity}` · Files: `halo_{entity}.py`
- Views: `halo_{model}_view_{type}` · Menus: `halo_menu_{section}`
- Every model: `security/ir.model.access.csv` + record rules with `business_id` filter
- Async operations via `queue_job`: `record.with_delay().method()`
- Logger: `_logger = logging.getLogger(__name__)` — never `print()`
- Linter: `ruff` · Formatter: `ruff format`

### Absolute Rules — NEVER Do These

1. **Never** raw SQL — Odoo ORM only (no psycopg2, no cr.execute)
2. **Never** commit `.env`, API keys, passwords, tokens, or Stripe keys
3. **Never** modify audit records (`halo.execution`, `halo.execution.step`) after creation
4. **Never** push to `main` — always feature branch + PR + CI green + Jeff approves
5. **Never** run `rm -rf`, `git push --force`, `git reset --hard`
6. **Never** create models without security rules (ir.model.access.csv + record rules)
7. **Never** log secrets — not even in DEBUG level
8. **Never** use `sudo()` without a justifying comment
9. **Never** make AI steps without structured output schemas + guardrails
10. **Never** call external APIs synchronously in the request cycle — use `queue_job`

### Content Rules (Customer-Facing)

- Say "workflow" not "process" or "pipeline"
- Say "reliable" or "same every time" not "deterministic"
- Say "your servers" not "on-premise"
- Say "AI-powered step" not "LLM call" or "inference"
- Brand: "Halo" (capital H, one word, no "App")
- Never make unsubstantiated uptime/SLA/compliance claims
- Never name competitors in marketing copy
