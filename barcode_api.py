'''
Python3

API tool for electronic component suppliers (digikey, mouser, LCSC)
https://github.com/maholli/barcode-scanner
M.Holliday
'''

import requests
import json, re
import os.path 
from os import path
from types import SimpleNamespace
from requests_html import HTMLSession
from bs4 import BeautifulSoup
oauth_headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}
oauth_body = {
    'client_id': "",
    'client_secret': "",
    'grant_type': 'refresh_token',
    'refresh_token': ''
}
digi_headers = {
     "X-DIGIKEY-Client-Id": "",
    'authorization': "",
    'accept': "application/json"
}
mouser_headers = {
    'Content-Type': "application/json",
    'accept': "application/json"
}

def printlevel(level,text):
    print('\t'*level+str(text))

class barcode:
    RECORDS_FILE = 'api_records_digi.txt'
    def __init__(self,cred,debug=False):
        self.DEBUG=debug
        self.digi2D="https://api.digikey.com/Barcoding/v3/Product2DBarcodes/".encode('utf-8')
        self.digi1D="https://api.digikey.com/Barcoding/v3/ProductBarcodes/".encode('utf-8')
        self.digiPN="https://api.digikey.com/Search/v3/Products/".encode('utf-8')
        self.mouserPN="https://api.mouser.com/api/v1/search/partnumber?apiKey=".encode('utf-8')
        self.barcode=SimpleNamespace()
        self.query=SimpleNamespace()
        self.query.suppliers={
            'digikey':{
                '1D':lambda:requests.get(url=self.digi1D+self.barcode.barcode, headers=digi_headers),
                '2D':lambda:requests.get(url=self.digi2D+self.barcode.barcode, headers=digi_headers),
                'pn':lambda:requests.get(url=self.digiPN+self.barcode.response['DigiKeyPartNumber'].encode(),headers=digi_headers),
            },
            'mouser':{
                '1D':lambda:print('mouser1d'),
                '2D':lambda:requests.post(url=self.mouserPN+cred['mouser_key'].encode('utf-8'),data=self.barcode.mfpn.encode(), headers=mouser_headers),
            },
            'lcsc':{
                '1D':lambda:print('lcsc1d'),
                '2D':lambda:lcsc.scrape(self.barcode.supplierPN),
            }
        }

        digi_headers['X-DIGIKEY-Client-Id']=cred['client_id']
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
                    digi_headers['authorization']= "Bearer "+latest['access_token']
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
                print('\t',digi_headers['authorization'])
                apidata.write(json.dumps(data,sort_keys=True))
                apidata.write('\n')
                oauth_body['refresh_token']=data['refresh_token']
                digi_headers['authorization']= "Bearer "+data['access_token']
                print('After Refresh:')
                print('\t',oauth_body['refresh_token'])
                print('\t',digi_headers['authorization'])
                print('Updated Records File: {}\n'.format(self.RECORDS_FILE))
                return True
            except Exception as e:
                print('Refresh Error:',e)
                return False

    def search(self,scan,product_info=False):
        # Determine barcode type and supplier
        self.barcode.barcode=scan.data
        if self.DEBUG: print(scan)
        try:
            if 'QRCODE' in scan.type:
                self.barcode.type='2D'
                self.barcode.supplier='lcsc'
                supPN=re.split(r",",self.barcode.barcode.decode())
                self.barcode.supplierPN=supPN[1][12:]
            elif 'CODE128' in scan.type:
                self.barcode.type='1D'
                if self.barcode.barcode.decode().isdecimal():
                    if len(self.barcode.barcode) > 10:
                        self.barcode.supplier='digikey'
                    else:
                        print("Short barcode... possibly Mouser Line Item or QTY: ".format(self.barcode.barcode.decode()))
                else:
                    self.barcode.supplier='mouser'
            else:
                print('Unknown supplier')
        except AttributeError:
            self.barcode.type='2D'
            if b'>[)>' in self.barcode.barcode:
                self.barcode.supplier='mouser'
                mfgpart=re.split(r"",self.barcode.barcode.decode())
                print('mfgpart:',mfgpart)
                if '1P' in mfgpart[3]:
                    self.barcode.mfpn="{\"SearchByPartRequest\": {\"mouserPartNumber\": \""+mfgpart[3][2:]+"\",}}"
            else:
                self.barcode.supplier='digikey'

        # make supplier-specific API query 
        try:
            r=self.query.suppliers[self.barcode.supplier][self.barcode.type]()
            self.barcode.response=r.json()
            if 'ErrorMessage' in self.barcode.response:
                if 'Bearer token  expired' in self.barcode.response['ErrorMessage']:
                    if self.refresh_token():
                        r=self.query.suppliers[self.barcode.supplier][self.barcode.type]()
                        self.barcode.response=r.json()
                    else:
                        print('Fatal error during token refresh ')
                        return
            if product_info:
                self.barcode.type='pn'
                try:
                    r=self.query.suppliers[self.barcode.supplier][self.barcode.type]()
                    self.barcode.response.update(r.json())
                except Exception as e:
                    print('Error during Product Info request:',e)
            print(json.dumps(self.barcode.response,indent=3,sort_keys=True))
            return self.barcode
        except Exception as e:
            print('Error during API request:',e)
            if self.DEBUG:print('Attributes: {}'.format(self.barcode))
            return
class lcscdata:
    def __init__(self,val):
        self.value=val
    def json(self):
        return self.value
class lcsc:
    def scrape(pn):
        lcscPN=pn
        # create an HTML Session object
        session = HTMLSession()
        # Use the object above to connect to needed webpage
        r1 = session.get("https://lcsc.com/search?q="+lcscPN)
        # Run any JavaScript code on webpage
        r1.html.render()
        # Find absolute link for product page
        a=r1.html.find('body > div#lcsc.push-body > div#global_search.contianer > div.table-content > section > div > div#product_table_list > div.product-list-area.table-area > table')
        links=a[0].absolute_links
        for link in links:
            if lcscPN+'.html' in link:
                product_page=link
        # Load product page
        direct=session.get(product_page)
        soup = BeautifulSoup(direct.html.html, "lxml")
        # Find correct product table
        table=soup.find('table', attrs={'class':'products-specifications'}) # 2nd table
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        result=lcscdata({})
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            line=[ele for ele in cols if ele]
            try:
                result.value.update({line[0]:line[1]})
            except:
                pass
        return result