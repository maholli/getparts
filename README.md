# What is getparts?

Getparts is a Python3 tool takes a supplier barcode value as an input and returns component information. Currently works for most Digi-Key, Mouser, and some LCSC bags.

## Barcode Status

Digi-Key
   - 2D: ✔
   - 1D: ✔

Mouser
   - 2D: ✔
   - 1D: ➖

LCSC
   - 2D: ✔
   - 1D: ❌

# Why?

Nearly every electrical component ordered online will be packaged and marked with a barcode containing relevant part information. Supplier-specific API are starting to emerge, but I needed a single tool that would retrieve part info from a variety of suppliers with and without search API. 

# How?

An example script is included that lets you use a webcam (laptop or usb webcam) to scan barcodes on component bags (Digikey, Mouser, and LCSC). This barcode value is fed into getparts which then tries a variety of techinques to retrieve the part information. Uses Python3. Works for 2D DataMatrix,  QR, and 1D barcodes.

Some setup required. See 👇 for a guide setting up a Digikey/Mouser API and running the python script.
### ![📃 Step-by-step Tutorial](/tutorial.md)

- ![getparts.py](/getparts.py) handles all the API calls and refresh tokens (when necessary).
- ![webcam_example.py](/webcam_example.py) is an example using a webcam. There are lots of debug messages to help others troubleshoot their own scripts.

# In Action

<p align="middle">
  <img width="700" src="images/demo.gif">
  <img width="300" src="https://user-images.githubusercontent.com/29153441/79077389-25e6db80-7cb6-11ea-9a7c-d49c9db015c4.png">
</p>

# Detailed Barcode Status

- [ ] Digikey: DK provides a fully functional barcode API for product and invoice info. 👍 good job DK!
   - ✔ 2D: specific API exists for invoice and product info queries. QR code is data matrix format.<br>Always starts with `[)>`
   - ✔ 1D: specific API exists for invoice and product info queries. QR code is data matrix format.
- [ ] Mouser: There's a part number query API, but no native barcode searching. 
   - ✔ 2D: PN is extracted from DataMatrix (always starts with `>[)>`) and searched using Mouser's API
   - ➖ 1D: Script can read the barcodes, but currently has no way of telling which barcode value correlates to which property because there are seperate 1D barcodes for `Cust PO`, `Line Items`, `Mouser P/N`, `MFG P/N`, `QTY`, `COO`, and `Invoice No`.
- [ ]  LCSC: No API. So we have to scrape.
   - ✔ 2D: Some of my LCSC bags have QR barcodes (1 in 10 I'd guess). The QR code contains: `productCode`, `orderNo`, `pickerNo`,`pickTime`, and `checkCode`. So far all the tool can do is search LCSC for the PN but the user needs to navigate the page and extract the info. Need to write a javascript web scraper. 
   - ❌ 1D: String ~10 characters in length. Can't extract anything useful from these.

This tool was developed to aid inventory management via [InvenTree](https://inventree.github.io/)
