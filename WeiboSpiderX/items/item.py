#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/24 23:38
@Project:WeiboSpiderX
@File:item.py
@Desc:
"""
import json

from WeiboSpiderX.items.base import BaseItem


class RequestMeta(BaseItem):

    def __init__(self):
        self._url = None
        self._raw_url = None
        self._params = None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def raw_url(self):
        return self._raw_url

    @raw_url.setter
    def raw_url(self, value):
        self._raw_url = value

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value

    def to_dict(self):
        obj_dict = self.__dict__
        cleaned_dict = {}
        for key, value in obj_dict.items():
            if key.startswith('_'):
                key = key[1:]
            cleaned_dict[key] = value
        return cleaned_dict

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)


class RequestParam(BaseItem):

    def __init__(self):
        self._url = None
        self._cookies = None
        self._meta = None
        self._callback = None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, value):
        self._cookies = value

    @property
    def meta(self):
        return self._meta

    @meta.setter
    def meta(self, value):
        self._meta = value

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        self._callback = value

    def to_dict(self):
        obj_dict = self.__dict__
        cleaned_dict = {}
        for key, value in obj_dict.items():
            if key.startswith('_'):
                key = key[1:]
            cleaned_dict[key] = value
        return cleaned_dict

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
