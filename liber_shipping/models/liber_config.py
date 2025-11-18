from odoo import models, fields


class LiberConfig(models.Model):
    _name = 'liber.config'
    _description = 'Configuración Liber Shipping'

    name = fields.Char(string='Nombre', default='Configuración Liber Shipping')
    api_url = fields.Char(string='URL de la API')
    api_key = fields.Char(string='API Key', help='Clave de acceso a la API de Liber')

