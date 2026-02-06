import logging

_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PaasPlan(models.Model):
    _name = 'paas.plan'
    _description = 'PaaS Plan'

    paas_id = fields.Char(string='Backend ID', readonly=True, copy=False)
    name = fields.Char(string='Name', required=True)
    slug = fields.Char(string='Slug', required=True)
    price = fields.Float(string='Price', default=0.0)
    currency = fields.Selection([
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('ARS', 'ARS'),
    ], string='Currency', default='USD')
    
    limit_instances = fields.Integer(string='Instance Limit', default=0)
    limit_storage_gb = fields.Float(string='Storage Limit (GB)', default=0.0)
    limit_staging_environments = fields.Integer(string='Staging Env Limit', default=0)
    limit_workers = fields.Integer(string='Worker Limit', default=0)
    product_id = fields.Many2one('product.product', string='Associated Product', ondelete='restrict', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('slug') and vals.get('name'):
                vals['slug'] = vals.get('name').lower().replace(' ', '-')
                
            if not vals.get('product_id'):
                product = self.env['product.product'].create({
                    'name': vals.get('name'),
                    'type': 'service',
                    'list_price': vals.get('price', 0.0),
                    'sale_ok': True,
                    'purchase_ok': False,
                })
                vals['product_id'] = product.id
            
            # API Call - Only if config exists
            config = self.env['paas.config'].get_config(silent=True)
            if config:
                api_data = {
                    "name": vals.get('name'),
                    "slug": vals.get('slug'),
                    "price": vals.get('price', 0.0),
                    "currency": vals.get('currency', 'USD'),
                    "limits": {
                        "instances": vals.get('limit_instances', 0),
                        "storageGB": vals.get('limit_storage_gb', 0.0),
                        "workers": vals.get('limit_workers', 0)
                    }
                }
                try:
                    response = self.env['paas.client']._make_request('POST', '/api/plans', data=api_data)
                    if response and isinstance(response, dict) and response.get('_id'):
                        vals['paas_id'] = response.get('_id')
                    elif response and isinstance(response, dict) and response.get('id'):
                         vals['paas_id'] = response.get('id')
                except Exception as e:
                    _logger.warning("Failed to sync plan %s with backend: %s", vals.get('name'), str(e))
            else:
                _logger.info("Skipping API sync for plan %s: No active configuration found.", vals.get('name'))

        return super(PaasPlan, self).create(vals_list)

    def write(self, vals):
        res = super(PaasPlan, self).write(vals)
        
        # Prepare API update
        api_fields = ['name', 'slug', 'price', 'currency', 'limit_instances', 'limit_storage_gb', 'limit_workers']
        if any(f in vals for f in api_fields):
            for rec in self:
                if not rec.paas_id:
                    continue
                
                api_data = {
                    "name": rec.name,
                    "slug": rec.slug,
                    "price": rec.price,
                    "currency": rec.currency,
                    "limits": {
                        "instances": rec.limit_instances,
                        "storageGB": rec.limit_storage_gb,
                        "workers": rec.limit_workers
                    }
                }
                try:
                    config = self.env['paas.config'].get_config(silent=True)
                    if config:
                        self.env['paas.client']._make_request('PUT', f'/api/plans/{rec.paas_id}', data=api_data)
                    else:
                        _logger.info("Skipping API update for plan %s: No active configuration found.", rec.name)
                except Exception as e:
                    _logger.error("Error updating plan %s in backend: %s", rec.name, str(e))
                
                if 'name' in vals and rec.product_id:
                    rec.product_id.name = vals['name']
                if 'price' in vals and rec.product_id:
                    rec.product_id.list_price = vals['price']
        
        return res

    def unlink(self):
        config = self.env['paas.config'].get_config(silent=True)
        for rec in self:
            if rec.paas_id and config:
                try:
                    self.env['paas.client']._make_request('DELETE', f'/api/plans/{rec.paas_id}')
                except Exception as e:
                    _logger.error("Error deleting plan %s from backend: %s", rec.name, str(e))
        return super(PaasPlan, self).unlink()
