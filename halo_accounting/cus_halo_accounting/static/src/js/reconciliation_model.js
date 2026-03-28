/** @odoo-module **/
/**
 * cus_halo_accounting – reconciliation_model.js
 *
 * Extends / replaces the upstream reconciliation model with:
 *   - Correct manual-proposition amount registration
 *   - NaN-safe proposition removal
 *   - Account code/name on auto-matched propositions
 *   - Statement-line name used as proposition label
 *   - all_lines_reconciled updated after each validate()
 */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// ─────────────────────────────────────────────────────────────────────────────
// StatementModel  (extends the base reconciliation model)
// ─────────────────────────────────────────────────────────────────────────────

export class HaloStatementModel {
    constructor(orm, env) {
        this.orm = orm;
        this.env = env;

        // Handle/line map
        this._lines = {};
        this._handlesByOrder = [];

        // Counters exposed to the view
        this.valuenow = 0;
        this.valuemax = 0;
        this.bank_statement_id = null;
        this.context = {};
    }

    // ── Public API ────────────────────────────────────────────────────────────

    getLine(handle) {
        return this._lines[handle];
    }

    // ── Validate ─────────────────────────────────────────────────────────────

    async validate(handle) {
        console.log("[validate] Starting for handle:", handle);
        const line = this.getLine(handle);
        if (!line) {
            console.warn("[validate] No line for handle:", handle);
            return { reconciled: [], updated: [] };
        }

        const props = (line.reconciliation_proposition || []).filter(p => !p.invalid);
        if (!props.length) {
            console.warn("[validate] No valid propositions for handle:", handle);
            return { reconciled: [], updated: [] };
        }

        // Separate existing-move-line ids from manually created ones
        const mv_line_ids = props
            .filter(p => p.id && !isNaN(p.id) && typeof p.id === 'number')
            .map(p => p.id);

        const new_mv_line_dicts = props
            .filter(p => !p.id || isNaN(p.id) || typeof p.id !== 'number')
            .map(p => this._formatToProcessReconciliation(line, p));

        const payload = [{
            id: line.id,
            type: 'statement_line',
            mv_line_ids,
            new_mv_line_dicts,
        }];

        console.log("[validate] Sending payload:", payload);

        const result = await this.orm.call(
            'account.reconciliation.widget',
            'process_move_lines',
            [payload],
        );

        console.log("[validate] Completed with:", result);
        console.log("[validate] Server reconciliation successful");

        // Update bank statement all_lines_reconciled
        if (this.bank_statement_id && this.bank_statement_id.id) {
            this.valuenow = (this.valuenow || 0) + 1;
            const allReconciled = this.valuenow >= this.valuemax;
            await this.orm.write(
                'account.bank.statement',
                [this.bank_statement_id.id],
                { all_lines_reconciled: allReconciled },
            );
            console.log("[validate] Updated bank statement all_lines_reconciled to:", allReconciled);
        }

        line.reconciled = true;
        return { reconciled: [handle], updated: [] };
    }

    // ── Proposition management ────────────────────────────────────────────────

    _addProposition(line, prop) {
        console.log("[_addProposition] Adding proposition:", prop);
        // Normalise amount sign
        if (prop.debit > 0) {
            prop.amount = prop.debit;
        } else if (prop.credit > 0) {
            prop.amount = -prop.credit;
        }
        prop.display = true;
        prop.invalid = false;

        if (!line.reconciliation_proposition) {
            line.reconciliation_proposition = [];
        }
        line.reconciliation_proposition.push(prop);
    }

    async addProposition(handle, mv_line_id, mode) {
        console.log("[addProposition] handle:", handle, "mv_line_id:", mv_line_id, "mode:", mode);
        const line = this.getLine(handle);
        if (!line) return;

        const targetMode = mode || line.mode || 'match_rp';
        const mvLines = line['mv_lines_' + targetMode] || [];
        const mvLineIdNumber = Number(mv_line_id);
        const prop = mvLines.find(l => l.id === mvLineIdNumber);
        if (!prop) {
            console.warn("[addProposition] Move line not found:", mv_line_id);
            return;
        }

        this._addProposition(line, { ...prop });
        // Remove from available list
        line['mv_lines_' + targetMode] = mvLines.filter(l => l.id !== mvLineIdNumber);
        await this._computeLine(line);
    }

    async createProposition(handle) {
        console.log("[createProposition] handle:", handle);
        const line = this.getLine(handle);
        if (!line) return;

        const quickCreate = line.quick_create_data || {};
        const newProp = this._formatQuickCreate(line, quickCreate);
        // Use a string-based ID so NaN checks work
        newProp.id = 'new_' + Date.now();
        this._addProposition(line, newProp);
        await this._computeLine(line);
    }

