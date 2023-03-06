# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For lice nse information, please see license.txt


from __future__ import unicode_literals
import frappe
import datetime
import json
from frappe import _, msgprint
from frappe.utils import flt
from erpnext.accounts.utils import get_fiscal_year
from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges

#row = [d[0], d.item_name,d.item_group,d.description,d.qty,d.stock_uom,d.base_rate, d.net_amount,d.name,d.transaction_date,d.customer, d.customer_name, d.territory,d.project, d.delivered_qty, d.billed_amt,d.company]
def execute(filters=None):
	if not filters: filters = {}
        
	#Check if customer id is according to naming series or customer name
	
	columns = get_columns()
	#msgprint(filters)
	data = []
        
	customer_list = get_details(filters)
	posting_date=0
	
	#frappe.msgprint(json.dumps(customer_list, default=datetime_handler))
	for d in customer_list:
		em=frappe.db.get_list("Sales Invoice Item",{"parent":d.name},["*"])
		sup=frappe.db.get_value("Customer",{"customer_name":d.customer_name},["*"],as_dict=1)
		it_name=''
		poa=''
		#frappe.msgprint(json.dumps(d.return_against, default=datetime_handler))
		for s in em:
			#frappe.msgprint(s.item_name)
			#frappe.msgprint(json.dumps(s, default=datetime_handler))
			it_name+=s.item_name + ','
		#frappe.msgprint(json.dumps(sup, default=datetime_handler))            
		if d.posting_date:
			posting_date=d.posting_date        
		if d.return_against:
			po=frappe.db.get_value("Sales Invoice",{"name":d.return_against},["posting_date"],as_dict=1) 
			poa= po.posting_date     		
		row = [sup.tax_id, d.customer_name,d.tim_tax_code,posting_date,d.name,it_name,d.total,d.total_taxes_and_charges,d.return_against,poa,d.type_of_exports,d.custom_entry_number,d.port_of_exit,d.destination_country,d.relavent_paragraph]
		data.append(row)
        
	return columns, data
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    #raise TypeError("Unknown type")
def get_columns():
	columns = [
   
		_("Pin Of Customer") + ":120",
		_("Name Of Customer") + ":120",
		_("ETR Serieal Number") + ":120",
		_("Invoice Date") + ":150",
        _("Invoice Number") + ":150",
		_("Description Of Goods ") + ":100",
		_("Taxable Value") + ":150",
                _("Amount Of VAT") + ":150",
                _("Relavant Invoice Number") + ":150",
                _("Relavant Invoice Date") + ":150",
				
         _("Type of Exports") + ":120",
		_("Custom Entry Number") + ":120",
		_("Port of Exit") + ":120",
		_("Destination Country") + ":150",
        _("Relevant Paragraph") + ":150",
		
         
         
         
	]

	
	return columns


def get_details(filters):
	#conditions = ""

	#if filters.get("customer"):
		#conditions += " where name = %(customer)s"
  
	return frappe.db.sql("""select * from `tabSales Invoice`  where
	 posting_date >= %(from_date)s and posting_date <= %(to_date)s  and tax_category=%(tax_category)s 
	
order by name desc

	""" , {
			 
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			 "tax_category": filters.tax_category
		} ,as_dict=True)


 
@frappe.whitelist()
def get_taxdetails(ids):
	url = 'http://209.182.239.212:1061/api/invoice'
	ref=''
	invoicecategory='Tax Invoice'
	po = frappe.db.get_value("Sales Invoice", {"name": ids}, ["*"], as_dict=1)
	sach = frappe.db.get_list("Sales Invoice Item", {"parent": ids}, ["*"])
	tax = frappe.db.get_value("Sales Taxes and Charges", {"parent": ids}, ["*"], as_dict=1)
	if po.is_return:
		invoicecategory="Credit Note"
	elif po.is_debit_note:
		invoicecategory="Debit Note"
		ref=po.return_against
	else:
		invoiceCategory="Tax Invoice"
	hea, sep, tail = str(po.get("posting_time")).partition('.')
	data = {
    "Invoice": {
        "SenderId": "c8ae9218bcde687ff24b",
        "InvoiceTimestamp":"{}T{}".format(po.get("posting_date"), hea),
        "InvoiceCategory": invoicecategory,
        "TraderSystemInvoiceNumber": ids,
        "RelevantInvoiceNumber": ref or "",
        "PINOfBuyer": po.get("tax_id"),
        "Discount": po.get("total_discount",0),
        "InvoiceType": "Original",
        "TotalInvoiceAmount": po.get("grand_total"),
        "TotalTaxableAmount": po.get("total"),
        "TotalTaxAmount": tax.get("tax_amount", 0), 
        "ExemptionNumber": "",
        "ItemDetails": [
            {
                "HSDesc": d.get("item_name"),
                "TaxRate": tax.get("rate", 0),
                "ItemAmount": d.get("amount"),
                "TaxAmount": round(d.get("amount") * (tax.get("rate", 0) / 100), 2),
                "TransactionType": "1",
                "UnitPrice": d.get("price_list_rate"),
                "HSCode": d.get("hs_code"),
                "Quantity": d.get("qty")
            }
            for d in sach
        ]
    }
	}
	headers = {
    'Content-Type': 'application/json'
	}

	response = requests.post(url, json=data, headers=headers)
	return data
	result = response.text
	y = json.loads(result)
	if 'Invoice' in y :
		qrc = y['Invoice']['QRCode']
	else:
		qrc = y['Existing']['QRCode']
	img = qrcode.make(qrc)
	file_name = "/home/frappe/frappe-bench/sites/keniya/public/files/{}.png".format(po.get("name"))
	img.save(file_name)
	#po['qrc'] = qrc
	frappe.db.sql("""update `tabSales Invoice`  set qrcode=%(qrcode)s  where
	 name = %(ids)s 

	""" , {
			 
			"qrcode": qrc,
			"ids": ids
			
		} ,as_dict=False)
	#frappe.db.set_value('Sales Invoice', ids, 'qrcode', qrc)
	return data
@frappe.whitelist()
def get_picklist(ids,batch_no): 
	po = frappe.db.get_value("Batch", {"name": batch_no}, ["*"], as_dict=1)
	frappe.db.sql("""update `tabPick List Item`  set batch_no=%(batch_no)s , exp_date=%(exp_date)s  where
	 name = %(ids)s 

	""" , {
			 
			"batch_no": batch_no,
		        "exp_date": po.expiry_date,
			"ids": ids
			
		} ,as_dict=False) 

	sales_order = frappe.db.get_value('Pick List Item', ids, 'sales_order')
	frappe.db.sql("""update `tabSales Order Item`  set batch_no=%(batch_no)s , exp_date=%(exp_date)s  where
	 parent = %(sales_order)s 

	""" , {
			 
			"batch_no": batch_no,
		        "exp_date": po.expiry_date,
			"sales_order": sales_order
			
		} ,as_dict=False) 

 

 

 
