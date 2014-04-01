#!/usr/bin/env python2
#!coding:utf-8

import json
import requests

DomainListUrl = 'https://dnsapi.cn/Domain.List'
DomainDeleteUrl = "https://dnsapi.cn/Domain.Remove"
DomainCreateUrl = "https://dnsapi.cn/Domain.Create"
DomainRecordListUrl = "https://dnsapi.cn/Record.List"
DomainInfoUrl = "https://dnsapi.cn/Domain.Info"


class Domain():
    def __init__(self, user, param):
        """
        'name':
        'id':optianl
        """
        self.__domain_detail = {}
        self.__status = {}
        self.user = user
        if param.has_key('id'):
            self.__getinfo(param['id'])
        else:
            self.__domain_detail = {
                'domain': param['name'],
                'name': param['name']
            }

    def save(self):
        if self.__domain_detail.has_key('id'):
            self.__status = {
                'message': 'save can not with a value called id'
            }
            return False
        new_param = self.user.getparam()
        new_param.update({
            'domain': self.__domain_detail['domain']
        })
        try:
            r = requests.post(DomainCreateUrl, new_param)
        except requests.exceptions.RequestException as e:
            self.__status = {
                'message': 'Requests Error'
            }
            return False
        else:
            if r.status_code != 200:
                self.__status = {
                    'message': 'Http Error'
                }
                return False
            resultdata = json.loads(r.text)
            if resultdata['status']['code'] == '1':
                self.__domain_detail['id'] = resultdata['domain']['id']
                return True
            else:
                self.__status = resultdata['status']
                return False

    def __getinfo(self, domain_id):
        new_param = self.user.getparam()
        new_param.update({
            'domain_id':domain_id
        })
        try:
            r = requests.post(DomainInfoUrl, new_param)
        except requests.exceptions.RequestEXceptions as e:
            raise Exception("requestError")
        else:
            if r.status_code != 200:
                raise Exception("responseError")
            resultdata = json.loads(r.text)
            self.__domain_detail = resultdata['domain']

    def getid(self):
        if self.__domain_detail.has_key('id'):
            return self.__domain_detail['id']
        else:
            return None

    def getgrade(self):
        if self.__domain_detail.has_key('grade'):
            return self.__domain_detail['grade']
        else:
            return None

    def getallrecords(self):
        new_param = self.user.getparam()
        new_param.update({
            'domain_id': self.__domain_detail['id']
        })
        try:
            r = requests.post(DomainRecordListUrl, new_param)
        except requests.exceptions.RequestException as e:
            self.__status = {
                'message': e.strerror
            }
            return False
        else:
            if r.status_code != 200:
                self.__status = {
                    'message': "Response Error"
                }
                return False
            resultdata = json.loads(r.text)
            if resultdata['status']['code'] != '1':
                self.__status = resultdata['status']
                return False
            else:
                return resultdata

    def getstatus(self):
        return self.__status

