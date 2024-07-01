# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_amount = fields.Float('Discount (Rp)', digits=(10,2))

    @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount:
            self.discount_amount = 0

    @api.onchange('discount_amount')
    def _onchange_discount_amount(self):
        if self.discount_amount:
            self.discount = 0

    @api.multi
    @api.constrains('discount', 'discount_amount')
    def _check_only_one_discount(self):
        for line in self:
            if line.discount and line.discount_amount:
                raise ValidationError(("You can only set one type of discount per line."))


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_amount')
    def _compute_amount(self):
        vals = {}
        for line in self.filtered(lambda l: l.discount_amount):
            real_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) - (line.discount_amount or 0.0)
            twicked_price = real_price / (1 - (line.discount or 0.0) / 100.0)
            vals[line] = {'price_unit': line.price_unit}
            line.update({'price_unit': twicked_price})

        res = super(SaleOrderLine, self)._compute_amount()
        for line in vals.keys():
            line.update(vals[line])
        return res

    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({'discount_amount': self.discount_amount})
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id

        if not account and self.product_id:
            raise UserError(('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') % (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos and account:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'discount_amount': self.discount_amount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'display_type': self.display_type,
        }
        return res

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    discount_amount = fields.Float('Discount (Rp)', digits=(10,2))

    @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount:
            self.discount_amount = 0

    @api.onchange('discount_amount')
    def _onchange_discount_amount(self):
        if self.discount_amount:
            self.discount = 0

    def _prepare_invoice_line(self):
        data = {
            'name': self.name,
            'origin': self.origin,
            'uom_id': self.uom_id.id,
            'product_id': self.product_id.id,
            'account_id': self.account_id.id,
            'price_unit': self.price_unit,
            'quantity': self.quantity,
            'discount': self.discount,
            'discount_amount': self.discount_amount,
            'account_analytic_id': self.account_analytic_id.id,
            'analytic_tag_ids': self.analytic_tag_ids.ids,
            'invoice_line_tax_ids': self.invoice_line_tax_ids.ids
        }
        return data

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity', 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id', 'invoice_id.date_invoice', 'invoice_id.date', 'discount_amount')
    def _compute_price(self):
        if not self.discount_amount:
            return super(AccountInvoiceLine, self)._compute_price()
        prev_price_unit = self.price_unit
        prev_discount_amount = self.discount_amount
        price_unit = self.price_unit - self.discount_amount
        self.update({
            'price_unit': price_unit,
            'discount_amount': 0.0,
        })
        super(AccountInvoiceLine, self)._compute_price()
        self.update({
            'price_unit': prev_price_unit,
            'discount_amount': prev_discount_amount,
        })

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount = fields.Monetary('Discount', default=0.0, store=True, readonly=True, compute='_compute_discount', currency_field='currency_id')
    amount_without_discount_tax = fields.Monetary('Undiscounted Amount', default=0.0, store=True, readonly=True, compute='_compute_amount_without_discount_tax', currency_field='currency_id')

    @api.one
    @api.depends('order_line.discount_amount')
    def _compute_discount(self):
        disc = 0
        for line in self.order_line:
            if line.discount_amount:
                disc += line.discount_amount

        self.discount = disc

    @api.one
    @api.depends('order_line.discount_amount', 'amount_untaxed')
    def _compute_amount_without_discount_tax(self):
        disc = 0
        for line in self.order_line:
            if line.discount_amount:
                disc += line.discount_amount

        self.amount_without_discount_tax = self.amount_untaxed + disc

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    discount = fields.Monetary('Discount', default=0.0, store=True, readonly=True, compute='_compute_discount', currency_field='currency_id')
    amount_without_discount_tax = fields.Monetary('Undiscounted Amount', default=0.0, store=True, readonly=True, compute='_compute_amount_without_discount_tax', currency_field='currency_id')

    @api.one
    @api.depends('invoice_line_ids.discount_amount')
    def _compute_discount(self):
        disc = 0
        for line in self.invoice_line_ids:
            if line.discount_amount:
                disc += line.discount_amount

        self.discount = disc

    @api.one
    @api.depends('invoice_line_ids.discount_amount', 'amount_untaxed')
    def _compute_amount_without_discount_tax(self):
        disc = 0
        for line in self.invoice_line_ids:
            if line.discount_amount:
                disc += line.discount_amount

        self.amount_without_discount_tax = self.amount_untaxed + disc

    @api.multi
    def get_taxes_values(self):
        self.ensure_one()
        vals = {}
        for line in self.invoice_line_ids.filtered('discount_amount'):
            vals[line] = {
                'price_unit': line.price_unit,
                'discount_amount': line.discount_amount,
            }
            price_unit = line.price_unit - line.discount_amount
            line.update({
                'price_unit': price_unit,
                'discount_amount': 0.0,
            })
        tax_grouped = super(AccountInvoice, self).get_taxes_values()
        for line in vals.keys():
            line.update(vals[line])
        return tax_grouped
