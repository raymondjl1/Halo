---
name: write-deployment-guide
description: Write or update customer deployment documentation. Triggers when working on Docker configs, installation procedures, or docs/deployment-guide.md.
---

# Write Deployment Guide

## Before Starting
Read `documents/Halo v2/architecture.md` Section 8 (Deployment Architecture).

## Steps

1. **Target audience**: Non-technical customer or their IT person. Assume Docker knowledge but not Odoo knowledge.

2. **Structure**:
   - Prerequisites (Docker, GPU drivers, domain, Stripe account)
   - Quick start (5 commands to running instance)
   - Configuration (`.env` file, AI provider setup)
   - Module installation
   - License activation
   - First workflow setup
   - Troubleshooting (common issues + fixes)
   - Updating (how to pull new version)

3. **Use exact commands** — copy-paste ready. No pseudo-code.

4. **Test every command** on a clean environment before publishing.

5. **Include expected output** for key commands so users can verify success.

6. **Write at** `docs/deployment-guide.md`.
