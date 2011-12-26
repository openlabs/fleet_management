#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.pyson import Eval, Equal, Not
from trytond.wizard import Wizard
from trytond.report import Report


class PurchaseLine(ModelSQL, ModelView):
    """
    Fleet Management Purchase Line
    """
    _name = 'purchase.line'

    product_fleet_type = fields.Function(
        fields.Char('Product_Fleet_Type', on_change_with=['product']),
        'get_product_fleet_type'
        )

    asset = fields.Many2One("fleet.asset", "Asset",
        states={
            'invisible': Not(Equal(Eval('product_fleet_type'), 'fuel')),
            'required': Equal(Eval('product_fleet_type'), 'fuel')
            },
        depends=['product_fleet_type']
        )

    meter_reading = fields.BigInteger("Meter Reading",
        states={
            'invisible': Not(Equal(Eval('product_fleet_type'),'fuel')),
            'required': (Eval('product_fleet_type') == 'fuel')
            },
        depends=['product_fleet_type']
        )

    fuel_efficiency = fields.Function(
        fields.Float("Fuel Efficiency",
        states={
            'invisible': Not(Equal(Eval('product_fleet_type'),'fuel')),
            },
        depends=['product_fleet_type']),
        'get_fuel_efficiency'
        )

    def get_product_fleet_type(self, ids, name):
        """Get the product type.
        """
        res = {}
        for purchase_line in self.browse(ids):
            res[purchase_line.id] = purchase_line.product.fleet_management_type
        return res

    def get_fuel_efficiency(self, ids, name):
        """Return the fuel efficiency
        """
        res = {}
        for purchase_line in self.browse(ids):
            efficiency = 0.00
            previous_line_ids = self.search([
                ('asset', '=', purchase_line.asset.id),
                ('purchase.purchase_date', '<', purchase_line.purchase.purchase_date)
                ], limit=1)
            if previous_line_ids:
                previous_line = self.browse(previous_line_ids[0])
                efficiency = (purchase_line.meter_reading - \
                    previous_line.meter_reading) / purchase_line.quantity
            res[purchase_line.id] = efficiency
        return res

    def on_change_with_product_fleet_type(self, vals):
        """Set the value of product_fleet_type so that the invisible and 
        required property may be set
        """
        product_obj = Pool().get('product.product')
        if vals.get('product'):
            product = product_obj.browse(vals['product'])
            return product.fleet_management_type
        return None

PurchaseLine()


class GetDates(ModelView):
    """Get the starting and end Date.
    """
    _name = 'purchase.line.fuel_efficency.init'

    begin_date = fields.Date('Begin Date', required=True)
    end_date = fields.Date('End Date', required=True)

    def default_begin_date(self):
        date_obj = Pool().get('ir.date')
        return date_obj.today()

    def default_end_date(self):
        date_obj = Pool().get('ir.date')
        return date_obj.today()

GetDates()


class FuelEfficiencyReport(Wizard):
    """Fuel Efficiency Wizard
    """
    _name = 'purchase.line.report_fuel_efficiency'

    states = {
        'init': {
            'result': {
                'type': 'form',
                'object': 'purchase.line.fuel_efficency.init',
                'state': [
                    ('end', 'Cancel', 'tryton-cancel'),
                    ('print', 'Print', 'tryton-print', True)
                ],
            },
        },
        'print': {
            'result':{
                'type': 'print',
                'report': 'purchase.line.fuel_efficiency',
                'state': 'end',
            },
        },
    }

FuelEfficiencyReport()


class GenerateFuelEfficiencyReport(Report):
    """Generate the fuel efficiency Report.
    """
    _name = 'purchase.line.fuel_efficiency'

    def parse(self, report, objects, datas, localcontext):
        """Get all the purchase orders lines with in the range dates
        that are given in wizard, product type as fuel and the state
        is of done or confirmed.

        :param report: BrowseRecord of the ir.action.report
        :param objects: BrowseRecordList of the records on which parse report
        :param datas: a dictionary with datas that will be set in local context
            of the report
        :param localcontext: the context used to parse the report
        """
        purchase_obj = Pool().get('purchase.purchase')
        purchase_line_obj = Pool().get('purchase.line')
        res = {}

        purchase_line_ids = purchase_line_obj.search([
            ('purchase.purchase_date', '>=',  datas['form']['begin_date']),
            ('purchase.purchase_date', '<=',  datas['form']['end_date']),
            ('purchase.state', 'in', ('done', 'confirmed')),
            ('product.fleet_management_type', '=', 'fuel')
            ])

        localcontext['purchase_lines'] = purchase_line_obj.browse(purchase_line_ids)
        localcontext['begin_date'] = datas['form']['begin_date']
        localcontext['end_date'] = datas['form']['end_date']

        return super(GenerateFuelEfficiencyReport, self).parse(report,
            objects, datas, localcontext)

GenerateFuelEfficiencyReport()
