# Halo v2 — Style Guide

## Brand

- **Name:** Halo (capital H, one word — never "HaloApp," "Halo App," or "HALO")
- **Company:** Halo Solutions Inc.
- **Product tagline:** "AI automation that works the same way every time."
- **Logo/colors:** [TODO: finalize brand design]

## Voice & Tone

### Customer-Facing (Website, Marketing, Blog)
- **Confident but approachable.** We know what we built and why it matters.
- **Direct.** Lead with the outcome, not the technology. "Process invoices in 2 minutes" > "Leverage our AI-powered document extraction pipeline."
- **Honest.** Acknowledge tradeoffs. Don't oversell. "Works best for repeatable workflows" is better than "AI that does everything."
- **First-person for blog posts.** "I built Halo because..." — the solo founder story is an asset.

### Technical Documentation
- **Precise and concise.** Code samples over prose. Tables over paragraphs.
- **Example-heavy.** Show, don't just tell.
- **Commands are copy-paste ready.** Include expected output when helpful.

### Error Messages (In-App)
- **Human-readable.** "This workflow has no steps yet. Add at least one step before activating." — not "ValidationError: step_ids constraint violated."
- **Actionable.** Tell the user what to do, not just what went wrong.

## Terminology

### Customer-Facing (ALWAYS use these)

| Use This | Not This |
|----------|----------|
| workflow | process, pipeline, automation |
| reliable / same every time | deterministic |
| your servers / your hardware | on-premise, on-prem |
| AI-powered step | LLM call, inference, model invocation |
| Halo | HaloApp, Halo App, HALO |
| workflow template | agent, bot |
| step | node, activity, task (in workflow context) |
| approval | human-in-the-loop, HITL |

### Technical (OK in docs and code)
All precise technical terms are fine in architecture docs, code comments, and developer guides: deterministic, LLM, inference, ORM, circuit breaker, structured output, guardrails, etc.

## Formatting Standards

- **All documents in Markdown** (GitHub-flavored)
- **Tables** for comparisons and feature lists
- **Code blocks** with language tags for all commands and code
- **Paragraphs** under 4 sentences
- **Headers** use sentence case ("How it works" not "How It Works")
- **Lists** for 3+ items
- **Bold** for emphasis, not ALL CAPS
- **No emojis** in documentation or marketing unless explicitly requested

## Content Rules

- Never make unsubstantiated claims (no uptime %, no SLA, no compliance certifications unless real)
- Never name competitors in marketing copy — compare features and categories
- Never publish customer names without explicit permission
- Pricing must always match Stripe configuration: Free $0, Pro $49, Business $149, Enterprise $299
- All customer-facing content requires Jeff's approval before publication
