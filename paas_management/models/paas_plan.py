from odoo import models, fields

class PaasPlan(models.Model):
    _name = 'paas.plan'
    _description = 'PaaS Plan'

    name = fields.Char(string='Name', required=True)
    limit_instances = fields.Integer(string='Instance Limit', default=0)
    limit_storage_gb = fields.Float(string='Storage Limit (GB)', default=0.0)
    limit_staging_environments = fields.Integer(string='Staging Env Limit', default=0)
    limit_workers = fields.Integer(string='Worker Limit', default=0)
