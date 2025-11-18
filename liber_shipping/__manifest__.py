{
    'name': 'Liber Shipping',
    'version': '1.0.0',
    'summary': 'Cotiza y genera guías con la API de Liber',
    'description': """
Módulo para cotizar y generar guías desde Odoo usando la API de Liber.
""",
    'author': 'Gregory Rodríguez',
    'license': 'LGPL-3',
    'category': 'Inventory/Delivery',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/liber_menus.xml',
        'views/liber_config_views.xml',
        'views/liber_quote_views.xml',
        'views/liber_guide_views.xml',
    ],
    'external_dependencies': {'python': ['requests']},
    'installable': True,
    'application': True,
}




