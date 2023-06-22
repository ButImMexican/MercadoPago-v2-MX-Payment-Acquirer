# coding: utf-8

from odoo import fields, models, api

MX_CURRENCY = "MXN"


class AcquirerMercadopagoMX(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[
        ('mercadopago_mx', 'MercadoPago México')],
        ondelete={'mercadopago_mx': 'set default'})
    mercadopago_mx_public_key = fields.Char(string="Public Key")
    mercadopago_mx_access_token = fields.Char(string="Access Token")
    mercadopago_mx_test_public_key = fields.Char(string="TEST Public Key")
    mercadopago_mx_test_access_token = fields.Char(string="TEST Access Token")

    @api.model
    def _get_compatible_acquirers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to unlist Payco acquirers when the currency is not supported. """
        acquirers = super()._get_compatible_acquirers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name != MX_CURRENCY:
            acquirers = acquirers.filtered(lambda a: a.provider != 'mercadopago_mx')

        return acquirers

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'mercadopago_mx':
            return super()._get_default_payment_method_id()
        return self.env.ref('l10n_mx_payment_mercadopago.payment_method_mercadopago_mx').id

    def _get_mercadopago_mx_credentials(self):
        self.ensure_one()
        access_token = False
        public_key = False
        if self.state == 'enabled':
            public_key = self.mercadopago_mx_public_key
            access_token = self.mercadopago_mx_access_token
        else:
            public_key = self.mercadopago_mx_test_public_key
            access_token = self.mercadopago_mx_test_access_token

        return access_token, public_key
