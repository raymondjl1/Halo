from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    halo_subscription = fields.Boolean(string='Is Halo Subscription')
    expires_in_days = fields.Selection([
        ('30', '30 Days'),
        ('60', '60 Days'),
        ('90', '90 Days'),
        ('120', '120 Days'),
        ('150', '150 Days'),
        ('180', '180 Days'),
        ('365', '365 Days'),
    ], string='Subscription Duration')
    group_type_id = fields.Many2one('halo.cus.application.user.groups', string='User Group Type')