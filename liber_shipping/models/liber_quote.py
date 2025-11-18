import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LiberQuote(models.Model):
    _name = 'liber.quote'
    _description = 'Cotización Liber'
    _order = 'id desc'

    name = fields.Char('Referencia', required=True,
                       default=lambda s: s.env['ir.sequence'].next_by_code('liber.quote') or '/')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('rated', 'Cotizado'),
        ('done', 'Guía creada'),
    ], default='draft', tracking=True)

    # Paquete
    package_content = fields.Char('Contenido', required=True)
    package_content_price = fields.Float('Valor contenido', default=0.0)
    package_height = fields.Float('Alto (cm)', required=True)
    package_width  = fields.Float('Ancho (cm)', required=True)
    package_depth  = fields.Float('Largo (cm)', required=True)
    package_weight = fields.Float('Peso (kg)', required=True)

    # Origen/Destino
    origin_postal_code  = fields.Char('CP Origen', required=True)
    origin_city_name    = fields.Char('Ciudad Origen', required=True)
    destiny_postal_code = fields.Char('CP Destino', required=True)
    destiny_city_name   = fields.Char('Ciudad Destino', required=True)

    # Remitente
    sender_full_name   = fields.Char('Remitente')
    sender_phone       = fields.Char('Tel. Remitente')
    sender_state       = fields.Char('Estado Remitente')
    sender_city        = fields.Char('Ciudad Remitente')
    sender_colony      = fields.Char('Colonia Remitente')
    sender_street      = fields.Char('Calle Remitente')
    sender_ext_number  = fields.Char('No. Ext. Remitente')
    sender_int_number  = fields.Char('No. Int. Remitente')
    sender_refs        = fields.Char('Referencias Remitente')

    # Destinatario
    recipient_full_name  = fields.Char('Destinatario')
    recipient_phone      = fields.Char('Tel. Destinatario')
    recipient_state      = fields.Char('Estado Dest.')
    recipient_city       = fields.Char('Ciudad Dest.')
    recipient_colony     = fields.Char('Colonia Dest.')
    recipient_street     = fields.Char('Calle Dest.')
    recipient_ext_number = fields.Char('No. Ext. Dest.')
    recipient_int_number = fields.Char('No. Int. Dest.')
    recipient_refs       = fields.Char('Referencias Dest.')

    rate_ids = fields.One2many('liber.quote.rate', 'quote_id', string='Cotizaciones')
    selected_rate_id = fields.Many2one('liber.quote.rate', string='Opción elegida')

    def _param(self, key):
        return self.env['ir.config_parameter'].sudo().get_param(key)

    # --- COTIZAR ---
    def action_get_rates(self):
        for rec in self:
            base = rec._param('liber.api.base') or ''
            key  = rec._param('liber.api.key.rates') or rec._param('liber.api.key.liber')
            if not base or not key:
                raise UserError(_('Configura URL base y API Key en Ajustes > Liber Shipping.'))

            url = base.rstrip('/') + '/rates/get-all-rates'
            payload = {
                "origin_postal_code": rec.origin_postal_code,
                "destiny_postal_code": rec.destiny_postal_code,
                "origin_city_name": rec.origin_city_name,
                "destiny_city_name": rec.destiny_city_name,
                "package_height": rec.package_height,
                "package_width": rec.package_width,
                "package_depth": rec.package_depth,
                "package_weight": rec.package_weight,
            }
            headers = {'liber_api_key': key}

            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                raise UserError(_('Error al cotizar: %s') % e)

            rec.rate_ids.unlink()
            rates = data if isinstance(data, list) else data.get('rates') or []
            if not rates:
                raise UserError(_('Sin tarifas devueltas. Respuesta: %s') % data)

            for r in rates:
                self.env['liber.quote.rate'].create({
                    'quote_id': rec.id,
                    'provider': (r.get('provider') or '').upper(),
                    'service_name': r.get('service_name') or r.get('shipping_code'),
                    'shipping_code': r.get('shipping_code'),
                    'product_code': r.get('product_code'),
                    'local_product_code': r.get('local_product_code'),
                    'price': float(r.get('price') or r.get('total') or 0.0),
                    'raw_response': r,
                })
            rec.state = 'rated'
        return True

    # --- CREAR GUÍA ---
    def action_create_guide(self):
        for rec in self:
            rate = rec.selected_rate_id
            if not rate:
                raise UserError(_('Selecciona una tarifa antes de crear la guía.'))

            base = rec._param('liber.api.base') or ''
            if not base:
                raise UserError(_('Configura la URL base de la API.'))
            url = base.rstrip('/') + '/guides/create-guide'

            # API Key por proveedor
            key_map = {
                'T1': rec._param('liber.api.key.t1'),
                'T2': rec._param('liber.api.key.t2'),
                'LIBER': rec._param('liber.api.key.liber') or rec._param('liber.api.key.rates'),
            }
            api_key = key_map.get((rate.provider or '').upper())
            if not api_key:
                raise UserError(_('Falta API Key para el proveedor %s.') % (rate.provider,))

            body = {
                "provider": (rate.provider or '').upper(),
                "guide_info": {
                    "package_content": rec.package_content,
                    "package_content_price": rec.package_content_price or 0,
                    "package_height": rec.package_height,
                    "package_depth": rec.package_depth,
                    "package_width": rec.package_width,
                    "package_weight": rec.package_weight
                },
                "sender_info": {
                    "postal_code": rec.origin_postal_code,
                    "full_name": rec.sender_full_name,
                    "telephone_number": rec.sender_phone,
                    "state": rec.sender_state,
                    "city": rec.sender_city or rec.origin_city_name,
                    "colony": rec.sender_colony,
                    "street_name": rec.sender_street,
                    "ext_number": rec.sender_ext_number,
                    "int_number": rec.sender_int_number or "",
                    "location_references": rec.sender_refs or ""
                },
                "recipient_info": {
                    "postal_code": rec.destiny_postal_code,
                    "full_name": rec.recipient_full_name,
                    "telephone_number": rec.recipient_phone,
                    "state": rec.recipient_state,
                    "city": rec.recipient_city or rec.destiny_city_name,
                    "colony": rec.recipient_colony,
                    "street_name": rec.recipient_street,
                    "ext_number": rec.recipient_ext_number,
                    "int_number": rec.recipient_int_number or "",
                    "location_references": rec.recipient_refs or ""
                }
            }

            # Campos específicos según proveedor
            prov = (rate.provider or '').upper()
            if prov == 'T1':
                body["shipping_code"] = rate.shipping_code
            elif prov == 'T2':
                body["product_code"] = rate.product_code
                body["local_product_code"] = rate.local_product_code

            headers = {'liber_api_key': api_key}

            try:
                resp = requests.post(url, json=body, headers=headers, timeout=60)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                raise UserError(_('Error al crear la guía: %s') % e)

            guide = self.env['liber.guide'].create({
                'quote_id': rec.id,
                'provider': rate.provider,
                'shipping_code': rate.shipping_code,
                'product_code': rate.product_code,
                'local_product_code': rate.local_product_code,
                'price': rate.price,
                'response_json': data,
            })
            rec.state = 'done'
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'liber.guide',
                'view_mode': 'form',
                'res_id': guide.id,
            }

class LiberQuoteRate(models.Model):
    _name = 'liber.quote.rate'
    _description = 'Tarifa Liber'
    _order = 'price asc'

    quote_id = fields.Many2one('liber.quote', required=True, ondelete='cascade')
    provider = fields.Char('Proveedor')
    service_name = fields.Char('Servicio')
    shipping_code = fields.Char('Shipping Code')
    product_code = fields.Char('Product Code')
    local_product_code = fields.Char('Local Product Code')
    price = fields.Float('Precio')
    raw_response = fields.Json('Respuesta cruda')

    def action_select(self):
        self.ensure_one()
        self.quote_id.selected_rate_id = self.id
        return True

class LiberGuide(models.Model):
    _name = 'liber.guide'
    _description = 'Guía Liber'
    _order = 'id desc'

    name = fields.Char(default=lambda s: s.env['ir.sequence'].next_by_code('liber.guide') or '/', readonly=True)
    quote_id = fields.Many2one('liber.quote', string='Cotización origen')
    provider = fields.Char('Proveedor')
    shipping_code = fields.Char('Shipping Code')
    product_code = fields.Char('Product Code')
    local_product_code = fields.Char('Local Product Code')
    price = fields.Float('Precio')
    response_json = fields.Json('Respuesta API')

