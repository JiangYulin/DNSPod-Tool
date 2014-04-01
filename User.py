#!/usr/bin/evn python2
#!coding:utf-8
__author__ = 'jiangyulin'

import requests
import json
UserDetailUrl = "https://dnsapi.cn/User.Detail"


class User():
    def __init__(self, login_email, login_password):
        self.__logined = False
        self.__login_email = login_email
        self.__login_password = login_password
        self.__status = ''
        self.__veryfy()

    def __veryfy(self):
        UserDetailUrl = "https://dnsapi.cn/User.Detail"
        param = {'login_email': self.__login_email, 'login_password': self.__login_password, 'format': 'json'}
        print param
        r = requests.post(UserDetailUrl, data=param)
        print param
        if r.status_code == 200:
            resultData = json.loads(r.text)
            if resultData['status']['code'] == '1':
                self.__logined = True
            else:
                self.__status = resultData['status']

    def logined(self):
        return self.__logined

    def getstatus(self):
        return self.__status

    def getparam(self):
        return {
            'login_email': self.__login_email,
            'login_password': self.__login_password,
            'format': 'json'
        }
