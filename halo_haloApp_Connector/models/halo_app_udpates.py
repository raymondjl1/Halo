from odoo import models, fields, api
import base64

class HaloAppUpdates(models.Model):
    _name = 'halo.cus.app.updates'
    _description = 'Halo App Updates'

    name = fields.Char(string='Name', required=True)
    version = fields.Char(string='Version', required=True)
    update_file = fields.Binary(string='Update File', attachment=True)
    date_available = fields.Date(string='Date Available')
    file_name = fields.Char(string='File Name')
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', readonly=True)
    download_url = fields.Char(string='Download URL', compute='_compute_download_url', readonly=True)

    @api.depends('attachment_id')
    def _compute_download_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.attachment_id:
                record.download_url = f"{base_url}/app_updates/download/{record.id}"
            else:
                record.download_url = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.update_file:
                record._create_attachment()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'update_file' in vals:
            self._create_attachment()
        return res

    def _create_attachment(self):
        """Create an attachment for the update file"""
        self.ensure_one()
        if self.attachment_id:
            self.attachment_id.unlink()
            
        if not self.update_file:
            return

        attachment = self.env['ir.attachment'].create({
            'name': self.file_name,
            'datas': self.update_file,
            'res_model': self._name,
            'res_id': self.id,
        })
        self.attachment_id = attachment