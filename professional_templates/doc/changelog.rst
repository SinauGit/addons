.. _changelog:

Changelog
=========

`Version 1.5 (Sun Jun 28 10:52:53 2020)`
------------------------------------------
- `[FIX] Template settings page`
    - Fixed the reported issue where a user could not delete the watermark PDF after uploading because of overlapping.

`Version 1.4 (Wed Feb 19 01:18:19 2020)`
------------------------------------------
- `[FIX] invoice payment lines`
    - Removed lines that have cancelled payments

`Version 1.3 (Fri Jan 31 23:39:12 2020)`
------------------------------------------
- `[IMP] account journal`
    - Brought back `display_on_footer` field for bank accounts

- `[IMP] company footer`
    - Pagination is now global, whether you disabled or enabled footer it still appears

`Version 1.2 (Wed Dec 25 17:38:41 2019)`
-----------------------------------------
- Whats new?
  -- Fixed Odoo studio issue found  when editing sales order or invoice report

`Version 1.1 (Fri Dec  6 22:08:21 2019)`
-----------------------------------------
- Whats new?
  -- FIX in website, Error print or download invoice

`Version 1.0 ( 20 Sept 2019 18:05)`
------------------------------------
- Whats new?
  -- Introduced handling of exception for `Incorrect padding` errors.

`Version 0.7 ( 15 Jan 2019 14:44)`
----------------------------------
- Whats new?
  -- Fixed the error relating to printing PO with taxes, display currency issue.


`Version 0.6 ( 11 Jan 2019 12:24)`
----------------------------------
- Whats new?
  -- changed the base64 method for decoding PDF files from b64decode to urlsafe_b64decode

`Version 0.5 ( 24 Dec 2018)`
-----------------------------
- Whats new?
  -- Fixed the Item count bug which was miscounting items when Line Section or Line Note  is added.

`Version 0.4 (21 Dec 2018)`
--------------------------------
- Whats new?
  -- Fixed an Error in regards to printing 'Invoices Without Payment'

`Version 0.3 (27 NOV 2018)`
----------------------------
- Whats new?
  -- Included PRO-FORMA INVOICE as part of the customized reports.

`Version 0.2 (01 NOV 2018)`
----------------------------
- Whats new?
  -- Removed DUPLICATE reports since they are no longer part of standard Odoo reports.


`Version 0.1 (29 OCT 2018)`
-------------------------------
- New module for Odoo 12.0 ported from the same module for odoo 11.0 with same features and settings
