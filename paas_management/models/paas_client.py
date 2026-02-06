from odoo import models, api, _
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class PaasClient(models.AbstractModel):
    _name = 'paas.client'
    _description = 'PaaS API Client'

    @api.model
    def _get_headers(self):
        config = self.env['paas.config'].get_config()
        return {
            'Authorization': f'Bearer {config.admin_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    @api.model
    def _make_request(self, method, endpoint, data=None):
        config = self.env['paas.config'].get_config()
        url = f"{config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            _logger.info("PaaS API Request: %s %s - Data: %s", method, url, data)
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code >= 400:
                error_msg = f"Backend Error ({response.status_code}): {response.text}"
                _logger.error(error_msg)
                raise UserError(_("The backend returned an error: %s") % error_msg)
            
            if response.status_code == 204:
                return True
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error("Network Error: %s", str(e))
            raise UserError(_("Communication error with the backend: %s") % str(e))
        except Exception as e:
            _logger.error("Unexpected Error: %s", str(e))
            raise UserError(_("An unexpected error occurred: %s") % str(e))
