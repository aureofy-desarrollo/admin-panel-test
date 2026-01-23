from odoo import models, fields, api, _

class PaasUser(models.Model):
    _name = 'paas.user'
    _description = 'PaaS User'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    github_id = fields.Char(string='GitHub ID')
    username = fields.Char(string='Username')
    
    plan_id = fields.Many2one('paas.plan', string='Plan')
    instance_ids = fields.One2many('paas.instance', 'user_id', string='Instances')
    
    last_login_at = fields.Datetime(string='Last Login')
    
    # Owned instances is handled by the reverse relation instance_ids

    @api.model_create_multi
    def create(self, vals_list):
        # Ensure email from partner is reachable if needed, 
        # but _inherits handles the creation of the partner given the partner fields.
        return super(PaasUser, self).create(vals_list)

    def action_create_invoice(self):
        self.ensure_one()
        return {
            'name': _('New Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'context': {
                'default_move_type': 'out_invoice',
                'default_partner_id': self.partner_id.id,
            },
            'target': 'current',
        }
