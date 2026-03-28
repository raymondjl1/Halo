from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        
        if self.move_type == 'out_invoice' and self.payment_state == 'paid':
            for line in self.invoice_line_ids:
                if line.product_id.halo_subscription:
                    self.env['halo.cus.subscriptions'].halo_build_key(
                        self.partner_id.id,
                        self.invoice_origin and self.env['sale.order'].search([('name', '=', self.invoice_origin)]).id,
                        int(line.product_id.expires_in_days),
                        line.product_id.group_type_id.id
                    )
        
        return res