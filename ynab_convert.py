#!/usr/bin/env python

"""
Convert external CSV data from multiple sources into YNAB's CSV import format.
"""

from __future__ import print_function
import sys
import csv
import ConfigParser
import argparse

CONFIG = ConfigParser.SafeConfigParser()
CONFIG.read('ynab_convert.ini')
CONFIG_MAIN    = dict(CONFIG.items('main'))
CONFIG_SHOPIFY = dict(CONFIG.items('shopify'))
CONFIG_CHASE   = dict(CONFIG.items('chase'))

def write(fileobj, data):
    """Write YNAB-style data to a new CSV file."""

    writer = csv.DictWriter(fileobj, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)

def convert(shopify_trans=None, shopify_payouts=None, chase=None):
    """Convert external data into YNAB format.
    
    Takes in CSV filenames and produces a list of dicts using YNAB's key names.
    Currently supports these sources:
      * Shopify Transactions Export CSV
      * Shopify Payouts Export CSV
      * Chase Bank Activity Export CSV
    """

    data = []
    if shopify_trans:
        data.extend(read_and_convert_shopify_transactions(shopify_trans))
    if shopify_payouts:
        data.extend(read_and_convert_shopify_payouts(shopify_payouts))
    if chase:
        data.extend(read_and_convert_chase(chase))
    return data

def _shopify_date_to_ynab(text):
    date = text.split()[0]
    yyyy = date.split('-')[0]
    mm = date.split('-')[1]
    dd = date.split('-')[2]
    return "%s/%s/%s" % (mm, dd, yyyy)

def _set_amount(entry, amt):
    amt = float(amt)
    if amt > 0:
        entry['Inflow']   = str(amt)
        entry['Outflow']  = ''
    else:
        entry['Inflow']   = ''
        entry['Outflow']  = str(0-amt)

def read_and_convert_shopify_transactions(filename):
    """Read in Shopify transaction CSV and convert to YNAB-style."""

    data = []
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            order = row['Order'].strip('#')
            date = _shopify_date_to_ynab(row['Transaction Date'])
            if row['Type'] == "charge":
                entry_gross = {}
                entry_gross['Date']     = date
                entry_gross['Memo']     = 'order # %s' % order
                _set_amount(entry_gross, row['Amount'])
                entry_gross['Payee']    = CONFIG_MAIN['payee_you']
                entry_gross['Category'] = CONFIG_SHOPIFY['category_income']
                entry_fee = {}
                entry_fee['Date']     = date
                entry_fee['Memo']     = 'order # %s' % order
                entry_fee['Inflow']   = ''
                entry_fee['Outflow']  = row['Fee']
                entry_fee['Payee']    = 'Shopify'
                entry_fee['Category'] = CONFIG_SHOPIFY['category_fees']
                data.append(entry_gross)
                data.append(entry_fee)
            elif row['Type'] == "refund":
                entry = {}
                entry['Date']     = date
                entry['Memo']     = 'order # %s refund' % order
                _set_amount(entry, row['Amount'])
                entry['Payee']    = 'Shopify'
                entry['Category'] = CONFIG_SHOPIFY['category_refunds']
                data.append(entry)
            elif row['Type'] == "adjustment":
                entry = {}
                entry['Date']     = date
                entry['Memo']     = 'order # %s refund fee adjustment' % order
                _set_amount(entry, row['Amount'])
                entry['Payee']    = CONFIG_MAIN['payee_you']
                entry['Category'] = CONFIG_SHOPIFY['category_fees']
                data.append(entry)
            else:
                raise Exception("Category \"%s\" not recognized" % row['Type'])
    return data

def read_and_convert_shopify_payouts(filename):
    data = []
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            status = row['Status'] # will this sometimes be pending?
            date = _shopify_date_to_ynab(row['Payout Date'])
            entry = {}
            entry['Category'] = ''
            entry['Memo'] = ''
            entry['Date'] = date
            entry['Payee']    = 'Transfer: ' + CONFIG_SHOPIFY['payout_payee']
            # note this math is backwards compared to the transactions
            total = float(row['Total']) # net outbound transfer amount
            _set_amount(entry, 0-total)
            data.append(entry)
    return data

def read_and_convert_chase(filename):
    """Read in Shopify transaction CSV and convert to YNAB-style."""
    data = []
    # Type,Trans Date,Post Date,Description,Amount
    with open(filename, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date = row['Trans Date']
            entry = {}
            entry['Date']     = date
            entry['Memo']     = "%s: %s" % ( row["Type"], row["Description"] )
            entry['Category'] = "" # unknown, at least in most cases
            _set_amount(entry, float(row['Amount']))
            # A regular credit card purchase.  Defaults mostly fine.
            if row['Type'].lower() == "sale":
                entry['Payee']    = "" # leaving blank for now
            # Payment of statement balance.
            elif row['Type'].lower() == "payment":
                entry['Payee'] = "Transfer: %s" % CONFIG_CHASE["payment_account"]
                entry['Memo']  = "" # none needed
            # A refund of a purchase or fee.
            elif row['Type'].lower() == "refund":
                entry['Payee'] = CONFIG_MAIN["payee_you"]
            # Cash back
            elif row['Type'].lower() == "adjustment":
                entry['Payee'] = CONFIG_CHASE["payee_cash_back"]
                entry['Memo'] = "" # none needed
            # Late fee, foreign transaction fee, ...
            elif row['Type'].lower() == "fee":
                entry['Payee'] = CONFIG_CHASE['chase_payee']
                if row['Description'] == 'FOREIGN TRANSACTION FEE':
                    entry['Category'] = CONFIG_CHASE['chase_fees_category_foreign'] 
                else:
                    entry['Category'] = CONFIG_CHASE['chase_fees_category'] 
            # Anything else
            else:
                raise Exception("Category \"%s\" not recognized" % row['Type'])
            data.append(entry)
    return data

def main(args):
    parser = argparse.ArgumentParser(description=\
            "Converts external CSV data from multiple sources into YNAB's CSV import format",\
            epilog="Specify at least one of the input CSV files")
    parser.add_argument("--shopify-trans", help="Shopify transactions CSV file")
    parser.add_argument("--shopify-payouts", help="Shopify payouts CSV file")
    parser.add_argument("--chase", help="Chase credit card CSV file")
    parsed = parser.parse_args(args[1:])
    data = convert(**vars(parsed))
    write(sys.stdout, data)

if __name__ == "__main__":
    main(sys.argv)
