from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    paas_user_ids = fields.One2many('paas.user', 'partner_id', string='PaaS Users')
    paas_user_count = fields.Integer(compute='_compute_paas_user_count', string='PaaS User Count')

    @api.depends('paas_user_ids')
    def _compute_paas_user_count(self):
        for partner in self:
            partner.paas_user_count = len(partner.paas_user_ids)

    def action_view_paas_user(self):
        self.ensure_one()
        action = {
            'name': 'PaaS Users',
            'type': 'ir.actions.act_window',
            'res_model': 'paas.user',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
        if len(self.paas_user_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.paas_user_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
            })
        return action
