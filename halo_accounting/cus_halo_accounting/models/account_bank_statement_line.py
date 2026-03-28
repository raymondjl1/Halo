# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    is_reconciled = fields.Boolean(
        string='Is Reconciled',
        default=False,
        copy=False,
    )

    bank_state = fields.Selection(
        selection=[
            ('valid', 'Valid'),
            ('invalid', 'Invalid'),
            ('reconciled', 'Reconciled'),
        ],
        string='Bank State',
        default='invalid',
        copy=False,
    )

    amount_residual = fields.Monetary(
        string='Residual Amount',
        currency_field='currency_id',
        copy=False,
    )

    lines_widget_json = fields.Text(
        string='Lines Widget JSON',
        copy=False,
    )

    # -------------------------------------------------------------------------
    # Compute / Onchange
    # -------------------------------------------------------------------------

    @api.onchange('amount')
    def _onchange_amount(self):
        if self.amount and not self.is_reconciled:
            self.amount_residual = self.amount
            self.bank_state = 'valid'
        elif not self.amount:
            self.bank_state = 'invalid'

    # -------------------------------------------------------------------------
    # Button Actions
    # -------------------------------------------------------------------------

    def button_validation(self):
        """Validate the statement line (set as reconciled)."""
        for line in self:
            _logger.info("[STMT-LINE] Validating statement line %s", line.id)
            line.write({
                'is_reconciled': True,
                'bank_state': 'reconciled',
                'amount_residual': 0,
            })
            # Trigger recompute on parent statement
            if line.statement_id:
                line.statement_id.force_recompute()
        return True

    def button_reset(self):
        """Unreconcile / reset the statement line."""
        for line in self:
            _logger.info("[STMT-LINE] Resetting statement line %s", line.id)
            # Delegate to the reconciliation widget's unreconcile method
            self.env['account.reconciliation.widget'].unreconcile_statement_line(line.id)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_to_check(self):
        """Flag the line as needing review."""
        self.write({'to_check': True})

    def button_set_as_checked(self):
        """Clear the to-check flag."""
        self.write({'to_check': False})

    # -------------------------------------------------------------------------
    # Overrides
    # -------------------------------------------------------------------------

    def read(self, fields=None, load='_classic_read'):
        result = super().read(fields=fields, load=load)
        check_fields = {'is_reconciled', 'bank_state', 'amount_residual'}
        if not fields or check_fields.intersection(fields):
            self.invalidate_recordset(list(check_fields))
        return result
