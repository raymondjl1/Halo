# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    all_lines_reconciled = fields.Boolean(
        string='All Lines Reconciled',
        compute='_compute_all_lines_reconciled',
        store=True,
    )

    reconciliation_status = fields.Selection(
        selection=[('reconciled', 'Reconciled'), ('not_reconciled', 'Not Reconciled')],
        string='Reconciliation Status',
        compute='_compute_reconciliation_status',
        store=True,
    )

    is_complete = fields.Boolean(
        string='Is Complete',
        compute='_compute_is_complete',
        store=True,
    )

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------

    @api.depends('line_ids', 'line_ids.is_reconciled')
    def _compute_all_lines_reconciled(self):
        for statement in self:
            _logger.info(
                "[BANK-STMT] Computing all_lines_reconciled for statement %s", statement.id
            )
            if not statement.line_ids:
                statement.all_lines_reconciled = True
            else:
                all_reconciled = all(line.is_reconciled for line in statement.line_ids)
                statement.all_lines_reconciled = all_reconciled
                _logger.info(
                    "[BANK-STMT] Statement %s all_lines_reconciled=%s", statement.id, all_reconciled
                )

    @api.depends('is_complete', 'all_lines_reconciled')
    def _compute_reconciliation_status(self):
        for statement in self:
            _logger.info(
                "[BANK-STMT] Computing reconciliation_status for statement %s, is_complete=%s",
                statement.id, statement.is_complete,
            )
            statement.reconciliation_status = (
                'reconciled' if statement.is_complete else 'not_reconciled'
            )

    @api.depends(
        'balance_end', 'balance_end_real',
        'line_ids.amount', 'line_ids.state', 'line_ids.is_reconciled',
    )
    def _compute_is_complete(self):
        _logger.info("[BANK-STMT] Computing is_complete for bank statements")
        for statement in self:
            if not statement.line_ids:
                statement.is_complete = False
                continue
            # All lines must be reconciled for the statement to be complete
            all_reconciled = all(line.is_reconciled for line in statement.line_ids)
            # Balances must also match
            balances_match = statement.currency_id.is_zero(
                statement.balance_end - statement.balance_end_real
            ) if statement.currency_id else (
                statement.balance_end == statement.balance_end_real
            )
            statement.is_complete = all_reconciled and balances_match
            _logger.info(
                "[BANK-STMT] Statement %s is_complete=%s (all_reconciled=%s, balances_match=%s)",
                statement.id, statement.is_complete, all_reconciled, balances_match,
            )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def force_recompute(self):
        """Force recomputation of all computed reconciliation fields."""
        for statement in self:
            statement.invalidate_recordset(
                ['all_lines_reconciled', 'reconciliation_status', 'is_complete']
            )
            statement._compute_all_lines_reconciled()
            statement._compute_is_complete()
            statement._compute_reconciliation_status()
        return True
