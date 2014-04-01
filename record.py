#!/usr/bin/env python2
import requests
import json
import User

RecordCreateUrl = "https://dnsapi.cn/Record.Create"
RecordModifyUrl = "https://dnsapi.cn/Record.Modify"
RecordDeleteUrl = "https://dnsapi.cn/Record.Remove"


class Record():
    def __init__(self, user, param):
        """
        param : {
        'domain_id':
        'record_id':
        'sub_domain';
        'record_type':
        'record_line':
        'value':
        'mx':optional
        'ttl':optional
        }
        """
        self.__record = {}
        self.__status = []
        self.__record = param
        if param.has_key('id'):
            self.__record['record_id'] = param['id']
        if param.has_key('type'):
            self.__record['record_type'] = param['type']
        if param.has_key('line'):
            self.__record['record_line'] = param['line']
        if param.has_key('name'):
            self.__record['sub_domain'] = param['name']
        self.__user = user

    def save(self):
        new_param = self.__user.getparam()
        new_param.update(self.__record)
        if self.__record.has_key("record_id") is False:
            url = RecordCreateUrl
        else:
            url = RecordModifyUrl
        r = requests.post(url, new_param)
        result = json.loads(r.text)
        if result['status']['code'] == '1':
            return True
        else:
            self.__status = result['status']
            return False

    def delete(self):
        if self.__record.has_key("record_id") is True:
            new_param = self.__user.getparam()
            new_param.update({
                'record_id':self.__record['record_id'],
                'domain_id':self.__record['domain_id']
            })
            print new_param
            r = requests.post(RecordDeleteUrl, new_param)
            if r.status_code == 200:
                result = json.loads(r.text)
                print result
                if result['status']['code'] == "1":
                    return True
                else:
                    return result['status']
            else:
                return {
                    'message': r.status_code
                }
        else:
            return {
                'message':''
            }

    def getstatus(self):
        return self.__status