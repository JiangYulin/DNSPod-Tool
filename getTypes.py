#!/usr/bin/env python2
#!coding:utf-8

__author__ = 'jiangyulin'

import requests
import json

import Dnspod as dns

RecordTypeUrl = "https://dnsapi.cn/Record.Type"
LineTypeUrl = "https://dnsapi.cn/Record.Line"

class DnsTypesDetail():
    def __init__(self, user, domain_grade , domain_id):
        """
        传入一个DNSpod实例，用来使用其中的用户信息
        并得到用户允许使用的记录类型
        """
        self.domain_id = domain_id
        self.param = user.getparam()
        self.param.update({
            'domain_grade': domain_grade,
        })


    def getRecordTypes(self):
        try:
            r = requests.post(RecordTypeUrl, self.param)
        except requests.exceptions.RequestException as e:
            self.__types = False
        else:
            if r.status_code != 200:
                self.__types = False
            else:
                result = json.loads(r.text)
                print result
                return result['types']

    def getLineTypes(self):
        new_param = self.param
        new_param.update({
            'domain_id':self.domain_id
        })
        try:
            r = requests.post(LineTypeUrl, new_param)
        except requests.exceptions.RequestException as e:
            return False
        else:
            if r.status_code !=200:
                self.__linetypes = False
            else:
                result = json.loads(r.text)
                print result
                return result['lines']
