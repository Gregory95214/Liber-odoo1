# -*- coding: utf-8 -*-
from odoo import models, fields

class LiberConfig(models.Model):
    _name = 'liber.config'
    _description = 'Configuración de Liber Paquetería'

    name = fields.Char(string='Nombre configuración', default='Configuración Liber')
