from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class PaasConfig(models.Model):
    _name = 'paas.config'
    _description = 'PaaS API Configuration'
    
    name = fields.Char(string='Name', default='Main Backend', required=True)
    base_url = fields.Char(string='Base URL', default='http://localhost:3000/', required=True)
    admin_token = fields.Char(string='Admin Token', required=True)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def get_config(self, silent=False):
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            if silent:
                return False
            raise UserError(_("No active PaaS configuration found. Please create one in Configuration."))
        return config

    def action_test_connection(self):
        self.ensure_one()
        try:
            # We use /api/plans as a simple test endpoint
            headers = {
                'Authorization': f'Bearer {self.admin_token}',
                'Accept': 'application/json'
            }
            url = f"{self.base_url.rstrip('/')}/api/plans"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful'),
                        'message': _('Successfully connected to the backend.'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("Connection failed with status code: %s. Response: %s") % (response.status_code, response.text))
        except Exception as e:
            raise UserError(_("Error connecting to backend: %s") % str(e))
