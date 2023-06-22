# -*- coding: utf-8 -*-

import logging
import pprint
import requests
import werkzeug
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class MercadoPagoMXController(http.Controller):
    _checkout_url = '/payment/mercadopago-mx/checkout'
    _status_url = '/payment/mercadopago-mx/return'

    @http.route(_checkout_url, type='http', auth='public', website=True, csrf=False, save_session=False)
    def mercadopago_mx_checkout(self, **post):
        """ MercadoPago MX."""
        return request.render('l10n_mx_payment_mercadopago.checkout', post)

    @http.route(_status_url, type='http', auth='public', website=True, csrf=False, save_session=False)
    def mercadopago_mx_return(self, **post):
        _logger.info("entering _handle_feedback_data with data:\n%s", pprint.pformat(post))
        request.env['payment.transaction'].sudo()._handle_feedback_data('mercadopago_mx', post)
        return request.redirect('/payment/status')
