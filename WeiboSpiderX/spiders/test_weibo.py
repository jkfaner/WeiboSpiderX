#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/30 12:10
@Project:WeiboSpiderX
@File:test_weibo.py
@Desc:
"""
import scrapy

from WeiboSpiderX.bean.user import UserItem
from WeiboSpiderX.spiders.weibo import WeiboSpider


class TestWeiBo(WeiboSpider):
    name = "test"

    def test(self):
        user = UserItem()
        # user.idstr = "5620230193"
        # user.screen_name = "175灵敏"
        user.idstr = "7796248561"
        user.screen_name = "-Wsssui-"
        # user.idstr = "3700763437"
        # user.screen_name = "女刺客儿"
        user.idstr = "6091593545"
        user.screen_name = "Lee_and_Lee"
        self.logger.info("首次获取{}的博客...".format(user.screen_name))
        params = {"uid": user.idstr, "page": 1, "since_id": "", "feature": 0}
        item = self.request(self.user_blog_url, params, self.process_blogs)
        yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

    def start_requests(self):
        """
        爬虫入口
        :return:
        """
        return self.test()