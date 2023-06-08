#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/6/8 00:16
@Project:WeiboSpiderX
@File:cache_user.py
@Desc:
"""
from WeiboSpiderX.bean.base import BaseItem


class CacheUserItem(BaseItem):
    def __init__(self):
        self._time = None
        self._user = None

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value


class CacheUser(BaseItem):

    def __init__(self):
        self._now = None
        self._list = []

    @property
    def now(self):
        return self._now

    @now.setter
    def now(self, value):
        self._now = value

    @property
    def list(self):
        return self._list

    @list.setter
    def list(self, value):
        self._list = value
