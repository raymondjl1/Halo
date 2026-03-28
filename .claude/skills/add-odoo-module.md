---
name: add-odoo-module
description: Create a new Halo Odoo custom module with models, views, security, tests, and manifest. Triggers when scaffolding a new halo_* module in addons/.
---

# Add Odoo Module

## Steps

1. **Scaffold** the module:
   ```sh
   docker compose exec odoo odoo scaffold halo_{name} /mnt/extra-addons
   ```

2. **Create `__manifest__.py`**:
   - `name`: "Halo {Name}"
   - `version`: "18.0.1.0.0"
   - `category`: "Halo"
   - `depends`: at minimum `['halo_base']`
   - `data`: list all XML and CSV files
   - `license`: "LGPL-3"

3. **Create models** in `models/`:
   - File naming: `halo_{entity}.py`
   - Model naming: `halo.{domain}.{entity}`
   - Always include: `_name`, `_description`, `_order`
   - Always add `business_id = fields.Many2one('halo.business', required=True, ondelete='cascade')`
   - Import `__init__.py` chain

4. **Create views** in `views/`:
   - Form view: `halo_{model}_view_form`
   - List view: `halo_{model}_view_tree`
   - Menu items: `halo_menu_{section}`
   - Action: `halo_{model}_action`

5. **Create security** in `security/`:
   - `ir.model.access.csv`: read/write/create for `base.group_user`, full for `halo.group_admin`
   - `halo_security.xml`: record rule filtering by `business_id = user.business_id.id`

6. **Create tests** in `tests/`:
   - `test_{entity}.py` with `TransactionCase`
   - Test CRUD operations, constraints, business logic
   - Import in `tests/__init__.py`

7. **Create `CLAUDE.md`** in module root:
   - What the module does
   - Key models and relationships
   - What should never be changed
   - Testing instructions

8. **Install and test**:
   ```sh
   docker compose exec odoo odoo -d halo_dev -i halo_{name} --stop-after-init
   docker compose exec odoo odoo -d halo_test -i halo_{name} --test-enable --stop-after-init
   ```
