#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/27 11:37
@Project:WeiboSpiderX
@File:cookie.py
@Desc: TODO 需要重新实现
"""
import json
import logging

from DecryptLogin.modules import weibo
from requests.utils import dict_from_cookiejar
from scrapy.exceptions import IgnoreRequest

from WeiboSpiderX import constants


class HandleCookieMiddleware:
    is_login = False

    def __init__(self, uid, redis):
        self.logger = logging.getLogger(__name__)
        self.uid = uid
        self.redis = redis

    @classmethod
    def from_crawler(cls, crawler):
        uid = crawler.settings.get('SPIDER_UID')
        redis = crawler.spider.server
        return cls(uid, redis)

    def get_cookies(self):
        """
        获取cookie
        :return: 返回缓存中的Cookie
        """
        if self.redis.hexists(constants.LOGIN_KEY, self.uid):
            cookie = self.redis.hget(constants.LOGIN_KEY, self.uid)
            return json.loads(cookie)
        self.login()
        return self.get_cookies()

    def login(self):
        result, session = weibo().login()
        uid = result["uid"]
        if uid != self.uid:
            self.logger.error("当前登录用户与设置用户不一致！")
            raise Exception("当前登录用户与设置用户不一致！")
        cookie = dict_from_cookiejar(session.cookies)
        self.redis.hset(constants.LOGIN_KEY, self.uid, json.dumps(cookie))
        self.is_login = True
        self.logger.info("登录成功...")

    def process_response(self, request, response, spider):
        # 检查响应是否表示登录失败
        if self.cookie_failed(request, response):
            if not self.is_login:
                # 登录失败，重新登录
                self.login()

            if request.meta.get("url") != response.url:
                # 重新发送原始请求
                new_request = request.replace(url=request.meta.get("url"))
                new_request.dont_filter = True
                return new_request
            else:
                raise IgnoreRequest("URL filtered: {}".format(request.url))

        return response

    def process_request(self, request, spider):
        # 在请求中添加Cookie
        if request.meta.get("url"):
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
