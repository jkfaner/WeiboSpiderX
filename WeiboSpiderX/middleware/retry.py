#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/27 11:37
@Project:WeiboSpiderX
@File:retry.py
@Desc:
"""
import logging
import time

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message


class TooManyRequestsRetryMiddleware(RetryMiddleware):

    def __init__(self, crawler):
        super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if response.status == 414:
            self.logger.info("[{}]当前请求：{}".format(response.status,response.url))
            self.crawler.engine.pause()
            time.sleep(60 * 2)  # If the rate limit is renewed in a minute, put 60 seconds, and so on.
            self.crawler.engine.unpause()
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            self.logger.info("[{}]当前请求：{}".format(response.status, response.url))
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response