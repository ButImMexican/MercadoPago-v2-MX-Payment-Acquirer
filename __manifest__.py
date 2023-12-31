# -*- coding: utf-8 -*-
{
    'sequence': 100,
    'version': "15.0.0.1",
    'name': 'MercadoPago v2 MX Payment Acquirer',
    'images': ['static/src/img/main.png'],
    'price': 50,
    'currency': 'USD',
    'category': 'Accounting/Payment Acquirers',
    'summary': 'Payment Acquirer: MercadoPago México Implementation v2',
    'author': "Yan chirino <support@yanchirino.com>",
    'website': "https://yanchirino.com",
    'license': "Other proprietary",
    'depends': ['base','web','payment'],
    'external_dependencies': {"python": ["mercadopago"], "bin": []},
    'data': [
        #'security/ir.model.access.csv',
        'views/acquirer.xml',
        'views/templates.xml',
        'data/acquirer.xml',
        ],    
    'post_load': None,
    'pre_init_hook': None,
    'post_init_hook': None,
    'uninstall_hook': 'uninstall_hook',
    'application': True,
    'auto_install': False,
    'installable': True,
}
