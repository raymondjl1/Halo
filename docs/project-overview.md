# Halo v2 — Project Overview (Hybrid Bridge)

## How the Software and Knowledge Work Relate

Halo v2 is a software product AND a content-driven business. Both sides must stay in sync.

### The Software Side
- **Odoo custom modules** (`addons/halo_*`) — the product itself
- **Android app** (`android/`) — mobile companion
- **Docker deployment** (`docker/`) — how customers run it
- **CI/CD** (`.github/workflows/`) — automated build + test + deploy
- **Automated dev pipeline** — Claude Code implements features from GitHub Issues

### The Content Side
- **Product website** (`addons/halo_website/`) — landing page, pricing, blog
- **Marketing content** (`documents/marketing/`) — blog posts, comparison sheets
- **Product documentation** (`documents/Halo v2/`) — requirements, architecture, dev guide
- **Marketplace templates** (`documents/templates/`) — template docs for users
- **Customer guides** (`docs/deployment-guide.md`) — how customers deploy and use Halo
- **Style guide** (`docs/style-guide.md`) — voice, tone, terminology

## Where the Sides Connect

| Trigger | Software Side | Content Side |
|---------|--------------|-------------|
| New feature shipped | Module code + tests | Update requirements.md, write blog post, update website features |
| New template created | Template JSON in halo_market | Template documentation, marketplace listing copy |
| Pricing change | Stripe config + halo_license tier logic | Pricing page XML, requirements.md §2.3, blog announcement |
| Bug fix | Module code + tests | Update runbook if it's a common issue |
| New integration | OAuth + action methods in halo_integrations | Website feature list, integration setup guide |
| Architecture change | Module code restructure | Update architecture.md, update CLAUDE.md files |

## Workflow: Feature → Content Pipeline

```
1. Jeff writes feature issue → labeled claude-implement
2. Claude Code implements feature + tests → PR
3. Jeff reviews + merges
4. Jeff writes content issue: "Update website to include {feature}"
5. Claude Code updates website XML + blog post → PR
6. Jeff reviews tone/accuracy → merges
7. Deploy code + content together in next release
```

## Who Touches What

| Actor | Software | Content |
|-------|----------|---------|
| **Jeff** | Architecture decisions, PR review, release | Content approval, tone/voice review, business decisions |
| **Claude Code (autonomous)** | Feature implementation, bug fixes, tests, refactoring | Doc updates, blog drafts, website copy drafts |
| **Claude Code (interactive)** | Complex design, debugging | Marketing strategy, pitch refinement |
| **Maintenance agents** | Dependency updates, security scans, test coverage | Doc drift detection, doc sync |

## Key Rule

**Code and content must deploy together.** A feature that ships without updated documentation or marketing is incomplete. A marketing claim without shipped code is dishonest. The automated doc-sync agent (see `automated_development.md` §8.5) catches drift bi-weekly.
