from odoo import models, fields, api

class PaasPlan(models.Model):
    _name = 'paas.plan'
    _description = 'PaaS Plan'

    name = fields.Char(string='Name', required=True)
    limit_instances = fields.Integer(string='Instance Limit', default=0)
    limit_storage_gb = fields.Float(string='Storage Limit (GB)', default=0.0)
    limit_staging_environments = fields.Integer(string='Staging Env Limit', default=0)
    limit_workers = fields.Integer(string='Worker Limit', default=0)
    product_id = fields.Many2one('product.product', string='Associated Product', ondelete='restrict', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('product_id'):
                product = self.env['product.product'].create({
                    'name': vals.get('name'),
                    'type': 'service',
                    'sale_ok': True,
                    'purchase_ok': False,
                })
                vals['product_id'] = product.id
        return super(PaasPlan, self).create(vals_list)

    def write(self, vals):
        res = super(PaasPlan, self).write(vals)
        if 'name' in vals:
            for rec in self:
                if rec.product_id:
                    rec.product_id.name = vals['name']
        return res
