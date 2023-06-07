#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/20 19:27
@Project:WeiboSpiderX
@File:run.py
@Desc:debug开发使用
"""
from scrapy import cmdline

if __name__ == '__main__':
    cmd = 'scrapy crawl weibo'
    # cmd = 'scrapy crawl refresh'
    cmdline.execute(cmd.split())
