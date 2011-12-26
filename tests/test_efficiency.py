# -*- coding: utf-8 -*-
"""
    test_efficiency

    Test Average fuel efficiency

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement

import sys, os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

from decimal import Decimal
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class FuelTestCase(unittest.TestCase):
    """
    Test average fuel efficiency for assets.
    """

    def setUp(self):
        """
        Installing the module and initializing the objects.
        """
        trytond.tests.test_tryton.install_module('fleet_management')
        self.currency_obj = POOL.get('currency.currency')
        self.party = POOL.get('party.party')
        self.user_obj = POOL.get('res.user')
        self.account_obj = POOL.get('account.account')
        self.account_template_obj = POOL.get('account.account.template')
        self.create_chart_account_obj = POOL.get(
            'account.account.create_chart_account', type="wizard")
        self.company_obj = POOL.get('company.company')
        self.payment_term_obj = POOL.get('account.invoice.payment_term')
        self.location_obj = POOL.get('stock.location')
        self.purchase_obj = POOL.get('purchase.purchase')
        self.product_obj = POOL.get('product.product')
        self.purchase_line_obj = POOL.get('purchase.line')
        self.asset_obj = POOL.get('fleet.asset')
        self.uom_obj = POOL.get('product.uom')
        self.uom_category_obj = POOL.get('product.uom.category')
        self.product_category_obj = POOL.get('product.category')
        self.date_obj = POOL.get('ir.date')

    def setup_chart_of_accounts(self, company):
        """
        Sets up chart of accounts
        """
        account_template, = self.account_template_obj.search(
            [('parent', '=', False)])

        wiz_id = self.create_chart_account_obj.create()
        self.create_chart_account_obj.execute(wiz_id, {}, 'account')
        self.create_chart_account_obj.execute(wiz_id,
            {
                'form': {
                    'account_template': account_template,
                    'company': company,
                }
            }, 'create_account'
        )

    def test_0010_average_efficiency(self):
        """
        Test to check the functional field 'average_fuel_efficiency'
        """

        with Transaction().start(DB_NAME, USER, CONTEXT) as transaction:

            payment_term_id = self.payment_term_obj.create({
                'name': 'Cash',
            })

            party = self.party.create({
                'name': 'Openlabs'
                })
            currency = self.currency_obj.create({
                'name': 'US Dollar',
                'symbol': 'USD',
                'code': 'USD',
                })

            company_id = self.company_obj.create({
                'party': party,
                'currency': currency,
                })

            self.user_obj.write(USER, {
                'main_company': company_id,
                'company': company_id,
                })

            self.setup_chart_of_accounts(company_id)

            # Create multiple asset to check fuel efficiency
            asset_id1 = self.asset_obj.create({
                'code': 'car',
                })
            asset_id2 = self.asset_obj.create({
                'code': 'truck',
                })
            asset_id3 = self.asset_obj.create({
                'code': 'bike',
                })

            uom_category_id = self.uom_category_obj.create({
                'name': 'Volume',
                })

            default_uom_id, = self.uom_obj.search([
                'name', '=', 'Gallon'
                ])

            product_category = self.product_category_obj.create({
                'name': 'coal'
                })

            account, = self.account_obj.search(
                [('kind', '=', 'expense')])

            product_id = self.product_obj.create({
                'name': 'fuel',
                'type': 'consumable',
                'cost_price_method': 'fixed',
                'default_uom': default_uom_id,
                'category': product_category,
                'account_expense': account,
                'purchase_uom': default_uom_id,
                'purchasable': True,
                })
            warehouse_id, = self.location_obj.search([
                ('code', '=', 'WH')
                ], limit=1)
            today = self.date_obj.today()

            purchase_id = self.purchase_obj.create({
                'company': company_id,
                'purchase_date': today,
                'payment_term': payment_term_id,
                'party': party,
                'warehouse': warehouse_id,
                'currency': currency,
                'state': 'draft',
                'invoice_method': 'manual',
                'invoice_state': 'none',
                'shipment_state': 'none',
                })

            # purchase lines for first asset
            self.purchase_line_obj.create({
                'type': 'line',
                'product': product_id,
                'meter_reading': '30',
                'description': 'fuel',
                'asset': asset_id1,
                'quantity': 10.0,
                'unit_price': Decimal('10'),
                'unit': default_uom_id,
                'purchase': purchase_id,
                })

            self.purchase_line_obj.create({
                'type': 'line',
                'product': product_id,
                'meter_reading': '100',
                'description': 'fuel',
                'asset': asset_id1,
                'quantity': 15.0,
                'unit_price': Decimal('10'),
                'unit': default_uom_id,
                'purchase': purchase_id,
                })

            # purchase line for second asset
            self.purchase_line_obj.create({
                'type': 'line',
                'product': product_id,
                'meter_reading': '50',
                'description': 'petrol',
                'asset': asset_id2,
                'quantity': 20.0,
                'unit_price': Decimal('10'),
                'unit': default_uom_id,
                'purchase': purchase_id,
                })

            self.asset = POOL.get('fleet.asset')

            asset1 = self.asset.browse(asset_id1)
            asset2 = self.asset.browse(asset_id2)
            self.assertEqual(asset1.average_fuel_efficiency, Decimal('2.8'))

            # test for asset having one purchase line
            self.assertEqual(asset2.average_fuel_efficiency, Decimal('2.5'))

            # test for asset having no purchase line
            asset3 = self.asset.browse(asset_id3)
            self.assertEqual(asset3.average_fuel_efficiency, 0)


def suite():
    """Create a test suite
    """
    suite = trytond.tests.test_tryton.suite()

    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(FuelTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

