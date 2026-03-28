# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import api, models

_logger = logging.getLogger(__name__)


class DynamicAccountsReport(models.TransientModel):
    """
    Fix date-filtering bugs in the dynamic_accounts_report module:
      1. Prevent ValueError when start_date / end_date are empty strings.
      2. Ensure _get_entries() respects date filters (pass filtered move lines
         instead of querying the entire account).
    """
    _inherit = 'dynamic.balance.sheet.report'

    @api.model
    def get_filter_values(self, date_range, **kwargs):
        """Guard against empty date strings before parsing."""
        _logger.info("[FINANCIAL-REPORT] get_filter_values called with: %s", date_range)

        if isinstance(date_range, dict):
            for key in ('start_date', 'end_date'):
                if key in date_range and not date_range[key]:
                    _logger.warning(
                        "[FINANCIAL-REPORT] Empty %s in date_range, removing key", key
                    )
                    date_range.pop(key)

        return super().get_filter_values(date_range, **kwargs)


class ProfitAndLossReport(models.TransientModel):
    _inherit = 'profit.loss.report'

    def _get_entries(self, account_ids, account_type, account_move_lines):
        """
        Override to correctly apply date filtering.

        The upstream method calculates totals across all move lines for an
        account without respecting the already-filtered *account_move_lines*
        queryset. This override uses only the supplied recordset.
        """
        entries = []
        total = 0.0

        for account in account_ids:
            filtered_lines = account_move_lines.filtered(
                lambda line: line.account_id == account
            )

            # Opening balance when a start date filter is active
            opening_balance = 0.0
            if self.date_from:
                domain = [
                    ('account_id', '=', account.id),
                    ('date', '<', self.date_from),
                    ('parent_state', '=', 'posted'),
                ]
                if self.journal_ids:
                    domain.append(('journal_id', 'in', self.journal_ids.ids))
                opening_lines = self.env['account.move.line'].search(domain)
                opening_debit = sum(opening_lines.mapped('debit'))
                opening_credit = sum(opening_lines.mapped('credit'))
                if account_type in (
                    'income', 'income_other',
                    'liability_payable', 'liability_current',
                    'liability_non_current', 'equity', 'equity_unaffected',
                ):
                    opening_balance = -(opening_debit - opening_credit)
                else:
                    opening_balance = opening_debit - opening_credit

            # Period amount
            period_amount = 0.0
            if filtered_lines:
                debit = sum(filtered_lines.mapped('debit'))
                credit = sum(filtered_lines.mapped('credit'))
                if account_type in (
                    'income', 'income_other',
                    'liability_payable', 'liability_current',
                    'liability_non_current', 'equity', 'equity_unaffected',
                ):
                    period_amount = -(debit - credit)
                else:
                    period_amount = debit - credit

            amount = opening_balance + period_amount
            entries.append({
                'name': "{} - {}".format(account.code, account.name),
                'amount': "{:,.2f}".format(amount),
            })
            total += amount

        return entries, "{:,.2f}".format(total)
