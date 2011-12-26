#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
"""Test Asset for Fleet Management System."""

import sys, os

DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT,\
    test_view, test_depends
from trytond.transaction import Transaction


class AssetTestCase(unittest.TestCase):
    """
    Test Asset for Fleet Management System.
    """

    def setUp(self):
        """
        Setup method
        """
        trytond.tests.test_tryton.install_module('fleet_management')
        self.asset_obj = POOL.get('fleet.asset')
        self.uom_obj = POOL.get('product.uom')

    def test_0005_view(self):
        """
        Test View
        """
        test_view('fleet_management')

    def test_0006_depends(self):
        """
        Test depends
        """
        test_depends()

    def test_0010_asset(self):
        """
        Create a new asset.
        """

        with Transaction().start(DB_NAME, USER, CONTEXT) as transaction:

            uom_id, = self.uom_obj.search(
                [('name', '=', 'Kilometer')]
                )
            asset_id = self.asset_obj.create({
                'code': 'Car',
                'meter_unit': uom_id,
                })

            asset_id, =  self.asset_obj.search([('code', '=', 'Car')])

            self.assertEqual(self.asset_obj.browse(asset_id).code, 'Car')

    def test_0020_asset(self):
        """
        Create an asset without defining meter_unit and raise exception
        """

        with Transaction().start(DB_NAME, USER, CONTEXT) as transaction:

            self.assertRaises(Exception, self.asset_obj.create,
                {
                'code': 'Bus',
                })

def suite():
    """Create a test suite.
    """
    suite = trytond.tests.test_tryton.suite()

    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
         AssetTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
