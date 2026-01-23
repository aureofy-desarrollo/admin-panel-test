import logging
import uuid
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PaasInstance(models.Model):
    _name = 'paas.instance'
    _description = 'PaaS Odoo Instance'

    paas_id = fields.Char(string='PaaS ID', readonly=True, copy=False)
    name = fields.Char(string='Instance Name', required=True)
    user_id = fields.Many2one('paas.user', string='User', required=True)
    state = fields.Selection([
        ('provisioning', 'Provisioning'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('error', 'Error'),
    ], string='State', default='provisioning', required=True)
    odoo_version = fields.Selection([
        ('15.0', '15.0'),
        ('16.0', '16.0'),
        ('17.0', '17.0'),
        ('18.0', '18.0'),
    ], string='Odoo Version', default='18.0', required=True)
    url = fields.Char(string='URL')
    last_sync = fields.Datetime(string='Last Sync', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Mock API call on creation"""
        for vals in vals_list:
            if not vals.get('paas_id'):
                vals['paas_id'] = str(uuid.uuid4())[:8].upper()
                _logger.info("Mock API: Created instance %s with PaaS ID %s", vals.get('name'), vals['paas_id'])
            
            if vals.get('state') == 'running' and not vals.get('url'):
                vals['url'] = f"https://{vals.get('name')}.odoo.com"

        return super(PaasInstance, self).create(vals_list)

    def write(self, vals):
        """Mock API call on update"""
        res = super(PaasInstance, self).write(vals)
        for record in self:
            _logger.info("Mock API: Updated instance %s (PaaS ID: %s)", record.name, record.paas_id)
        return res

    def unlink(self):
        """Mock API call on deletion"""
        for record in self:
            _logger.info("Mock API: Deleted instance %s (PaaS ID: %s)", record.name, record.paas_id)
        return super(PaasInstance, self).unlink()

    def action_sync_paas(self):
        """Action to simulate a manual sync from the PaaS"""
        for record in self:
            new_state = 'running' if record.state == 'provisioning' else record.state
            record.write({
                'state': new_state,
                'last_sync': fields.Datetime.now()
            })
            if new_state == 'running' and not record.url:
                record.url = f"https://{record.name}.odoo.com"
        return True
