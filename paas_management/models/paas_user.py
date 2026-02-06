from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PaasUser(models.Model):
    _name = 'paas.user'
    _description = 'PaaS User'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    paas_id = fields.Char(string='Backend ID', readonly=True, copy=False)
    github_id = fields.Char(string='GitHub ID')
    username = fields.Char(string='Username')
    
    plan_id = fields.Many2one('paas.plan', string='Backend Plan')
    instance_ids = fields.One2many('paas.instance', 'user_id', string='Instances')
    
    subscription_status = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
        ('cancelled', 'Cancelled'),
    ], string='Subscription Status', default='trial')
    
    subscription_start_date = fields.Datetime(string='Start Date')
    subscription_end_date = fields.Datetime(string='End Date')
    
    last_login_at = fields.Datetime(string='Last Login')

    @api.model_create_multi
    def create(self, vals_list):
        users = super(PaasUser, self).create(vals_list)
        for user in users:
            # API Call to create user
            api_data = {
                "email": user.email,
                "username": user.username or user.name.lower().replace(' ', '_'),
                "githubId": user.github_id or ""
            }
            try:
                response = self.env['paas.client']._make_request('POST', '/api/users', data=api_data)
                if response and isinstance(response, dict):
                    backend_id = response.get('_id') or response.get('id')
                    user.write({'paas_id': backend_id})
            except Exception as e:
                _logger.warning("Could not create user in backend: %s", str(e))
        return users

    def action_update_license(self):
        self.ensure_one()
        if not self.paas_id:
            raise UserError(_("This user is not registered in the backend."))
        if not self.plan_id:
            raise UserError(_("Please select a plan before updating the license."))
        if not self.plan_id.paas_id:
             raise UserError(_("The selected plan is not synchronized with the backend."))

        api_data = {
            "plan": {
                "id": self.plan_id.paas_id,
                "status": self.subscription_status,
                "startDate": self.subscription_start_date.isoformat() if self.subscription_start_date else None,
                "endDate": self.subscription_end_date.isoformat() if self.subscription_end_date else None
            }
        }
        
        # Odoo Datetime fields are already strings sometimes, but verify
        if self.subscription_start_date:
             api_data["plan"]["startDate"] = self.subscription_start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        if self.subscription_end_date:
             api_data["plan"]["endDate"] = self.subscription_end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        self.env['paas.client']._make_request('PUT', f'/api/users/{self.paas_id}', data=api_data)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('License Updated'),
                'message': _('The license has been successfully updated in the backend.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_create_invoice(self):
        self.ensure_one()
        # ... logic for invoice remains similar ...
        context = {
            'default_move_type': 'out_invoice',
            'default_partner_id': self.partner_id.id,
            'default_company_id': self.env.company.id,
        }
        if self.plan_id and self.plan_id.product_id:
            context['default_invoice_line_ids'] = [
                (0, 0, {
                    'product_id': self.plan_id.product_id.id,
                    'quantity': 1,
                    'price_unit': self.plan_id.price,
                })
            ]
        return {
            'name': _('New Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'context': context,
            'target': 'current',
        }

    def action_view_partner(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contact'),
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.partner_id.id,
            'target': 'current',
        }
