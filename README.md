# ynab-convert

A Python script to convert a few different financial CSV formats into [YNAB]'s
[CSV import format].  This works for me under YNAB 4 ("classic") but I don't
know how it behaves with their new web-based service.

This can read from any combination of:
 * Shopify's Transaction Export CSV
 * Shopify's Payouts Export CSV
 * Chase bank's Activity Export CSV

## Bugs and Limitations

 * Transfers are automatically categorized as income in YNAB for some reason.
   These can be filtered in YNAB with `Is:Error` and then fixed in bulk by
   setting Category to '(No Category)'.
 * Pending transactions should be marked un-cleared, if possible.
 * Again, no idea if this plays nicely with the new web-based YNAB.

## Export from Shopify

 1. Go to <https://myshopify.com/admin/payments/transactions>
 2. Click "Export" in the upper-right
   * Choose "Export payment transactions by date"
   * Choose "CSV for Excel, Numbers, and other spreadsheet programs"
 3. And also export from here: <https://rennes.myshopify.com/admin/payments/payouts>

## Export from Chase

 1. Log in and go to See Activity.
 2. Click "I'd Like To..." and choose "Download Activity."
 3. Choose appropriate date range.
 4. Choose CSV.
 5. Click "Download Activity."

## Convert

Optionally set up whatever text fields you want in `ynab_convert.ini`.  They
should be pretty self-explanatory.  Run the script giving the CSV filenames as
arguments, and direct the output to a new file.  Run `./ynab_convert.py -h` to
see all the options.

Example:

    ./ynab_convert.py --shopify-trans payment_transactions_export.csv --shopify-payouts payouts_export.csv > converted.csv

## Import in YNAB

Go to the account in YNAB and click the Import button.  Choose the CSV file
just created.  The defaults should be correct, but check the preview to be
sure.  After importing be sure to un-match any transactions YNAB has
incorrectly matched with existing ones.

[YNAB]: https://www.youneedabudget.com/
[CSV import format]: http://classic.youneedabudget.com/support/article/csv-file-importing
