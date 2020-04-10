'''
Barcode API interface for digikey and mouser

M.Holliday 2020
'''

import requests
import json
import os.path 
from os import path

oauth_headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}
oauth_body = {
    'client_id': "",
    'client_secret': "",
    'grant_type': 'refresh_token',
    'refresh_token': ''
}
app_headers = {
     "X-DIGIKEY-Client-Id": "",
    'authorization': "",
    'accept': "application/json"
    }

def printlevel(level,text):
    print('\t'*level+str(text))

class digikey:
    RECORDS_FILE = 'api_records_digi.txt'
    def __init__(self,cred,debug=False):
        self.DEBUG=debug
        self.barcode=''
        self.url2D="https://api.digikey.com/Barcoding/v3/Product2DBarcodes/".encode('utf-8')
        self.url1D="https://api.digikey.com/Barcoding/v3/ProductBarcodes/".encode('utf-8')
        self.urlProd="https://api.digikey.com/Search/v3/Products/".encode('utf-8')


        app_headers['X-DIGIKEY-Client-Id']=cred['client_id']
        oauth_body['client_id']=cred['client_id']
        oauth_body['client_secret']=cred['client_secret']
        self.setup_body = {k: cred[k] for k in ('code','client_id','client_secret')}
        printlevel(0,'Looking for local API records file in local directory...')
        if not path.exists('api_records_digi.txt'):
            printlevel(2,'No records found!')
            printlevel(2,'Running API setup...')
            if self.api_setup():
                printlevel(2,'API setup successful')
            else:
                printlevel(2,'API setup unsuccessful!')
                printlevel(2,'Must repeat OAuth approval step and try again with new authorization code')
                printlevel(3,'USE: https://api.digikey.com/v1/oauth2/authorize?response_type=code&client_id='+cred['client_id']+'&redirect_uri='+'https://localhost\n\n')
                raise Exception('New OAuth code required')
        else:
            printlevel(1,'Records file found...')
            try:
                with open(self.RECORDS_FILE,'r') as apidata:
                    for line in apidata:
                        if line.startswith('#'):
                            continue
                        else:
                            latest = json.loads(line)
                            latest_refresh_token=latest['refresh_token']
                            latest_access_token=latest['access_token']
                    oauth_body['refresh_token']=latest['refresh_token']
                    app_headers['authorization']= "Bearer "+latest['access_token']
            except Exception as e:
                printlevel(1,'Error loading/saving credentials to file: ',e)
    def api_setup(self):
        AUTH_URL="https://api.digikey.com/v1/oauth2/token".encode('utf-8')
        self.setup_body['grant_type']="authorization_code"
        self.setup_body['redirect_uri']="https://localhost"
        try:
            printlevel(2,'Sending authorization request...')
            x = requests.post(url=AUTH_URL, data=self.setup_body, headers=oauth_headers)
            response=x.json()
            if self.DEBUG: print(json.dumps(response,indent=3,sort_keys=True))
        except Exception as e:
            print('\tERROR during API setup - POST:',e)
            return False

        if 'ErrorMessage' not in response:
            printlevel(2,'Authorzation request successful')
            printlevel(2,'Creating new records file: api_records_digi.txt')
            try:
                printlevel(2,'Saving authorization credentials to file...')
                with open(self.RECORDS_FILE,'a') as apidata:
                    apidata.write(json.dumps(response,sort_keys=True))
                    apidata.write('\n')
                    return True
            except Exception as e:
                printlevel(2,'ERROR during API setup - SAVING step:',e)
                return False
        else:
            if 'Invalid authCode' in response['ErrorMessage']:
                printlevel(2,'ERROR during API setup - authorization code has expired')
            else:
                printlevel(2,'ERROR during API setup - Error message in POST')
            return False

    def refresh_token(self):
        print('Bearer token expired, attempting to refresh...')
        x = requests.post(url='https://api.digikey.com/v1/oauth2/token', data=oauth_body, headers=oauth_headers)
        data=x.json()
        print('New token:', data)
        with open(self.RECORDS_FILE,'a') as apidata:
            try:
                print('Before Refresh:')
                print('\t',oauth_body['refresh_token'])
                print('\t',app_headers['authorization'])
                apidata.write(json.dumps(data,sort_keys=True))
                apidata.write('\n')
                oauth_body['refresh_token']=data['refresh_token']
                app_headers['authorization']= "Bearer "+data['access_token']
                print('After Refresh:')
                print('\t',oauth_body['refresh_token'])
                print('\t',app_headers['authorization'])
                print('Updated Records File: {}\n'.format(self.RECORDS_FILE))
                return True
            except Exception as e:
                print('Refresh Error:',e)
                return False

    def barcode_search(self,barcode,barcode_type,product_info=False):
        if '2d' in barcode_type:
            baseurl=self.url2D
        else:
            baseurl=self.url1D
        self.barcode = barcode
        try:
            URL=baseurl+self.barcode
            r = requests.get(url=URL, headers=app_headers)
            api_response=r.json()
            api_response['Barcode']=self.barcode.decode()
            if 'ErrorMessage' in api_response:
                if 'Bearer token  expired' in api_response['ErrorMessage']:
                    if self.refresh_token():
                        r = requests.get(url=URL, headers=app_headers)
                        api_response=r.json()
                        api_response['Barcode']=self.barcode.decode()
                    else:
                        print('Fatal error during token refresh ')
                        return
            if product_info:
                try:
                    URL=self.urlProd+api_response["DigiKeyPartNumber"].encode('utf-8')
                    r = requests.get(url=URL, headers=app_headers)
                    api_response.update(r.json())
                except Exception as e:
                    print('Error during Product Info request:',e)
            print(json.dumps(api_response,indent=3,sort_keys=True))
            return api_response
        except Exception as e:
            print('Error during API request:',e)
            return


# READS FROM LATIN-1 ENCODED FILE
# import codecs
# with open('barcodes.csv','rb') as file:
#     for line in file:
#         QR.append(line.strip())