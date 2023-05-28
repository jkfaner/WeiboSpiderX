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
from abc import ABC, abstractmethod


class BaseItem(ABC):

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError("子类必须实现to_dict()方法")

    @abstractmethod
    def to_json(self):
        raise NotImplementedError("子类必须实现to_json()方法")