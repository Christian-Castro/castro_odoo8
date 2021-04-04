from openerp import models, fields, api, _


class AccountJournalInherit(models.Model):
    _inherit = "account.journal"

    cheques_postfechados = fields.Boolean(
        string='Cheques Postfechados',
    )
    