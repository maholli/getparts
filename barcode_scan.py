'''
Python3

Example barcode scanner and DigiKey API helper
https://github.com/maholli/barcode-scanner
'''

from pyzbar import pyzbar
from pylibdmtx import pylibdmtx
import time
import cv2, codecs
import numpy as np
import barcode_api
import os.path 
from os import path

# Update these following the guide on github (linked above)
app_credentials= {
    'code': 'AAA',
    'client_id': "BBB",
    'client_secret': "CCC"
}

api = barcode_api.digikey(app_credentials)
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
print("Warming webcam for 2 seconds...")
time.sleep(2)

# Webcam-specific tweaks
vs.set(cv2.CAP_PROP_FRAME_WIDTH , 640)
vs.set(cv2.CAP_PROP_FRAME_HEIGHT , 480)
vs.set(cv2.CAP_PROP_BRIGHTNESS, 120)
vs.set(cv2.CAP_PROP_CONTRAST, 170)
vs.set(cv2.CAP_PROP_SATURATION, 0)
vs.set(cv2.CAP_PROP_HUE, 13)
vs.set(cv2.CAP_PROP_GAIN, 40)
vs.set(cv2.CAP_PROP_EXPOSURE, -6) # min: -7  , max: -1  , increment:1
vs.set(cv2.CAP_PROP_TEMPERATURE, 5000)
vs.set(cv2.CAP_PROP_FOCUS, 240) # min: 0   , max: 255 , increment:5


state='Searching'
# loop over the frames from the video stream
while True:
    _,frame2 = vs.read()
    barcodes = pylibdmtx.decode(frame2,timeout=10)
    if barcodes:
        # loop over the detected barcodes
        for barcode in barcodes:
            barcodeData = barcode.data
            if barcodeData not in found:
                state='Found'
                result = api.barcode_search(barcodeData,barcode_type='2d',product_info=False)
                found.add(barcodeData)
                with codecs.open(barcodefile,'w', encoding='latin-1') as file:
                    file.write('{}\n'.format(codecs.decode(barcodeData,'latin-1')))
                    file.flush()
            else:
                state='Duplicate'
    else:
        bar1d=pyzbar.decode(frame2)
        if bar1d:
            state='Found'
            barcodeData = bar1d[0].data
            if barcodeData not in found:
                result = api.barcode_search(barcodeData,barcode_type='1d',product_info=False)
                found.add(barcodeData)
                with codecs.open(barcodefile,'w', encoding='latin-1') as file:
                    file.write('{}\n'.format(codecs.decode(barcodeData,'latin-1')))
                    file.flush()
        else:
            state='Searching'

    # show the output frame
    cv2.putText(frame2,str(state),(10,10),cv2.FONT_HERSHEY_SIMPLEX,0.5,states[state],2,cv2.LINE_AA)
    cv2.imshow("Barcode Scanner", frame2)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
