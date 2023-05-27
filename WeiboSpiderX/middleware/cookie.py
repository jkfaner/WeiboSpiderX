#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/27 11:37
@Project:WeiboSpiderX
@File:cookie.py
@Desc:
"""
import json
import sys

from DecryptLogin.modules import weibo
from requests.utils import dict_from_cookiejar

from WeiboSpiderX import constants


class HandleCookieMiddleware:

    def __init__(self, uid, redis, apis):
        self.uid = uid
        self.redis = redis
        self.api_list = apis

    @classmethod
    def from_crawler(cls, crawler):
        uid = crawler.settings.get('SPIDER_UID')
        redis = crawler.spider.server
        apis = crawler.spider.api_list
        return cls(uid, redis, apis)

    def get_cookies(self):
        """
        获取cookie
        :return: 返回缓存中的Cookie
        """
        if self.redis.hexists(constants.LOGIN_KEY, self.uid):
            cookie = self.redis.hget(constants.LOGIN_KEY, self.uid)
            return json.loads(cookie)
        return {}

    def login(self):
        result, session = weibo().login()
        uid = result["uid"]
        if uid != self.uid:
            sys.exit("当前登录用户与设置用户不一致！")
        cookie = dict_from_cookiejar(session.cookies)
        self.redis.hset(constants.LOGIN_KEY, self.uid, json.dumps(cookie))

    def process_response(self, request, response, spider):
        # 检查响应是否表示登录失败
        if self.cookie_failed(request, response):
            # 登录失败，重新登录
            self.login()

            # 重新发送原始请求
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request

        return response

    def process_request(self, request, spider):
        # 在请求中添加Cookie
        request.cookies = self.get_cookies()

    @staticmethod
    def cookie_failed(request, response):
        """
        根据请求的URL、响应内容等判断是否需要登录
        :param request:
        :param response:
        :return: 返回True表示需要登录，False表示无需登录
        """
        url = request.meta.get("url")
        if url:
            if url != response.url:
                return True

        return False
