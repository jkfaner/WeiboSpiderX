#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/6/7 21:01
@Project:WeiboSpiderX
@File:aop.py
@Desc:
"""
import functools


class ScrapyLogger:
    def __init__(self, start=None, end=None):
        if end is None:
            end = {}
        if start is None:
            start = {}
        self.start = start
        self.end = end

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            spider = args[0]

            start_info = self.start.get("info")
            start_error = self.start.get("error")

            end_info = self.end.get("info")
            end_error = self.end.get("error")

            if start_info:
                spider.logger.info(start_info)
            elif start_error:
                spider.logger.error(start_error)

            result = func(*args, **kwargs)

            if end_info:
                spider.logger.info(end_info)
            elif end_error:
                spider.logger.error(end_error)

            return result

        return wrapper
