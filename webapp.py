#!/usr/bin/env python3
# encoding: utf-8
import os
import locale
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

from urllib.parse import urlsplit, urljoin
import yaml
from config.app import pdnskey, baseurl, host, appkey

import datetime

zone = os.environ['URL']
url = "%s/%s." % (baseurl,zone)

#from quittance import genonedoc

from flask import render_template, Flask, request, session

app = Flask(__name__)
#app.config['DEBUG'] = True

app.secret_key = appkey

from proxmoxer import ProxmoxAPI

def proxauth(content: dict) -> bool:

    try:
        myprox = ProxmoxAPI(host, user=content['login'], password=content['password'])
        return True

    except Exception as e:
        print("Can't login \n\t%s" % e)
        return False


def addrecord(content: dict) -> bool:
    
    import requests

    datenow = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if "delete" in content and content['delete']:
        changetype = "DELETE"
    else: 
        changetype = "REPLACE"
        content['delete'] = False
    
    payload = {
                "rrsets": [
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
                ]
            }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/2023.5.8",
        "X-API-Key": pdnskey
    }
    
    response = requests.request("PATCH", url, json=payload, headers=headers)

    print("Status code : ***%s***" % response.status_code)
    print(response.text)

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

                        print("%s :: %s " % (response,result))
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
                "url": os.environ['URL']
            }
            return render_template("./form.html", content=content)




if __name__ == "__main__":

    if os.path.exists("cert.pem") and os.path.exists("key.pem"):
        app.run(host='::',port=5000, debug=False, ssl_context=('cert.pem', 'key.pem'))
    else:
        app.run(host='::',port=5000, debug=False)
