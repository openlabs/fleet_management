#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

"""Test Driver for Fleet Management System"""

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


class DriverTestCase(unittest.TestCase):
     """
     Test Driver for Fleet Management System.
     """

     def setUp(self):
         """
         SetUp method.
         """
         trytond.tests.test_tryton.install_module('fleet_management')
         self.employee_obj = POOL.get('company.employee')
         self.party_obj = POOL.get('party.party')
         self.company_obj = POOL.get('company.company')
         self.currency_obj = POOL.get('currency.currency')
         self.date_obj = POOL.get('ir.date')

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

     def test_0010_employee_driver(self):
        """Create an employee who is driver
        """

        with Transaction().start(DB_NAME, USER, CONTEXT) as transaction:
            party_id = self.party_obj.create({
                'name': 'Test_Party',
                'code': '1001'
                })

            currency_id = self.currency_obj.create({
                'name': 'Rupee',
                'symbol': 'RS',
                'code': 'RS'
                })

            company_id = self.company_obj.create({
                'party': party_id,
                'currency': currency_id
                })

            date = self.date_obj.today()
            employee_id = self.employee_obj.create({
                'name': 'Test_Employee',
                'company': company_id,
                'is_driver': 'True',
                'license_number': '102030',
                'expiry_date': date,
                })

            employee_id, = self.employee_obj.search(
                [('name', '=', 'Test_Employee')]
                )

            self.assertEqual(self.employee_obj.browse(employee_id).name, 
                'Test_Employee')


def suite():
    """Create a test suite.
    """
    suite = trytond.tests.test_tryton.suite()

    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
         DriverTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
