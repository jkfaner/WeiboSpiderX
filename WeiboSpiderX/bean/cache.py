#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/27 19:01
@Project:WeiboSpiderX
@File:cache.py
@Desc:
"""

from WeiboSpiderX.bean.base import BaseItem


class CacheItem(BaseItem):

    def __init__(self):
        self._is_end = False
        self._total = None
        self._last_total = None
        self._real_total = 0
        self._uid = None
        self._blog_ids = []

    @property
    def last_total(self):
        return self._last_total

    @last_total.setter
    def last_total(self, value):
        self._last_total = value

    @property
    def is_end(self):
        return self._is_end

    @is_end.setter
    def is_end(self, value):
        self._is_end = value

    @property
    def real_total(self):
        return self._real_total

    @real_total.setter
    def real_total(self, value):
        self._real_total = value

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, value):
        self._total = value

    @property
    def blog_ids(self):
        return self._blog_ids

    @blog_ids.setter
    def blog_ids(self, value):
        self._blog_ids = value