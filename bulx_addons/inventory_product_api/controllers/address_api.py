import logging

from odoo import http
from odoo.http import request
from odoo.tools import debugger


class Bulx(http.Controller):

    @http.route('/bulx/create-address', type='json', auth='public')
    def bulx_create_address(self, **rec):
        logging.warn(rec)
        # debugger.SUPPORTED_DEBUGGER.
        if "address_type" in rec and rec['address_type']:
            if rec['address_type'] not in ['Home', 'Business']:
                return {'status': 500, 'message': "address_type must be 'Home','Business'"}
        if "building_type" in rec and rec['building_type']:
            if rec['building_type'] not in ['Apartment', 'Villa_House']:
                return {'status': 500, 'message': "building_type must be 'Apartment','Villa_House'"}
        if not 'customer_id' in rec:
            return {'status': 500, 'message': "customer_id field is required and blank is not acceptable"}
        else:
            customer = request.env['res.partner'].sudo().search(['|',('bulx_code', '=', rec['customer_id'].lower()),('bulx_code', '=', rec['customer_id'].upper())])
        if not 'id' in rec and not rec['id']:
            return {'status': 500, 'message': "id field is required and blank is not acceptable"}
        if 'region_id' in rec :
            region_id = request.env['bulx.region'].sudo().search(['|',('bulx_id', '=', rec['region_id'].lower()),('bulx_id', '=', rec['region_id'].upper())])
            print(region_id)
            logging.warn(region_id)
            if not region_id:
                return {'status': 500, 'message': "region is not found"}
        vals = {
            "address_type": rec['address_type'] if "address_type" in rec else False,
            'building_type': rec['building_type'] if "building_type" in rec else False,
            'street': rec['street'] if "street" in rec else False,
            'land_mark': rec['land_mark'] if "land_mark" in rec else False,
            'latitude': rec['latitude'] if "latitude" in rec else False,
            'Longitude': rec['Longitude'] if "Longitude" in rec else False,
            'building_number': rec['building_number'] if "building_number" in rec else False,
            'villa_number': rec['villa_number'] if "villa_number" in rec else False,
            'floor_number': rec['floor_number'] if "floor_number" in rec else False,
            'apartment_number': rec['apartment_number'] if "apartment_number" in rec else False,
            'customer_id': customer.id,
            'region_id': region_id.id,
            'is_api': True,
            'bulx_id': rec['id']
        }
        logging.warn(vals)
        print(vals)
        bulx_adress = request.env['bulx.address'].sudo().create(vals)
        return {'status': 200, 'message': "Address - Success"}

    @http.route('/bulx/update-address', type='json', auth='public')
    def bulx_update_address(self, **rec):
        addressv = {'is_api': True}
        address_id = request.env['bulx.address']
        logging.warn(rec)
        if 'id' in rec and rec['id']:
            address_id = request.env['bulx.address'].sudo().search([('bulx_id', '=', rec['id'])])
            logging.warn(address_id)
            if not address_id:
                return {'status': 500, 'message': "Address not found for this ID"}
        else:
            return {'status': 500, 'message': "ID is Required"}
        if "address_type" in rec:
            addressv['address_type'] = rec['address_type']
            logging.warn(rec['address_type'])
            logging.warn(addressv['address_type'])
        if "building_type" in rec:
            addressv['building_type'] = rec['building_type']
        if "street" in rec:
            addressv['street'] = rec['street']
        if "land_mark" in rec:
            addressv['land_mark'] = rec['land_mark']
        if "latitude" in rec:
            addressv['latitude'] = rec['latitude']
        if "Longitude" in rec:
            addressv['Longitude'] = rec['Longitude']
        if "building_number" in rec:
            addressv['building_number'] = str(rec['building_number'])
        if "villa_number" in rec:
            addressv['villa_number'] = str(rec['villa_number'])
        if "floor_number" in rec:
            addressv['floor_number'] = str(rec['floor_number'])
        if "apartment_number" in rec:
            addressv['apartment_number'] = str(rec['apartment_number'])
        if "region_id" in rec:
            # region_id = request.env['bulx.region'].sudo().search([('bulx_id', '=', rec['region_id'].lower())])
            region_id = request.env['bulx.region'].sudo().search(
                ['|', ('bulx_id', '=', rec['region_id'].lower()), ('bulx_id', '=', rec['region_id'].upper())])
            logging.warn("region_id")
            logging.warn(region_id)
            if not region_id:
                return {'status': 500, 'message': "region is not found"}
            addressv['region_id'] = region_id.id
        if not 'id' in rec and rec['id']:
            return {'status': 500, 'message': "id field is required and blank is not acceptable"}
        address_id = request.env['bulx.address'].sudo().search([('bulx_id', '=', rec['id'])])
        if not address_id:
            return {'status': 500, 'message': "brand record not found in DB"}
        address = address_id.sudo().write(addressv)
        return {'status': 200, 'message': "Address updated- successful"}

    @http.route('/bulx/delete-address', type='json', auth='public')
    def bulx_delete_address(self, **rec):
        if not 'id' in rec and rec['id']:
            return {'status': 500, 'message': "code field is required and blank is not acceptable"}
        try:
            address_id = request.env['bulx.address'].sudo().search([('bulx_id', '=', rec['id'])])
            if not address_id:
                return {'status': 500, 'message': "Address id not found in DB"}
            address_id.unlink()
        except:
            return {'status': 500, 'message': "cannot delete Address as it related to other record"}
        return {'status': 200, 'message': "Deleted Success"}
