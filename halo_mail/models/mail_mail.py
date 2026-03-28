import logging
from collections import defaultdict
from odoo import models, api

_logger = logging.getLogger(__name__)

#inherit the mail BaseModel class and override the _notify_get_reply_to method
class CustomMailMail(models.AbstractModel):
    _inherit = 'mail.mail'

    def _notify_get_reply_to(self, default=None):
        """ Returns the preferred reply-to email address when replying to a thread
        on documents. This method is a generic implementation available for
        all models as we could send an email through mail templates on models
        not inheriting from mail.thread.

        Reply-to is formatted like "MyCompany MyDocument <reply.to@domain>".
        Heuristic it the following:
         * search for specific aliases as they always have priority; it is limited
           to aliases linked to documents (like project alias for task for example);
         * use catchall address;
         * use default;

        This method can be used as a generic tools if self is a void recordset.

        Override this method on a specific model to implement model-specific
        behavior. Also consider inheriting from ``mail.thread``.
        An example would be tasks taking their reply-to alias from their project.

        :param default: default email if no alias or catchall is found;
        :return result: dictionary. Keys are record IDs and value is formatted
          like an email "Company_name Document_name <reply_to@email>"/
        """
        _records = self
        model = _records._name if _records and _records._name != 'mail.thread' else False
        res_ids = _records.ids if _records and model else []
        _res_ids = res_ids or [False]  # always have a default value located in False
        _records_sudo = _records.sudo()
        doc_names = {rec.id: rec.display_name for rec in _records_sudo} if res_ids else {}

        # group ids per company
        if res_ids:
            company_to_res_ids = defaultdict(list)
            record_ids_to_company = _records_sudo._mail_get_companies(default=self.env.company)
            for record_id, company in record_ids_to_company.items():
                company_to_res_ids[company].append(record_id)
        else:
            company_to_res_ids = {self.env.company: _res_ids}
            record_ids_to_company = {_res_id: self.env.company for _res_id in _res_ids}

        # begin with aliases (independent from company, alias_domain_id on alias wins)
        reply_to_email = {}
        if model and res_ids:
            mail_aliases = self.env['mail.alias'].sudo().search([
                ('alias_domain_id', '!=', False),
                ('alias_parent_model_id.model', '=', model),
                ('alias_parent_thread_id', 'in', res_ids),
                ('alias_name', '!=', False)
            ])
            # take only first found alias for each thread_id, to match order (1 found -> limit=1 for each res_id)
            for alias in mail_aliases:
                reply_to_email.setdefault(alias.alias_parent_thread_id, alias.alias_full_name)

        # continue with company alias
        left_ids = set(_res_ids) - set(reply_to_email)
        if left_ids:
            for company, record_ids in company_to_res_ids.items():
                # left ids: use catchall defined on company alias domain
                if company.catchall_email:
                    left_ids = set(record_ids) - set(reply_to_email)
                    if left_ids:
                        reply_to_email.update({rec_id: company.catchall_email for rec_id in left_ids})

        # compute name of reply-to ("Company Document" <alias@domain>)
        reply_to_formatted = dict.fromkeys(_res_ids, default)
        for res_id, record_reply_to in reply_to_email.items():
            reply_to_formatted[res_id] = self._notify_get_reply_to_formatted_email(
                record_reply_to, doc_names.get(res_id) or '', company=record_ids_to_company[res_id],
            )
        # _logger the result
        _logger.debug('Reply-To: %s', reply_to_formatted)
        return reply_to_formatted
