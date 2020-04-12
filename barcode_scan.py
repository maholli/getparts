'''
Python3

Example barcode scanner for electronic component suppliers (digikey, mouser, LCSC)
https://github.com/maholli/barcode-scanner
M.Holliday
'''

from pyzbar import pyzbar
from pylibdmtx import pylibdmtx
import time
import cv2, codecs
import numpy as np
import barcode_api
import os.path 
from os import path

app_credentials= {
    'code': 'AAA',
    'client_id': "BBB",
    'client_secret': "CCC",
    'mouser_key': "DDD"
}

# initialize barcode_api with our API credentials
api = barcode_api.barcode(app_credentials,debug=False)
state='Searching'
states={
    'Searching':(0,0,255),
    'Found':(0,255,0),
    'Duplicate':(0,165,255),
}

# File to save barcodes
barcodefile='barcodes.txt'
found = set()
poly=np.array([[[0,0],[0,0],[0,0],[0,0]]],np.int32)

# initialize the video stream and allow the camera sensor to warm up
print("Starting video stream...")
vs=cv2.VideoCapture(0)
if vs is None or not vs.isOpened():
    raise TypeError('Error starting video stream\n\n')

while True:
    code=False
    # read frame from webcam
    _,frame2 = vs.read()
    # check for a data matrix barcode
    barcodes = pylibdmtx.decode(frame2,timeout=10)
    if barcodes:
        code=True
    # if no data matrix, check for any other barcodes
    else:
        barcodes=pyzbar.decode(frame2)
        if barcodes:
            code=True
    if code:
        for item in barcodes:
            barcodeData = item.data
            # find and draw barcode outline
            try:
                pts=[]
                [pts.append([i.x,i.y]) for i in item.polygon]
                poly=np.array([pts],np.int32)
                cv2.polylines(frame2, [poly], True, (0,0,255),2)
            except AttributeError:
                # data matrix
                (x, y, w, h) = item.rect
                cv2.rectangle(frame2,(x,y),(x+w, y+h),(0,0,255),2)
            # if we haven't seen this barcode this session, add it to our list
            if barcodeData not in found:
                state='Found'
                found.add(barcodeData)
                print(barcodeData.decode())
                # query the barcode_api.py for barcode
                result = api.search(item,product_info=False)
                with codecs.open(barcodefile,'a', encoding='latin-1') as file:
                    file.write('{}\n'.format(codecs.decode(barcodeData,'latin-1')))
                    file.flush()
            else:
                state='Duplicate'
        code=False
    else:
        state='Searching'
    # update the video stream window
    cv2.putText(frame2,str(state),(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.5,states[state],2,cv2.LINE_AA)
    cv2.imshow("Barcode Scanner", frame2)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

print("[INFO] cleaning up...")
cv2.destroyAllWindows()
