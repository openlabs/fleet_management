#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval


class Product(ModelSQL, ModelView):
    """
    Fleet Management Product
    """
    _name = "product.template"
    _rec_name = 'fleet_management_type'

    fleet_management_type = fields.Selection([
        ('fuel', 'Fuel'),
        ('tire', 'Tire'),
        ], "Fleet Management Type",
        states={'invisible': Eval('type') != 'goods'},
        depends=['type'])

Product()
