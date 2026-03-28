# -*- coding: utf-8 -*-
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountBudget(models.Model):
    """
    Fix DeprecationWarning: The model is not overriding the create method in batch.
    Odoo 18 requires create() to accept a list of vals_list for batch creation.
    """
    _inherit = 'account.budget.post'

    @api.model_create_multi
    def create(self, vals_list):
        _logger.debug("[BUDGET] Batch-creating %d budget records", len(vals_list))
        return super().create(vals_list)


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    @api.model_create_multi
    def create(self, vals_list):
        _logger.debug("[BUDGET] Batch-creating %d crossovered budget records", len(vals_list))
        return super().create(vals_list)


class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    @api.model_create_multi
    def create(self, vals_list):
        _logger.debug("[BUDGET] Batch-creating %d budget line records", len(vals_list))
        return super().create(vals_list)
