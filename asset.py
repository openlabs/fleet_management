#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import ModelSQL, ModelView, fields


class Asset(ModelSQL, ModelView):
    """
    Fleet Management Asset
    """
    _name = "fleet.asset"
    _description = "Fleet Management Asset"

    code = fields.Char('Code', required=True, select=1)
    meter_unit =  fields.Many2One("product.uom", "Meter Unit",
        domain=[('category.name', '=', 'Length')])
    status = fields.Selection([
        ('Active', 'Active'),
        ('Out of Service'),
        ], "Status", readonly=True)

    # Specifications
    year = fields.Integer("Year")
    make = fields.Char("Make")
    model = fields.Char("Model")
    serial_number = fields.Char("Serial Number")
    license_plate = fields.Char("Plate Number")

    # Purchase
    vendor = fields.Many2One("party.party", "Vendor")
    purchase_date = fields.Date("Purchase Date")
    purchase_meter = fields.BigInteger("Purchase Meter")
    warranty_expiration_date = fields.Date("Warranty Expiration Date")
    warranty_expiration_meter = fields.BigInteger("Warranty Expiration Meter")

    # Status
    in_service_date = fields.Date("In Service Date")
    out_of_service_date = fields.Date("Out of Service Date")

    # Comments
    comment = fields.Text('Comment')


Asset()
