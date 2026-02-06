from odoo import models, fields, api, _
from dateutil import parser
import logging

_logger = logging.getLogger(__name__)

class PaasSyncWizard(models.TransientModel):
    _name = 'paas.sync.wizard'
    _description = 'PaaS Sync Wizard'

    sync_plans = fields.Boolean(string='Sync Plans', default=True)
    sync_users = fields.Boolean(string='Sync Users', default=True)

    def action_sync(self):
        client = self.env['paas.client']
        
        if self.sync_plans:
            self._sync_plans(client)
        
        if self.sync_users:
            self._sync_users(client)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Completed'),
                'message': _('Plans and Users have been synchronized.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _sync_plans(self, client):
        plans_data = client._make_request('GET', '/api/plans')
        # Handle different response formats (list or dict with data key)
        plans_list = plans_data if isinstance(plans_data, list) else plans_data.get('data', [])
        
        for plan_info in plans_list:
            paas_id = plan_info.get('_id') or plan_info.get('id')
            existing = self.env['paas.plan'].search([('paas_id', '=', paas_id)], limit=1)
            
            vals = {
                'name': plan_info.get('name'),
                'slug': plan_info.get('slug'),
                'price': plan_info.get('price', 0.0),
                'currency': plan_info.get('currency', 'USD'),
                'limit_instances': plan_info.get('limits', {}).get('instances', 0),
                'limit_storage_gb': plan_info.get('limits', {}).get('storageGB', 0.0),
                'limit_workers': plan_info.get('limits', {}).get('workers', 0),
            }
            
            if existing:
                existing.with_context(skip_api=True).write(vals)
            else:
                vals['paas_id'] = paas_id
                self.env['paas.plan'].with_context(skip_api=True).create(vals)

    def _sync_users(self, client):
        users_data = client._make_request('GET', '/api/users')
        users_list = users_data if isinstance(users_data, list) else users_data.get('data', [])
        
        for user_info in users_list:
            paas_id = user_info.get('_id') or user_info.get('id')
            existing = self.env['paas.user'].search([('paas_id', '=', paas_id)], limit=1)
            
            # Find matching plan
            plan_id = False
            if user_info.get('plan') and user_info['plan'].get('id'):
                plan = self.env['paas.plan'].search([('paas_id', '=', user_info['plan']['id'])], limit=1)
                plan_id = plan.id if plan else False

            vals = {
                'username': user_info.get('username'),
                'github_id': user_info.get('githubId'),
                'plan_id': plan_id,
                'subscription_status': user_info.get('plan', {}).get('status', 'trial'),
            }
            
            # Map start/end dates if present
            if user_info.get('plan', {}).get('startDate'):
                start_dt = parser.isoparse(user_info['plan']['startDate'])
                vals['subscription_start_date'] = fields.Datetime.to_string(start_dt)
            if user_info.get('plan', {}).get('endDate'):
                end_dt = parser.isoparse(user_info['plan']['endDate'])
                vals['subscription_end_date'] = fields.Datetime.to_string(end_dt)

            if existing:
                existing.with_context(skip_api=True).write(vals)
            else:
                # Need to find or create partner
                email = user_info.get('email')
                partner = self.env['res.partner'].search([('email', '=', email)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].create({
                        'name': user_info.get('username') or email,
                        'email': email,
                    })
                
                vals.update({
                    'paas_id': paas_id,
                    'partner_id': partner.id,
                })
                self.env['paas.user'].with_context(skip_api=True).create(vals)
