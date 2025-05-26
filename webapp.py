#!/usr/bin/env python3
# encoding: utf-8
import os
import locale
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

from urllib.parse import urlsplit, urljoin
import yaml
from config.app import pdnskey, baseurl, host, appkey

import datetime
import curlify

if 'ZONE' not in os.environ:
    raise ValueError("Environment variable 'ZONE' is not set")
    exit(1)
if 'PORT' not in os.environ:
    raise ValueError("Environment variable 'PORT' is not set")
    exit(1)

if 'DEBUG' not in os.environ:
    os.environ['DEBUG'] = 'False'
else:
    if os.environ['DEBUG'] == 'True':
        os.environ['DEBUG'] = 'True'
    else:
        os.environ['DEBUG'] = 'False'

zone = os.environ['ZONE']
port = os.environ['PORT']
debug = os.environ['DEBUG']

url = "%s/%s." % (baseurl,zone)

#from quittance import genonedoc

from flask import render_template, Flask, request, session # type: ignore

app = Flask(__name__)
#app.config['DEBUG'] = True

app.secret_key = appkey

from proxmoxer import ProxmoxAPI

def proxauth(content: dict) -> bool:

    try:
        myprox = ProxmoxAPI(host, user=content['login'], password=content['password'])
        return True

    except Exception as e:
        app.logger.error("Proxmox authentication failed: %s" % e)
        #print("Can't login \n\t%s" % e)
        return False


def addrecord(content: dict) -> bool:
    
    import requests

    datenow = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if "delete" in content and content['delete']:
        changetype = "DELETE"
    else: 
        changetype = "REPLACE"
        content['delete'] = False
    
    
    content['txt'] = '"%s -- %s"' % (content['login'],datenow)
    rrsets = []

    rrsets.append(
            {
                "name": "%s" % content['name'],
                "ttl": 3600,
                "changetype": changetype,
                "type": "TXT",
                "records": [
                    {
                        "content": content['txt'],
                        "disabled": False
                    }
                ],
                "comments": [
                    {
                        "content": "domain %s --- user %s" % (content['name'], content['login']),
                        "account": "%s" % content['login'],
                        "date": "%s" % datenow
                    }
                ]
            }
    )
    
    if 'ipv4' in content and content['ipv4']:

        rrsets.append(
            {
                "name": "%s" % content['name'],
                "ttl": 3600,
                "changetype": changetype,
                "type": "A",
                "records": [
                    {
                        "content": "%s" % content['ipv4'],
                        "disabled": False
                    }
                ],
                "comments": [
                    {
                        "content": "domain %s --- ipv4 %s : action %s" % (content['name'], content['ipv6'], changetype),
                        "account": "%s" % content['login'],
                        "date": "%s" % datenow
                    }
                ]
            }
        )

    if 'ipv6' in content and content['ipv6']:

        rrsets.append(
            {
                "name": "%s" % content['name'],
                "ttl": 3600,
                "changetype": changetype,
                "type": "AAAA",
                "records": [
                    {
                        "content": "%s" % content['ipv6'],
                        "disabled": False
                    }
                ],
                "comments": [
                    {
                        "content": "domain %s --- ipv6 %s : action %s" % (content['name'], content['ipv6'], changetype),
                        "account": "%s" % content['login'],
                        "date": "%s" % datenow
                    }
                ]
            }
        )

    payload = { "rrsets": rrsets }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/2023.5.8",
        "X-API-Key": pdnskey
    }
    
    response = requests.request("PATCH", url, json=payload, headers=headers)
    app.logger.info('Curl request : %s ' % curlify.to_curl(response.request))

    app.logger.info("Status code : ***%s***" % response.status_code)
    app.logger.info("Response : ***%s***" % response.text)


    if response.status_code in [204,201] :

        return (response.status_code,True)

    else:

        return (response.text,False)



@app.route("/", methods=["GET", "POST"]) 
def home():

        if request.method == "POST":
                content = request.form.to_dict()

                if {'login','password'} <= content.keys():
                    myform = request.form

                    if proxauth(content=content):

                        response,result=addrecord(content=content)
                        
                        app.logger.info("Response : %s" % response)
                        app.logger.info("Result : %s" % result)
                        
                        if result:
                            return render_template("./done.html", content=content)
                        else:
                            content['error_cause'] = "DNS"
                            content['dns_cause'] = response
                            return render_template("./error.html", content=content)


                    else:
                        content['error_cause'] = "AUTH"
                        return render_template("./error.html", content=content)

        else:
            content = {
                "zone": os.environ['ZONE']
            }
            return render_template("./form.html", content=content)




if __name__ == "__main__":

    # debug = False
    # debug = True

    if os.path.exists("cert.pem") and os.path.exists("key.pem"):
        app.run(host='::',port=port, debug=debug, ssl_context=('cert.pem', 'key.pem'))
    else:
        app.run(host='::',port=port, debug=debug)
