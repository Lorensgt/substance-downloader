'''
Copyright (c) 2022 Llorenç Galmés

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import requests
import os.path
import re
import sys


login_url = "https://share-legacy.substance3d.com/user_session/new"
locin_url_post = "https://share-legacy.substance3d.com/user_session"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
	'X-CSRF-TOKEN': 'Fetch'
}

messages_text = {
    'user_log_text':'Enter your email:',
    'pass_log_text':'Enter your password:',
    'pass_index_text':'Enter start index of download. Default 1:',
    'founded_text':'Filename Founded:{} Type:{} Size:{} bytes',
    'download_text':'Downloading Filename:{} Type:{} Size:{} bytes',
    'download_prev':'This archive was downloaded previously',
    'error_password':'Check user/password',
    'error':'Error with connection',
    'error_nofile_found':'No file found',
    'intro':'This script will download all assets from https://share-legacy.substance3d.com in view of its imminent closure. \nMake a account (it\'s free for now). Login, and download. If you used this previously and you want start on another index, insert you desired input.'
}

print(messages_text["intro"])

user = input(messages_text["user_log_text"])
password = input(messages_text["pass_log_text"])
index = int(input(messages_text["pass_index_text"]))

run = True
s = requests.Session()
try:
    response = s.get(login_url, headers=headers)
    csrf_token = re.findall(r'[^\"\>\{\}\\]{86}==',
                            re.findall(r'name="csrf-token" content="[^\"\>\{\}\\]{86}==', response.text)[0])
    headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
    headers['content-type'] = 'application/x-www-form-urlencoded'
    payload = {
        'utf8': '✓',
        'authenticity_token': csrf_token[0],
        'destination': '',
        'session[email]': user,
        'session[password]': password,
        'commit': 'LOGIN'
    }

    response = s.post(locin_url_post, data=payload, headers=headers)

except:
    run = False
    print(messages_text["error"])


if len(re.findall("Sign-in failed! Please make sure your email and password are correct.",response.text))==0 and run:
    iCan = True
    reconnections = 0
    try:
        if int(index) < 1:
            index = 1
    except:
        index = 1

    canContinue = True
    while iCan:
        url = 'https://share-legacy.substance3d.com/libraries/'+ str(index) + '/download_file/'
        print("Try on https://share-legacy.substance3d.com/libraries/"+ str(index))
        r = s.get(url , stream=True)
        total_length = r.headers.get('content-length')
        canContinue = True
        #pat = re.findall('(\"\w+)(\.\w+)', r.headers['Content-Disposition'])
        try:
            pat = re.findall('(\"\S+)(\.\w+)', r.headers['Content-Disposition'])
        except:
            canContinue = False
            reconnections += 1
            print(messages_text["error_nofile_found"])

        if canContinue:
            try:
                filename = ('').join(pat[0])[1:]
            except:
                filename = ('').join(pat)[1:]
            try:
                category = r.headers['x-amz-meta-allegorithmic-asset-category']
            except:
                category = "No Category"

        if reconnections > 1500:
            iCan = False
            break

        if canContinue:
            size = r.headers['Content-Length']
            index += 1
            if len(category)< 1:
                 category = "No Category"
            print(messages_text["founded_text"].format(filename,category,size))
            reconnections = 0

            if not os.path.exists("Downloads"):
                os.mkdir("Downloads")

            if not os.path.exists(os.path.join("Downloads",category)):
                os.mkdir(os.path.join("Downloads",category))

            if not  (os.path.exists(os.path.join("Downloads",category,filename)) and os.path.getsize( os.path.join("Downloads",category,filename)) != size  ):
                print(messages_text["download_text"].format(filename, category, size))
                with open(os.path.join(os.path.join("Downloads",category), filename), "wb") as f:

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

                        print('\n')
            else:
                print(messages_text["download_prev"])
        else:
            index+=1
else:
    print(messages_text["error_password"])





