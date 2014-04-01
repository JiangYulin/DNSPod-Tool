#/usr/bin/env python2
#!coding: utf-8
# __author__ = 'jiangyulin'

import requests
import json
import types
from User import User

DomainListUrl = 'https://dnsapi.cn/Domain.List'
DomainDeleteUrl = "https://dnsapi.cn/Domain.Remove"
DomainCreateUrl = "https://dnsapi.cn/Domain.Create"
DomainRecordListUrl = "https://dnsapi.cn/Record.List"

def getalldomains(user):
    returnvalue = []
    try:
        r = requests.post(DomainListUrl, user.getparam())
    except requests.exceptions.RequestException as e:
        return False
    else:
        resultdata = json.loads(r.text)
        return resultdata

def get_domain_records(user, domain_id):  # if success, then return data else: return False
    returnvalue = []
    if type(domain_id) is types.IntType:
        new_param = user.getparam()
        new_param.update({
            'domain_id': domain_id
        })
    else:
        raise Exception("ParamTypeError")
    try:
        r = requests.post(DomainRecordListUrl, new_param)
    except requests.exceptions.RequestException as e:
        return False
    else:
        if r.status_code != 200:
            return False
        resultdata = json.loads(r.text)
        return resultdata

def delete_domain(user, domain_id):
    new_param = user.getparam()
    if types.IntType is not type(domain_id): #change
        raise Exception("ParamTypeError")
    new_param.update({
        'domain_id': domain_id
    })
    try:
        r = requests.post(DomainDeleteUrl, new_param)
    except requests.exceptions.RequestException as e:
        return
    else:
        if r.status_code != 200:
            return False
        resultdata = json.loads(r.text)
        return resultdata

def add_domain(user, domain_name):
    # domain_name is a QString which we need is Sting
    _domain_name = str(domain_name)
    new_param = user.getparam()
    new_param.update({
        'domain':_domain_name
    })
    try:
        r = requests.post(DomainCreateUrl, new_param)
    except requests.exceptions.RequestException as e:
        raise Exception("requestError")
    else:
        if r.status_code != 200:
            print r.status_code
            raise Exception("responseError")
        resultdata = json.loads(r.text)
        return resultdata
