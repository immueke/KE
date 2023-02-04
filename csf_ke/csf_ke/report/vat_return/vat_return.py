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
		em=frappe.db.get_list("Purchase Invoice Item",{"parent":d.name},["*"])
		sup=frappe.db.get_value("Supplier",{"supplier_name":d.supplier_name},["*"],as_dict=1)
		it_name=''
		#frappe.msgprint(json.dumps(em, default=datetime_handler))
		for s in em:
			#frappe.msgprint(s.item_name)
			#frappe.msgprint(json.dumps(s, default=datetime_handler))
			it_name+=s.item_name + ','
		#frappe.msgprint(json.dumps(sup, default=datetime_handler))            
		if d.posting_date:
			posting_date=d.posting_date        
		row = [sup.country,sup.tax_id, d.supplier_name,d.tim_tax_code,d.bill_date,d.bill_no,it_name,d.total,d.total_taxes_and_charges,d.return_against,'']
		data.append(row)
        
	return columns, data
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    #raise TypeError("Unknown type")
def get_columns():
	columns = [
    _("Type Of Purchase") + ":120",
		_("Pin Of Supplier") + ":120",
		_("Name Of Supplier") + ":120",
		_("ETR Serieal Number") + ":120",
		_("Invoice Date") + ":150",
        _("Invoice Number") + ":150",
		_("Description Of Goods ") + ":100",
		_("Taxable Value") + ":150",
                _("Amount Of VAT") + ":150",
                _("Relavant Invoice Number") + ":150",
                _("Relavant Invoice Date") + ":150"
				
         
         
         
         
	]

	
	return columns


def get_details(filters):
	#conditions = ""

	#if filters.get("customer"):
		#conditions += " where name = %(customer)s"
  
	return frappe.db.sql("""select * from `tabPurchase Invoice`  where
	 posting_date >= %(from_date)s and posting_date <= %(to_date)s  and tax_category=%(tax_category)s 
	
order by name desc

	""" , {
			 
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			 "tax_category": filters.tax_category
		} ,as_dict=True)


 

 

 
