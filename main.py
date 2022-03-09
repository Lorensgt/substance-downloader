import requests

import json
import os.path
from os import path
import re
import browser_cookie3

import sys


login_url = "https://share-legacy.substance3d.com/"

iCan = True
reconnections = 0
index = 1
canContinue = True

while iCan:
    get_title = lambda html: re.findall('<title>(.*?)</title>', html, flags=re.DOTALL)[0].strip()
    cj = browser_cookie3.firefox()
    url = 'https://share-legacy.substance3d.com/libraries/'+ str(index) + '/download_file/'
    print("\nTry on index " + str(index))
    r = requests.get(url, cookies=cj, stream=True)

    total_length = r.headers.get('content-length')
    print(r.headers)
    canContinue = True
    #pat = re.findall('(\"\w+)(\.\w+)', r.headers['Content-Disposition'])
    try:
        pat = re.findall('(\"\S+)(\.\w+)', r.headers['Content-Disposition'])
    except:
        canContinue = False
        reconnections += 1

    if canContinue:
        try:
            filename = ('').join(pat[0])[1:]
        except:
            filename = ('').join(pat)[1:]
        try:
            category = r.headers['x-amz-meta-allegorithmic-asset-category']
        except:
            category = "No Cat"

    if reconnections > 1500:
        iCan = False
        break

    if canContinue:
        size = r.headers['Content-Length']
        index += 1
        if len(category)< 1:
            category = "No Cat"

        print("Downloading " + filename + " Type " + category + " Size" + size + "bytes")
        reconnections = 0

        if not path.exists(category):
            os.mkdir(category)

        with open(os.path.join(category, filename), "wb") as f:

            if total_length is None:  # no content length header
                f.write(r.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in r.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
    else:
        index+=1





