/** @odoo-module **/
/**
 * cus_halo_accounting – reconciliation.js
 *
 * StatementAction & StatementRenderer:
 *   - _onValidate: single-instance guard, delegates to model.validate()
 *   - showRainbowMan: OWL 18-compliant DoneMessage dialog + rainbow effect
 *   - onCloseBankStatement / onGoToBankStatement
 *   - _setupEventListeners / cleanup
 */

import {
    Component, useState, onMounted, useRef, useEffect, onWillUnmount, xml,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { DateTime } from "luxon";
import { session } from "@web/session";

// ─────────────────────────────────────────────────────────────────────────────
// DoneMessage – OWL 18 component shown in the completion dialog
// ─────────────────────────────────────────────────────────────────────────────

export class DoneMessage extends Component {
    static template = "cus_halo_accounting.DoneMessage";

    static props = {
        duration:              String,
        number:                Number,
        timePerTransaction:    Number,
        context:               { type: Object, optional: true },
        bank_statement_id:     { type: Object, optional: true },
        onCloseBankStatement:  { type: Function, optional: true },
        onGoToBankStatement:   { type: Function, optional: true },
        close:                 { type: Function },        // required by dialog service
    };

    async handleClose() {
        if (this.props.onCloseBankStatement) await this.props.onCloseBankStatement();
        this.props.close();
    }

    async handleGoTo(event) {
        if (this.props.onGoToBankStatement) await this.props.onGoToBankStatement(event);
        this.props.close();
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// StatementAction
// ─────────────────────────────────────────────────────────────────────────────

export class StatementAction extends Component {
    static template = "cus_halo_accounting.StatementAction";

    setup() {
        super.setup?.(...arguments);

        this.orm           = useService("orm");
        this.notification  = useService("notification");
        this.actionService = useService("action");
        this.effect        = useService("effect");
        this.dialog        = useService("dialog");

        this.state = useState({
            valuenow:         0,
            valuemax:         0,
            context:          {},
            bank_statement_id: null,
            notifications:    [],
        });

        // Track start time for duration calculation
        this.time = Date.now();

        // Prevent re-entrant validation
        this.isValidating = false;

        // Bind event handlers once
        this._boundOnValidate          = this._onValidate.bind(this);
        this._boundOnRemoveProposition = this._onRemoveProposition.bind(this);
        this._boundOnAddProposition    = this._onAddProposition.bind(this);
        this._boundOnApplyModel        = this._onApplyModel.bind(this);
        this._boundShowRainbowMan      = this.showRainbowMan.bind(this);

        useEffect(() => {
            this._setupEventListeners();
            return () => this._teardownEventListeners();
        });

        onMounted(() => this.onMounted());
    }

    async onMounted() {
        await this._loadStatementLines();
    }

    // ── Event bus wiring ─────────────────────────────────────────────────────

    _setupEventListeners() {
        this.env.bus.addEventListener('validate-line',        this._boundOnValidate);
        this.env.bus.addEventListener('remove-proposition',   this._boundOnRemoveProposition);
        this.env.bus.addEventListener('add-proposition',      this._boundOnAddProposition);
        this.env.bus.addEventListener('apply-reconcile-model',this._boundOnApplyModel);
        this.env.bus.addEventListener('show-rainbow-man',     this._boundShowRainbowMan);
    }

    _teardownEventListeners() {
        this.env.bus.removeEventListener('validate-line',        this._boundOnValidate);
        this.env.bus.removeEventListener('remove-proposition',   this._boundOnRemoveProposition);
        this.env.bus.removeEventListener('add-proposition',      this._boundOnAddProposition);
        this.env.bus.removeEventListener('apply-reconcile-model',this._boundOnApplyModel);
        this.env.bus.removeEventListener('show-rainbow-man',     this._boundShowRainbowMan);
    }

    // ── _onValidate ───────────────────────────────────────────────────────────

    async _onValidate({ detail }) {
        console.log("[_onValidate] Event triggered:", detail);
        console.log("[_onValidate] Validating status:", this.isValidating);

        if (this.isValidating) {
            console.warn("[_onValidate] Validation already in progress");
            return;
        }

        this.isValidating = true;
        const handle = detail.handle || this.props.handle;
        console.log("[_onValidate] Validating handle:", handle);

        try {
            const result = await this.model.validate(handle);
            console.log("[_onValidate] Validate result:", result);

            this.state.valuenow = (this.state.valuenow || 0) + 1;
            console.log(
                "[_onValidate] Progress:", this.state.valuenow, "/", this.state.valuemax
            );

            if (this.state.valuenow >= this.state.valuemax) {
                console.log("[_onValidate] All lines reconciled – showing rainbow man");
                this.env.bus.trigger('show-rainbow-man', {
                    valuenow:         this.state.valuenow,
                    valuemax:         this.state.valuemax,
                    context:          this.state.context,
                    bank_statement_id: this.state.bank_statement_id,
                });
            }
        } catch (err) {
            console.error("[_onValidate] Validation error:", err);
            this.notification.add(_t("Reconciliation failed. Please try again."), {
                type: 'danger',
            });
        } finally {
            this.isValidating = false;
        }
    }

    // ── Proposition event handlers ────────────────────────────────────────────

    async _onRemoveProposition({ detail }) {
        const { handle, moveLineId } = detail;
        await this.model.removeProposition(handle, moveLineId);
        this.env.bus.trigger('update-line', { handle });
    }

    async _onAddProposition({ detail }) {
        const { handle, moveLineId } = detail;
        await this.model.addProposition(handle, moveLineId);
        this.env.bus.trigger('update-line', { handle });
    }

    async _onApplyModel({ detail }) {
        const { handle, modelId } = detail;
        await this.model.applyReconciliationModel(handle, modelId);
        this.env.bus.trigger('update-line', { handle });
    }

    // ── Rainbow Man ───────────────────────────────────────────────────────────

    showRainbowMan({ detail }) {
        console.log("[showRainbowMan] Event detail:", detail);

        try {
            const dt = Date.now() - this.time;
            const dur = DateTime.fromMillis(dt).toUTC();
            const duration = [
                String(dur.hour).padStart(2, '0'),
                String(dur.minute).padStart(2, '0'),
                String(dur.second).padStart(2, '0'),
            ].join(':');

            const number = detail.valuenow || 0;
            const timePerTransaction = number > 0
                ? Math.round(dt / 1000 / number)
                : 0;

            this.dialog.add(DoneMessage, {
                duration,
                number,
                timePerTransaction,
                context:             detail.context   || {},
                bank_statement_id:   detail.bank_statement_id || null,
                onCloseBankStatement: this.onCloseBankStatement.bind(this),
                onGoToBankStatement:  this.onGoToBankStatement.bind(this),
            });

            if (session.show_effect !== false) {
                this.effect.add({
                    type: 'rainbow_man',
                    message: '',
                    fadeout: 'no',
                });
            }
        } catch (err) {
            console.error("[showRainbowMan] Error:", err);
            this.notification.add(
                _t("Reconciliation complete!"),
                { type: 'success' },
            );
        }
    }

    // ── Navigation ────────────────────────────────────────────────────────────

    async onCloseBankStatement() {
        const stmtId = this.state.bank_statement_id?.id;
        if (!stmtId) return;
        await this.orm.call(
            'account.bank.statement',
            'button_post',
            [[stmtId]],
        );
        this.actionService.doAction({ type: 'ir.actions.act_window_close' });
    }

    async onGoToBankStatement(event) {
        const journalId = event?.target?.dataset?.journalId;
        if (!journalId) return;
        const action = await this.orm.call(
            'account.journal',
            'action_open_reconcile',
            [[Number(journalId)]],
        );
        this.actionService.doAction(action);
    }

    // ── Data loading ──────────────────────────────────────────────────────────

    async _loadStatementLines() {
        // Subclasses / concrete implementations populate this.model, state.valuemax, etc.
        console.log("[StatementAction] _loadStatementLines – override in subclass");
    }
}
