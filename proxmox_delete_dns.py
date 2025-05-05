#/usr/bin/env python3
# encoding: utf-8

import re, os
#import argsparse
import yaml
import json

import requests
from config.app import baseurl, pdnskey

zone = os.environ['ZONE']
url = "%s/%s." % (baseurl,zone)

payload = ""
headers = {
    "User-Agent": "insomnia/2023.5.8",
    "X-API-Key": pdnskey
}

def deletedns(record: dict) -> None:

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/2023.5.8",
        "X-API-Key": pdnskey
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

for record in data['rrsets']:

    if re.search(r'-[debian|rocky]',record['name']) and not re.search(r'javond',record['name']):
        deletedns(record)
    if re.search(r'\.web\.',record['name']) and not re.search(r'javond',record['name']):
        deletedns(record)