    async removeProposition(handle, propId) {
        console.log("[removeProposition] handle:", handle, "propId:", propId);
        const line = this.getLine(handle);
        if (!line || !line.reconciliation_proposition) return;

        const props = line.reconciliation_proposition;
        let idx = -1;

        // Numeric ID – exact match
        if (typeof propId === 'number' && !isNaN(propId)) {
            idx = props.findIndex(p => p.id === propId);
        }

        // String ID (manually created) – exact match
        if (idx === -1 && typeof propId === 'string') {
            idx = props.findIndex(p => String(p.id) === propId);
        }

        // NaN fallback – remove first manually-created proposition
        if (idx === -1) {
            console.warn("[removeProposition] NaN ID received, looking for first manual proposition");
            console.log("[removeProposition] Available propositions:", props);
            idx = props.findIndex(p => !p.id || isNaN(p.id) || typeof p.id === 'string');
        }

        if (idx === -1) {
            console.warn("[removeProposition] Proposition not found");
            return;
        }

        const removed = props.splice(idx, 1)[0];
        console.log("[removeProposition] Removed:", removed);

        // Restore to the move-lines list if it was a numeric server-side line
        if (typeof removed.id === 'number' && !isNaN(removed.id)) {
            const mode = line.mode || 'match_rp';
            if (!line['mv_lines_' + mode]) line['mv_lines_' + mode] = [];
            line['mv_lines_' + mode].push({ ...removed });
        }

        await this._computeLine(line);
    }

    // ── Formatting helpers ────────────────────────────────────────────────────

    _formatQuickCreate(line, values) {
        values = values || {};
        console.log("[_formatQuickCreate] values:", values, "line.balance:", line.balance);

        let amount = 0;
        switch (values.amount_type) {
            case 'percentage':
                amount = (line.balance && line.balance.amount || 0) * (values.amount || 0) / 100;
                break;
            case 'regex':
                if (values.amount_from_label_regex && line.st_line && line.st_line.name) {
                    const m = line.st_line.name.match(new RegExp(values.amount_from_label_regex));
                    if (m && m.length === 2) {
                        const clean = m[1].replace(/[^\d.,-]/g, '');
                        amount = parseFloat(clean.replace(',', '.')) || 0;
                    }
                }
                break;
            default:
                amount = parseFloat(values.amount) || (line.balance && line.balance.amount || 0);
        }

        const today = new Date().toISOString().slice(0, 10);

        return {
            id: null,
            name: (line.st_line && line.st_line.name) || values.label || '',
            account_id: values.account_id
                ? { id: values.account_id[0], display_name: values.account_id[1] }
                : false,
            analytic_distribution: values.analytic_distribution || {},
            journal_id: line.st_line && line.st_line.journal_id,
            date: today,
            amount,
            amount_str: String(amount),
            currency_id: line.st_line && line.st_line.currency_id,
            no_lead_link: true,
            display: true,
            invalid: false,
        };
    }

    _formatToProcessReconciliation(line, prop) {
        return {
            name: prop.name || (line.st_line && line.st_line.name) || '',
            debit: prop.amount > 0 ? prop.amount : 0,
            credit: prop.amount < 0 ? -prop.amount : 0,
            account_id: prop.account_id ? (prop.account_id.id || prop.account_id) : false,
            analytic_distribution: prop.analytic_distribution || {},
            journal_id: prop.journal_id ? (prop.journal_id.id || prop.journal_id) : false,
            date: prop.date || new Date().toISOString().slice(0, 10),
        };
    }

    // ── _computeLine  (balance recalculation) ─────────────────────────────────

    async _computeLine(line) {
        const props = (line.reconciliation_proposition || []).filter(p => !p.invalid);
        let total = (line.st_line && line.st_line.amount) || 0;

        for (const prop of props) {
            const amt = prop.partial_amount !== undefined ? prop.partial_amount : prop.amount;
            total -= (amt || 0);
            console.log("[_computeLine] After prop", prop.id, "amount", amt, "balance:", total);
        }

        const precision = 2;
        total = parseFloat(total.toFixed(precision)) || 0;
        console.log("[_computeLine] Final balance:", total);

        line.balance = {
            amount: total,
            amount_str: String(Math.abs(total)),
            currency_id: false,
            amount_currency: total,
            amount_currency_str: false,
            account_code: (line.balance && line.balance.account_code) || '',
        };
        line.balance.show_balance = line.balance.amount_currency !== 0;
        line.balance.type = line.balance.amount_currency
            ? (line.st_line && line.st_line.partner_id ? 0 : -1)
            : 1;
    }

    // ── Auto-matching via reconciliation rules ────────────────────────────────

    async applyReconciliationModel(handle, modelId) {
        console.log("[applyReconciliationModel] handle:", handle, "modelId:", modelId);
        const line = this.getLine(handle);
        if (!line) return;

        const [model] = await this.orm.read(
            'account.reconcile.model',
            [modelId],
            ['name', 'line_ids'],
        );
        if (!model) return;

        // Fetch line details (account code/name)
        const lineDetails = await this.orm.read(
            'account.reconcile.model.line',
            model.line_ids,
            ['account_id', 'label', 'amount_type', 'amount', 'analytic_distribution'],
        );

        for (const detail of lineDetails) {
            const prop = this._formatQuickCreate(line, {
                account_id: detail.account_id,
                // Label: prefer statement line name, fall back to rule name
                label: (line.st_line && line.st_line.name) || detail.label || model.name,
                amount_type: detail.amount_type,
                amount: detail.amount,
                analytic_distribution: detail.analytic_distribution,
            });
            prop.id = 'rule_' + modelId + '_' + Date.now();
            prop.reconcileModelId = modelId;
            this._addProposition(line, prop);
        }

        await this._computeLine(line);
    }
}

// Register in the action registry if needed
// registry.category("services").add("halo_statement_model", ...);
