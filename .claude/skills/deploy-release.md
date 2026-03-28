---
name: deploy-release
description: Build and deploy a Halo v2 release. Triggers when working with version tags, Docker images, or deployment procedures.
---

# Deploy Release

## Steps

1. **Ensure main is clean**: all PRs merged, CI green.

2. **Update version** in all `addons/halo_*/__manifest__.py` files.

3. **Run full test suite** on staging:
   ```sh
   docker compose exec odoo odoo -d halo_test \
     -i halo_base,halo_engine,halo_ai,halo_integrations,halo_knowledge,halo_license,halo_market,halo_mobile \
     --test-enable --stop-after-init
   ```

4. **Tag the release**:
   ```sh
   git tag v2.X.Y
   git push origin v2.X.Y
   ```

5. **GitHub Actions `deploy.yml`** triggers automatically:
   - Builds Docker image: `halo/odoo:v2.X.Y`
   - Pushes to Docker Hub
   - Tags as `latest`

6. **Customer update** (self-hosted):
   ```sh
   docker compose pull
   docker compose up -d
   # Odoo auto-updates modules on restart with --update flag
   ```

7. **Managed cloud update**:
   - Deploy to staging first, verify
   - Deploy to production
   - Monitor logs for 1 hour

8. **Post-deploy**: update CHANGELOG.md, notify customers.
