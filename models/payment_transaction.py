# -*- coding: utf-8 -*-

import logging
import mercadopago
from werkzeug import urls
from odoo import _, api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_repr
from odoo.addons.payment import utils as payment_utils
from odoo.addons.l10n_mx_payment_mercadopago.controllers.main import MercadoPagoMXController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    mercadopago_mx_preference_id = fields.Char(string="MP Preference ID")
    mercadopago_mx_collector_id = fields.Char(string="MP Collector ID")

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'mercadopago_mx':
            return res

        base_url = self.acquirer_id.get_base_url()
        access_token, public_key = self.acquirer_id._get_mercadopago_mx_credentials()
        preference = self._get_mercadopago_mx_preference_id(base_url, access_token)
        mp_values = {
            'mpmx_public_key': public_key,
            'mpmx_preference_id': preference['id'],
            'mpmx_init_point': preference['init_point'],
            'api_url': urls.url_join(base_url, MercadoPagoMXController._checkout_url),
        }
        
        return mp_values

    def _get_mercadopago_mx_preference_id(self, base_url, access_token):
        status_url = urls.url_join(base_url, MercadoPagoMXController._status_url)
        sdk = mercadopago.SDK(access_token)
        preference_data = {
            "items": [
                {
                    "title": self.reference,
                    "quantity": 1,
                    "unit_price": self.amount
                }
            ],
            "back_urls": {
                "success":  status_url,
                "failure":  status_url,
                "pending":  status_url
               },
            "auto_return": "approved",
            "external_reference": self.reference,
            "statement_descriptor": self.company_id.name,
            "binary_mode": True
        }

        try:
            preference_response = sdk.preference().create(preference_data)
            if preference_response.get('status') and preference_response['status'] == 201:
                preference = preference_response["response"]
                self.write({
                    'mercadopago_mx_preference_id': preference['id'],
                    'mercadopago_mx_collector_id': preference['collector_id']
                })
                return preference
        except Exception as e:
            return e

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'mercadopago_mx':
            return tx

        preference_id = data.get('preference_id')
        if not preference_id:
            raise ValidationError(
                "MercadoPago MX: " + _(
                    "Datos recibidos sin ID de preferencia (%(ref)s).",
                    ref=preference_id
                )
            )

        tx = self.search([('mercadopago_mx_preference_id', '=', preference_id), ('provider', '=', 'mercadopago_mx')])
        if not tx:
            raise ValidationError(
                "MercadoPago MX: " + _("No se encontró ninguna transacción que coincida con el ID de preferencia: %s.", preference_id)
            )

        return tx

    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != 'mercadopago_mx':
            return

        self.acquirer_reference = data.get('payment_id')

        status = data.get('status')
        if status == 'in_process':
            self._set_pending(state_message=_("Estamos procesando su pago."))
        elif status == 'approved':
            self._set_done(state_message=_("¡Hecho! Su pago fue acreditado."))
        elif status == 'rejected':
            self._set_canceled(state_message=_("Su pago fue rechazado."))
        else:
            _logger.warning(
                "received unrecognized payment state %s for transaction with reference %s",
                status, self.reference
            )
            self._set_error("MercadoPago MX: " + _("Estado de pago no válido."))
