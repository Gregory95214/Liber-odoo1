{
    'name': 'Liber Shipping',
    'version': '17.0.1.0.0',
    'summary': 'Integración de Liber Paquetería con Odoo',
    'description': """
Módulo para cotizar y generar guías de Liber Paquetería desde Odoo.
""",
    'author': 'Gregory Rodríguez',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
    'security/ir.model.access.csv',
    'views/liber_menus.xml',
    'views/liber_config_views.xml',
    'views/liber_quote_views.xml',
],
    'installable': True,
    'application': True,
}

