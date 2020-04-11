# Barcode scanner

Scan component bags (curren't just Digikey) and return product information. Uses Python3. Works for 2D data matrix QR codes and 1D barcodes.

- ![barcode_api.py](/barcode_api.py) handles all the API calls and refresh tokens (when necessary).
- ![barcode_scan.py](/barcode_scan.py) is an example using a webcam. There are lots of debug messages to help others troubleshoot their own scripts.

Some setup required. See 👇 for a guide setting up a Digikey API account and running the python script.
### ![Step-by-step Tutorial](/tutorial.md)

![images/demo.gif](images/demo.gif)

# Supplier Barcodes

- [ ] ✔ Digikey: DK provides a fully functional barcode API for product and invoice info. 👍 good job DK!
   - 2D: specific API exists for invoice and product info queries. QR code is data matrix format.<br>Always starts with `[)>`
   - 1D: specific API exists for invoice and product info queries. QR code is data matrix format.
- [ ] ➖ Mouser: There's a part number query API, but no native barcode searching. 
   - 2D: PN does appear to be stored as plain-text within the barcode. Need to look into doing some sort of regex to extra PN and invoice number. Always starts with `>[)>`
   - 1D: There's usually seperate 1D barcodes for `Cust PO`, `Line Items`, `Mouser P/N`, `MFG P/N`, `QTY`, `COO`, and `Invoice No`.
- [ ] ❌ LCSC: No API. 
   - 2D: I am starting to see QR codes on component bags (format is not data matrix like DK or Mouser... Maybe JSON?). My LCSC 2D barcodes have `productCode`, `orderNo`, `pickerNo`,`pickTime`, and `checkCode`. So far all I can do is search on LCSC for the product code. 
   - 1D: String ~10 characters in length. Can't extract anything useful from these.
