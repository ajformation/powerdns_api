#/usr/bin/env python3
# encoding: utf-8

import re
#import argsparse
import yaml
import json

import requests
from config.app import url, xapikey

payload = ""
headers = {
    "User-Agent": "insomnia/2023.5.8",
    "X-API-Key": xapikey
}

def deletedns(record: dict) -> None:

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/2023.5.8",
        "X-API-Key": xapikey
    }
    payload = {"rrsets": [
        {
            "name": "%s" % record['name'],
            "changetype": "DELETE",
            "type": "AAAA"
        }
        ]}
    response = requests.request("PATCH", url, json=payload, headers=headers)
    if response.status_code:
        print("%s deleted" % record['name'])
        print("code : %s" % response.status_code)


response = requests.request("GET", url, data=payload, headers=headers)

data = json.loads(response.text)

#print(yaml.safe_dump(data))

for record in data['rrsets']:

    if re.search(r'-[debian|rocky]',record['name']) and not re.search(r'javond',record['name']):
        deletedns(record)
    if re.search(r'\.web\.',record['name']) and not re.search(r'javond',record['name']):
        deletedns(record)


#import requests
#
#url = "http://ns1.cfai2024.ajformation.fr:8081/api/v1/servers/localhost/zones/cfai24.ajformation.fr."
#


#
#response = requests.request("PATCH", url, json=payload, headers=headers)
#
#print(response.text)