from odoo import models, fields

class LiberSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    liber_api_base = fields.Char(
        string="Liber API Base",
        config_parameter='liber.api.base',
        default='https://mawh8ut7ek.execute-api.mx-central-1.amazonaws.com/development',
        help="URL base de la API de Liber (ambiente)."
    )
    liber_api_key_rates = fields.Char(
        string="API Key - Rates",
        config_parameter='liber.api.key.rates',
        help="API Key para endpoint de cotizaciones."
    )
    liber_api_key_t1 = fields.Char(
        string="API Key - T1",
        config_parameter='liber.api.key.t1',
        help="API Key para crear guía con proveedor T1."
    )
    liber_api_key_t2 = fields.Char(
        string="API Key - T2",
        config_parameter='liber.api.key.t2',
        help="API Key para crear guía con proveedor T2."
    )
    liber_api_key_liber = fields.Char(
        string="API Key - LIBER",
        config_parameter='liber.api.key.liber',
        help="API Key para crear guía con proveedor LIBER (si aplica)."
    )

