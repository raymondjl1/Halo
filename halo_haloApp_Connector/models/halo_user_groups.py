from odoo import models, fields, api

class HaloUserGroups(models.Model):
    _name = 'halo.cus.application.user.groups'
    _description = 'Halo User Groups'

    name = fields.Char(string='Group Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)