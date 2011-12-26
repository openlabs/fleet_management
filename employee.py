#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval


class Employee(ModelSQL, ModelView):
    """Set the information for Employee who are Driver.
    """
    _name = 'company.employee'

    is_driver = fields.Boolean('Is Driver')
    license_number = fields.Char('License Number',
        states={
            'required': Eval('is_driver', False),
            }, depends=['is_driver'])
    expiry_date = fields.Date('Expiry Date',
        states={
            'required': Eval('is_driver', False),
            }, depends=['is_driver'])
    notes = fields.Text('Notes')

Employee()
