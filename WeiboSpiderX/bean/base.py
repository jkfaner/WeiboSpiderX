#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/20 22:14
@Project:WeiboSpiderX
@File:base.py
@Desc:
"""
import json


class BaseItem(object):

    def to_dict(self):
        cleaned_dict = {}
        for key, value in self.__dict__.items():
            key = key[1:] if key.startswith('_') else key
            if isinstance(value, BaseItem):
                value = value.to_dict()
            elif isinstance(value, bytes):
                value = value.decode("utf-8")
            elif isinstance(value, list):
                _ = []
                for v in value:
                    if isinstance(v, BaseItem):
                        _.append(v.to_dict())
                    else:
                        _.append(v)
                value = _
            cleaned_dict[key] = value
        return cleaned_dict

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
