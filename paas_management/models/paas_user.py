from odoo import models, fields, api

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

    @api.model
    def create(self, vals):
        # Ensure email from partner is reachable if needed, 
        # but _inherits handles the creation of the partner given the partner fields.
        return super(PaasUser, self).create(vals)
