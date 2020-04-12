# Barcode scanner

Scan electrical component bags (Digikey, Mouser, and LCSC) and return product information. Uses Python3. Works for 2D DataMatrix,  QR, and 1D barcodes.

- ![barcode_api.py](/barcode_api.py) handles all the API calls and refresh tokens (when necessary).
- ![barcode_scan.py](/barcode_scan.py) is an example using a webcam. There are lots of debug messages to help others troubleshoot their own scripts.

Some setup required. See 👇 for a guide setting up a Digikey/Mouser API and running the python script.
### ![📃 Step-by-step Tutorial](/tutorial.md)

# In Action

<p align="middle">
  <img width="500" src="images/demo.gif">
  <img width="200" src="https://user-images.githubusercontent.com/29153441/79077389-25e6db80-7cb6-11ea-9a7c-d49c9db015c4.png">
</p>

# Supplier Barcodes

- [ ] Digikey: DK provides a fully functional barcode API for product and invoice info. 👍 good job DK!
   - ✔ 2D: specific API exists for invoice and product info queries. QR code is data matrix format.<br>Always starts with `[)>`
   - ✔ 1D: specific API exists for invoice and product info queries. QR code is data matrix format.
- [ ] Mouser: There's a part number query API, but no native barcode searching. 
   - ✔ 2D: PN is extracted from DataMatrix (always starts with `>[)>`) and searched using Mouser's API
   - ➖ 1D: Script can read the barcodes, but currently has no way of telling which barcode value correlates to which property because there are seperate 1D barcodes for `Cust PO`, `Line Items`, `Mouser P/N`, `MFG P/N`, `QTY`, `COO`, and `Invoice No`.
- [ ]  LCSC: No API. 
   - ➖ 2D: Some of my LCSC bags have QR barcodes (1 in 10 I'd guess). The QR code contains: `productCode`, `orderNo`, `pickerNo`,`pickTime`, and `checkCode`. So far all the tool can do is search LCSC for the PN but the user needs to navigate the page and extract the info. Need to write a javascript web scraper. 
   - ❌ 1D: String ~10 characters in length. Can't extract anything useful from these.
