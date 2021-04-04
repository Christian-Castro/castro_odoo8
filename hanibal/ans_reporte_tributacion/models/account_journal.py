from openerp import models, fields, api, _


class AccountJournalInherit(models.Model):
    _inherit = "account.journal"

    reembolso = fields.Boolean(
        string='Reembolso',
    )
    