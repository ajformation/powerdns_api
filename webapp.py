#!/usr/bin/env python3
# encoding: utf-8
import locale
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

from urllib.parse import urlsplit, urljoin
import yaml
from config.app import key, url, host, xapikey


#from quittance import genonedoc

from flask import render_template, Flask, request, session

app = Flask(__name__)

app.secret_key = key

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

    #url

    payload = {"rrsets": [
            {
                "name": "%s" % content['name'],
                "ttl": 3600,
                "changetype": "REPLACE",
                "type": "AAAA",
                "records": [
                    {
                        "content": "%s" % content['ipv6'],
                        "disabled": False
                    }
                ],
                "comments": [
                    {
                        "content": "%s" % content['login'],
                        "account": "%s" % content['login']
                    }
                ]
            }
        ]}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/2023.5.8",
        "X-API-Key": xapikey
    }
    
    #print(url)
    #print(payload)
    response = requests.request("PATCH", url, json=payload, headers=headers)

    print("Status code : ***%s***" % response.status_code)
    print(response.text)

    if response.status_code in [204,201] :

        return (response.status_code,True)

    else:

        return (response.text,False)



@app.route("/", methods=["GET", "POST"]) 
def home():
        #results = []

        #with open("locations.yaml") as file:
        #    locations = yaml.safe_load(file.read())
        #locations = list(locations.keys())

        if request.method == "POST":
                #debug = True if "debug" in request.form else False
                print(request.form)
                content = request.form.to_dict()

                if {'login','password'} <= content.keys():
                    myform = request.form
                    
                    #content = request.form
                    #content = **myform # type: ignore

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

                #else 'start' in request.form and 'end' in request.form:
                #    session['quittances'] = {
                #        'start': request.form['start'],
                #        'end': request.form['end'],
                #        'type': request.form['type'],
                #        'location': request.form['location'],
                ##       'paiement': request.form['paiement'],
                #
                #        'debug': request.form['debug'] if 'debug' in request.form else False,
                #    }
        else:
            return render_template("./form.html")#, content=content)




if __name__ == "__main__":
    #app.run(host='::',port=5000, debug=True)
    app.run(host='::',port=5000, debug=False)
#    app.run(host='0.0.0.0',port=5000, debug=True)
