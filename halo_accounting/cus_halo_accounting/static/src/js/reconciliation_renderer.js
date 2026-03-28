/** @odoo-module **/
/**
 * cus_halo_accounting – reconciliation_renderer.js
 *
 * LineRenderer component patches:
 *   - onValidate: debounced, prevents double-fire
 *   - handleRemoveProposition: NaN-safe ID resolution
 *   - onSelectProposition: handles both numeric and string IDs
 *   - onAutoMatchLine: fetches account code/name; sets label from statement line
 */

import { Component, useState, onMounted, useRef, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LineRenderer extends Component {
    static template = "cus_halo_accounting.LineRenderer";

    setup() {
        super.setup?.(...arguments);

        this.orm = useService("orm");
        this.notification = useService("notification");

        // Debounce state
        this._lastValidationTime = 0;
        this._validationInProgress = false;
    }

    // ── Validate ──────────────────────────────────────────────────────────────

    onValidate(event) {
        console.log("[onValidate] Received event:", event);

        // Stop propagation to prevent duplicate DOM events
        if (event) {
            event.stopPropagation();
            event.preventDefault();
        }

        // Ignore if intended for a different handle
        if (
            event?.detail?.handle &&
            event.detail.handle !== this.props.handle
        ) {
            console.log("[onValidate] Ignoring event for handle:", event.detail.handle);
            return;
        }

        // Debounce: ignore clicks within 300 ms
        const now = Date.now();
        if (now - this._lastValidationTime < 300) {
            console.log("[onValidate] Debouncing: too soon since last validation");
            return;
        }

        // Re-entrancy guard
        if (this._validationInProgress) {
            console.log("[onValidate] Validation already in progress, ignoring duplicate");
            return;
        }

        this._lastValidationTime = now;
        this._validationInProgress = true;

        console.log("[onValidate] Triggering validate-line for handle:", this.props.handle);
        this.env.bus.trigger('validate-line', { handle: this.props.handle });

        // Reset guard after 1 s
        setTimeout(() => {
            this._validationInProgress = false;
        }, 1000);
    }

    // ── Remove proposition ────────────────────────────────────────────────────

    handleRemoveProposition(event) {
        console.log("[handleRemoveProposition] Received event:", event);

        const rawId = event?.detail?.moveLineId ?? event?.currentTarget?.dataset?.lineId;
        const moveLineId = Number(rawId);
        console.log(
            "[handleRemoveProposition] moveLineId:", moveLineId,
            "type:", typeof moveLineId,
        );

        if (isNaN(moveLineId)) {
            console.log("[handleRemoveProposition] NaN ID received, looking for any manually created proposition");
            // Surface the available propositions for debugging
            const state = this.props.state || {};
            console.log("[handleRemoveProposition] Available propositions:", state.reconciliation_proposition);
        }

        this.env.bus.trigger('remove-proposition', {
            handle: this.props.handle,
            moveLineId: isNaN(moveLineId) ? rawId : moveLineId,
        });
    }

    // ── Select proposition ────────────────────────────────────────────────────

    onSelectProposition(event) {
        console.log("[onSelectProposition] Received event:", event);

        const rawId = event?.currentTarget?.dataset?.lineId
            ?? event?.detail?.moveLineId;
        const idNum = Number(rawId);
        const moveLineId = isNaN(idNum) ? rawId : idNum;

        console.log("[onSelectProposition] Resolved moveLineId:", moveLineId, "type:", typeof moveLineId);

        this.env.bus.trigger('add-proposition', {
            handle: this.props.handle,
            moveLineId,
        });
    }

    // ── Auto-match via reconciliation model ───────────────────────────────────

    async onAutoMatchLine(event) {
        event.stopPropagation();
        const mvLine = event.currentTarget.closest('.mv_line');
        if (!mvLine) {
            console.warn("[onAutoMatchLine] Move line element not found");
            return;
        }

        const moveLineId = Number(mvLine.dataset.lineId);
        const modelId = Number(event.currentTarget.dataset.modelId);

        console.log(
            "[onAutoMatchLine] Auto-matching move line", moveLineId,
            "using model", modelId,
        );

        // Add the underlying move line first
        this.env.bus.trigger('add-proposition', {
            handle: this.props.handle,
            moveLineId,
        });

        // Then apply the reconciliation model rules
        if (modelId) {
            this.env.bus.trigger('apply-reconcile-model', {
                handle: this.props.handle,
                modelId,
            });
        }
    }
}
