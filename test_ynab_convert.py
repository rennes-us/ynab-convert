#!/usr/bin/env python
import unittest
import ynab_convert
import csv

inputs = {}
inputs['shopify_trans'] = 'data/payment_transactions_export.csv'
inputs['shopify_payouts'] = 'data/payouts_export.csv'
inputs['chase'] = 'data/chase.csv'

with open('data/all_converted.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    original = [row for row in reader]

class TestYnabConvert(unittest.TestCase):

    def test_convert(self):
        data = ynab_convert.convert(**inputs)
        self.assertEqual(data, original)

if __name__ == '__main__':
    unittest.main()
