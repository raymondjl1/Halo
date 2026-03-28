# -*- coding: utf-8 -*-
import json
import logging
from odoo import api, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountReconciliationWidget(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    # =========================================================================
    # process_move_lines  –  Entry point called from JS validate()
    # =========================================================================

    @api.model
    def process_move_lines(self, data):
        """
        Validate a batch of reconciliations in a single call.

        Each datum in *data* is a dict with:
            type            : 'statement_line' | 'partner' | 'account'
            id              : id of the affected record
            mv_line_ids     : ids of existing account.move.line to reconcile
            new_mv_line_dicts : list of dicts for account.move.line.create()
        """
        _logger.info("[PROCESS-MOVE-LINES] Starting with data: %s", data)

        Partner = self.env['res.partner']
        AccountMoveLine = self.env['account.move.line']
        BankStatementLine = self.env['account.bank.statement.line']

        for datum in data:
            _logger.debug("[PROCESS-MOVE-LINES] Processing datum: %s", datum)

            if datum.get('type') != 'statement_line' or not datum.get('id'):
                # Legacy partner / account reconciliation path
                if datum.get('type') == 'partner' and datum.get('id'):
                    Partner.browse(datum['id']).mark_as_reconciled()
                continue

            statement_line_id = datum['id']
            _logger.info("[PROCESS-MOVE-LINES] Statement line ID: %s", statement_line_id)

            # -- Lock the row to prevent concurrent processing ----------------
            self.env.cr.execute(
                "SELECT id, is_reconciled FROM account_bank_statement_line "
                "WHERE id = %s FOR UPDATE NOWAIT",
                (statement_line_id,)
            )
            row = self.env.cr.fetchone()
            if not row:
                _logger.error("[PROCESS-MOVE-LINES] Statement line %s not found", statement_line_id)
                continue
            if row[1]:
                _logger.warning(
                    "[PROCESS-MOVE-LINES] Statement line %s already reconciled, skipping",
                    statement_line_id,
                )
                continue

            statement_line = BankStatementLine.browse(statement_line_id)

            mv_line_ids = datum.get('mv_line_ids', [])
            new_mv_line_dicts = datum.get('new_mv_line_dicts', [])

            try:
                if mv_line_ids:
                    # Existing move lines
                    move_lines = AccountMoveLine.browse(mv_line_ids)
                    self._reconcile_lines(statement_line, move_lines, False)
                elif new_mv_line_dicts:
                    # Manually created propositions
                    self._process_new_move_lines(statement_line, new_mv_line_dicts)
                else:
                    _logger.warning(
                        "[PROCESS-MOVE-LINES] No move lines for statement line %s", statement_line_id
                    )
            except Exception as exc:
                _logger.error(
                    "[PROCESS-MOVE-LINES] Reconciliation failed for line %s: %s",
                    statement_line_id, exc,
                )
                raise

        _logger.info("[PROCESS-MOVE-LINES] Finished processing move lines.")
        return True

    # =========================================================================
    # _reconcile_lines  –  Core reconciliation for existing or new moves
    # =========================================================================

    @api.model
    def _reconcile_lines(self, statement_line, move_lines, new_line_account_id):
        """
        Reconcile *statement_line* against *move_lines*.

        If *new_line_account_id* is provided, the suspense line on the
        statement move is updated to that account instead of matching against
        existing move lines.
        """
        _logger.info(
            "[RECONCILE-LINES] Statement line %s | move_lines %s | new_account %s",
            statement_line.id, move_lines.ids, new_line_account_id,
        )

        # Identify the suspense (counterpart) lines on the statement move
        statement_counterpart_lines = statement_line.move_id.line_ids.filtered(
            lambda l: l.account_id.id != statement_line.journal_id.payment_credit_account_id.id
            and l.account_id.id != statement_line.journal_id.payment_debit_account_id.id
        )
        _logger.info(
            "[RECONCILE-LINES] Counterpart lines: %s", statement_counterpart_lines.ids
        )

        partial_reconciles = self.env['account.partial.reconcile']

        # ------------------------------------------------------------------
        # CASE A: New account  –  just swap the suspense account
        # ------------------------------------------------------------------
        if new_line_account_id and not move_lines:
            _logger.info(
                "[RECONCILE-LINES] New account path: updating suspense line to account %s",
                new_line_account_id,
            )
            suspense_line = statement_counterpart_lines[:1]
            if suspense_line:
                # Must be in draft to edit
                statement_line.move_id.button_draft()
                suspense_line.write({'account_id': new_line_account_id})
                statement_line.move_id.action_post()

            self._mark_statement_line_reconciled(statement_line, 0)
            return partial_reconciles

        # ------------------------------------------------------------------
        # CASE B: Existing move lines  –  full reconciliation flow
        # ------------------------------------------------------------------
        debit_line = None
        credit_line = None

        for stmt_line in statement_counterpart_lines:
            for mv_line in move_lines:
                if stmt_line.debit > 0 and mv_line.credit > 0:
                    debit_line = stmt_line
                    credit_line = mv_line
                    break
                elif stmt_line.credit > 0 and mv_line.debit > 0:
                    debit_line = mv_line
                    credit_line = stmt_line
                    break

        if debit_line and credit_line:
            _logger.info(
                "[RECONCILE-LINES] Reconciling debit %s with credit %s",
                debit_line.id, credit_line.id,
            )
            try:
                partial_reconcile = self.env['account.partial.reconcile'].create({
                    'debit_move_id': debit_line.id,
                    'credit_move_id': credit_line.id,
                    'amount': min(
                        abs(debit_line.amount_residual),
                        abs(credit_line.amount_residual),
                    ),
                })
                partial_reconciles |= partial_reconcile
            except Exception as exc:
                _logger.error("[RECONCILE-LINES] Partial reconcile failed: %s", exc)
                raise

        # Determine the offsetting account from the matched move lines
        offsetting_account_id = None
        for mv_line in move_lines:
            if mv_line.account_id.account_type in (
                'liability_payable', 'asset_receivable',
                'expense', 'expense_depreciation', 'expense_direct_cost',
                'income', 'income_other',
            ):
                offsetting_account_id = mv_line.account_id.id
                break
        if not offsetting_account_id and move_lines:
            offsetting_account_id = move_lines[0].account_id.id

        # Update the suspense line with the offsetting account
        if offsetting_account_id:
            suspense_line = statement_counterpart_lines.filtered(
                lambda l: l.account_id == statement_line.journal_id.suspense_account_id
            )[:1]
            if suspense_line:
                statement_line.move_id.button_draft()
                suspense_line.write({'account_id': offsetting_account_id})
                statement_line.move_id.action_post()

        # Update partner if available
        partner_id = next(
            (ml.partner_id.id for ml in move_lines if ml.partner_id), None
        )
        if partner_id:
            self.env.cr.execute(
                "UPDATE account_bank_statement_line SET partner_id = %s WHERE id = %s",
                (partner_id, statement_line.id),
            )

        # Calculate residual
        reconciled_amount = sum(
            abs(l.debit - l.credit)
            for l in statement_counterpart_lines
            if l.reconciled or l in (debit_line, credit_line)
        )
        original_amount = abs(statement_line.amount)
        new_residual = original_amount - reconciled_amount
        is_fully_reconciled = statement_line.currency_id.is_zero(new_residual)

        self._mark_statement_line_reconciled(statement_line, new_residual, is_fully_reconciled)
        return partial_reconciles

    # =========================================================================
    # _process_new_move_lines
    # =========================================================================

    @api.model
    def _process_new_move_lines(self, statement_line, new_mv_line_dicts):
        """
        Handle manually created propositions (new account lines).

        Expects exactly one dict in *new_mv_line_dicts* with at least an
        ``account_id`` key.
        """
        _logger.info(
            "[PROCESS-NEW-MOVE-LINES] Processing new move lines for statement line %s",
            statement_line.id,
        )
        AccountMoveLine = self.env['account.move.line']

        if len(new_mv_line_dicts) != 1:
            raise UserError(
                _("Expected exactly one entry in new_mv_line_dicts, got %s")
                % len(new_mv_line_dicts)
            )
        line_dict = new_mv_line_dicts[0]
        if not line_dict.get('account_id'):
            raise UserError(
                _("Missing account_id in new move line dict: %s") % line_dict
            )

        new_account_id = line_dict['account_id']
        _logger.info(
            "[PROCESS-NEW-MOVE-LINES] Using account ID %s", new_account_id
        )

        partial_reconciles = self._reconcile_lines(
            statement_line, AccountMoveLine.browse(), new_account_id
        )

        # Apply optional extra fields (name, analytic distribution)
        if partial_reconciles and line_dict.get('name'):
            updated_line = statement_line.move_id.line_ids.filtered(
                lambda l: l.account_id.id == new_account_id
            )
            if updated_line:
                write_vals = {'name': line_dict['name']}
                if 'analytic_distribution' in line_dict:
                    write_vals['analytic_distribution'] = line_dict['analytic_distribution']
                updated_line.write(write_vals)

        _logger.info(
            "[PROCESS-NEW-MOVE-LINES] Completed for statement line %s", statement_line.id
        )
        return partial_reconciles

    # =========================================================================
    # unreconcile_statement_line
    # =========================================================================

    @api.model
    def unreconcile_statement_line(self, statement_line_id):
        """
        Reverse reconciliation for a bank statement line.

        1. Identifies all move lines linked to the statement line.
        2. Removes partial and full reconcile records.
        3. Deletes any account moves created specifically for this
           reconciliation (manual entries tagged with the statement line).
        4. Resets the statement line fields to unreconciled state.
        """
        _logger.info("[UNRECONCILE] Starting for statement line: %s", statement_line_id)

        BankStatementLine = self.env['account.bank.statement.line']
        AccountMoveLine = self.env['account.move.line']
        AccountMove = self.env['account.move']

        statement_line = BankStatementLine.browse(statement_line_id)
        if not statement_line.exists():
            _logger.error("[UNRECONCILE] Statement line %s not found", statement_line_id)
            return False

        # Linked move lines
        linked_move_lines = AccountMoveLine.search([
            ('statement_line_id', '=', statement_line_id)
        ])
        _logger.info(
            "[UNRECONCILE] Found %d linked move lines", len(linked_move_lines)
        )

        full_reconcile_ids = linked_move_lines.mapped('full_reconcile_id')
        _logger.info(
            "[UNRECONCILE] Full reconcile IDs: %s",
            full_reconcile_ids.ids if full_reconcile_ids else 'None',
        )

        try:
            affected_moves = linked_move_lines.mapped('move_id')

            # Identify manually created reconciliation moves
            manual_moves = AccountMove.browse()
            for move in affected_moves:
                is_manual = (
                    (move.ref and 'Reconciliation for' in (move.ref or ''))
                    or all(
                        ml.statement_line_id.id == statement_line_id
                        for ml in move.line_ids
                    )
                )
                if is_manual:
                    manual_moves |= move

            _logger.info(
                "[UNRECONCILE] Manual moves to delete: %s", manual_moves.ids
            )

            # Remove partial reconciles
            partial_reconciles = linked_move_lines.mapped('matched_debit_ids') | \
                                  linked_move_lines.mapped('matched_credit_ids')
            if partial_reconciles:
                partial_reconciles.unlink()

            # Remove full reconciles
            if full_reconcile_ids:
                full_reconcile_ids.sudo().unlink()

            # Restore suspense account on the statement move
            statement_move_lines = statement_line.move_id.line_ids
            suspense_acct = statement_line.journal_id.suspense_account_id
            bank_acct = (
                statement_line.journal_id.payment_credit_account_id
                or statement_line.journal_id.payment_debit_account_id
            )
            counterpart_line = statement_move_lines.filtered(
                lambda l: l.account_id != bank_acct
            )[:1]
            if counterpart_line and suspense_acct and counterpart_line.account_id != suspense_acct:
                statement_line.move_id.button_draft()
                counterpart_line.write({'account_id': suspense_acct.id})
                statement_line.move_id.action_post()

            # Delete manual moves
            if manual_moves:
                try:
                    manual_moves.button_draft()
                    manual_moves.line_ids.write({'statement_line_id': False})
                    manual_moves.unlink()
                    _logger.info("[UNRECONCILE] Deleted manual moves")
                except Exception as exc:
                    _logger.warning(
                        "[UNRECONCILE] ORM delete failed, trying SQL: %s", exc
                    )
                    self.env.cr.execute(
                        "DELETE FROM account_move WHERE id = ANY(%s)",
                        (manual_moves.ids,)
                    )

            # Reset statement line
            self.env.cr.execute(
                "SELECT amount FROM account_bank_statement_line WHERE id = %s",
                (statement_line_id,)
            )
            row = self.env.cr.fetchone()
            original_amount = row[0] if row else 0

            self.env.cr.execute(
                """
                UPDATE account_bank_statement_line
                SET is_reconciled   = FALSE,
                    bank_state      = 'valid',
                    amount_residual = %s,
                    lines_widget_json = NULL
                WHERE id = %s
                """,
                (original_amount, statement_line_id),
            )

            # Reset parent statement
            if statement_line.statement_id:
                self.env.cr.execute(
                    "UPDATE account_bank_statement SET all_lines_reconciled = FALSE WHERE id = %s",
                    (statement_line.statement_id.id,)
                )

            self.env.cr.commit()
            _logger.info(
                "[UNRECONCILE] Successfully unreconciled statement line %s", statement_line_id
            )
            return True

        except Exception as exc:
            _logger.error(
                "[UNRECONCILE] Failed for statement line %s: %s", statement_line_id, exc
            )
            raise

    # =========================================================================
    # Helpers
    # =========================================================================

    def _mark_statement_line_reconciled(self, statement_line, residual, fully=True):
        """Write reconciliation status back to the statement line (SQL, bypass ORM)."""
        widget_json = {
            'content': [],
            'outstanding_credits_debits_widget': False,
        }
        state_val = 'reconciled' if fully else 'partially_reconciled'
        self.env.cr.execute(
            """
            UPDATE account_bank_statement_line
            SET is_reconciled     = %s,
                bank_state        = %s,
                amount_residual   = %s,
                lines_widget_json = %s
            WHERE id = %s
            """,
            (fully, state_val, residual, json.dumps(widget_json), statement_line.id),
        )
        _logger.info(
            "[RECONCILE] Statement line %s marked %s (residual=%s)",
            statement_line.id, state_val, residual,
        )
        # Propagate to parent statement
        if statement_line.statement_id:
            statement_line.statement_id.force_recompute()
