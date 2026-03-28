# Halo v2 — Reference Index

## Product Documentation

| Document | Path | Read When |
|----------|------|-----------|
| Requirements Specification | `documents/Halo v2/requirements.md` | Building features, writing feature descriptions, checking tier limits |
| Architecture Document | `documents/Halo v2/architecture.md` | Design decisions, understanding module relationships, deployment |
| Software Development Guide | `documents/Halo v2/software_development.md` | Coding standards, Odoo patterns, testing strategy |
| Automated Development Guide | `documents/Halo v2/automated_development.md` | CI/CD, Claude Code workflows, maintenance agents |
| Business Plan | `documents/halo_v2_business_plan.md` | Marketing, positioning, pricing, competitive analysis |
| Claude Code Project Definition | `documents/Halo v2/claude-code-project-definition.md` | Full project context for new Claude Code sessions |

## Configuration Files

| File | Path | Purpose |
|------|------|---------|
| Root CLAUDE.md | `CLAUDE.md` | Project context loaded every Claude Code session |
| Settings/Hooks | `.claude/settings.json` | Guardrails, session start, post-edit reminders |
| Skills | `.claude/skills/*.md` | Workflow-specific instructions for recurring tasks |

## Module Documentation

| Module | CLAUDE.md | Read Before |
|--------|-----------|-------------|
| halo_engine | `addons/halo_engine/CLAUDE.md` | Any workflow engine changes |
| halo_ai | `addons/halo_ai/CLAUDE.md` | Any AI inference changes |
| halo_integrations | `addons/halo_integrations/CLAUDE.md` | Any OAuth or API integration changes |
| halo_license | `addons/halo_license/CLAUDE.md` | Any billing or license changes |
| halo_knowledge | `addons/halo_knowledge/CLAUDE.md` | Any RAG or conversation changes |
| halo_market | `addons/halo_market/CLAUDE.md` | Any marketplace changes |
| halo_mobile | `addons/halo_mobile/CLAUDE.md` | Any mobile API changes |
| halo_website | `addons/halo_website/CLAUDE.md` | Any website content changes |

## Style & Content

| Resource | Path | Read When |
|----------|------|-----------|
| Style Guide | `docs/style-guide.md` | Writing any customer-facing content |
| Runbook | `docs/runbook.md` | Troubleshooting, operations, emergency procedures |

## External References

| Resource | Location | Read When |
|----------|----------|-----------|
| Odoo 18 docs | https://www.odoo.com/documentation/18.0/ | Odoo API/ORM questions |
| OCA queue_job | https://github.com/OCA/queue | Async job processing patterns |
| Stripe Billing docs | https://docs.stripe.com/billing | Subscription/webhook implementation |
| Anthropic Claude API | https://docs.anthropic.com/ | Claude AI integration |
| OpenAI API | https://platform.openai.com/docs | OpenAI integration |
| Halo v1 codebase | `/home/halo_user/HaloApp/` | Porting features from v1 to v2 |

## Marketing & Sales

| Resource | Path | Read When |
|----------|------|-----------|
| The Pitch (elevator + 2-min) | `documents/halo_v2_business_plan.md` §11 | Writing any marketing copy |
| Competitive landscape | `documents/halo_v2_business_plan.md` §2.3 | Writing comparison content |
| Pricing tiers | `documents/Halo v2/requirements.md` §2.3 | Pricing page, checkout flow |
| Target customer profile | `documents/halo_v2_business_plan.md` §2.2 | Audience targeting, ad copy |

## Templates & Marketplace

| Resource | Path | Read When |
|----------|------|-----------|
| Template documentation | `documents/templates/*.md` | [TODO: create as templates are built] |
| Seed script | `scripts/seed_templates.py` | Adding new marketplace templates |
