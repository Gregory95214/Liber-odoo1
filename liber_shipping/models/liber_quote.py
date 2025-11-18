# -*- coding: utf-8 -*-
from odoo import models, fields

class LiberQuote(models.Model):
    _name = 'liber.quote'
    _description = 'Cotización de envío Liber'

    name = fields.Char(string='Referencia')
    price = fields.Float(string='Precio')
