import time
from abc import ABC
from urllib.parse import urlencode

import scrapy
from scrapy_redis.spiders import RedisSpider

from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.extractor.wb_extractor import extractor_user
from WeiboSpiderX.items.item import RequestMeta, RequestParam


class WeiboSpider(RedisSpider, ABC):
    name = "weibo"

    def __init__(self, **kwargs):
        super(WeiboSpider).__init__()
        self.groups_url = "https://weibo.com/ajax/profile/getGroups"
        self.group_members_url = "https://weibo.com/ajax/profile/getGroupMembers"
        self.user_blog_url = "https://weibo.com/ajax/statuses/mymblog"
        self.user_info_url = "https://weibo.com/ajax/profile/info"
        self.user_info_detail_url = "https://weibo.com/ajax/profile/detail"
        self.user_friends_url = "https://weibo.com/ajax/friendships/friends"
        self.user_follow_content_url = "https://weibo.com/ajax/profile/followContent"
        self.api_list = self.get_api()
        self.settings = kwargs.get('settings')
        self.uid = None

    def get_api(self):
        attributes = [
            self.user_blog_url, self.user_info_url,
            self.user_info_detail_url, self.user_friends_url,
            self.groups_url, self.group_members_url, self.user_follow_content_url,
        ]
        return attributes

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WeiboSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.settings = crawler.settings
        return spider

    @staticmethod
    def request(raw_url, params, callback) -> RequestParam:
        """
        获取request
        :param raw_url: 不带任何参数的url
        :param params: 请求参数
        :param callback: 回调方法
        :return:
        """
        url = f'{raw_url}?{urlencode(params)}'
        meta = RequestMeta()
        meta.url = url
        meta.raw_url = raw_url
        meta.params = params

        p = RequestParam()
        p.url = url
        p.meta = meta.to_dict()
        p.callback = callback
        return p

    def start_requests(self):
        """
        爬虫入口
        :return:
        """
        return self.process_groups()

    def process_groups(self):
        """
        获得分组
        :return:
        """
        self.logger.info("获取分组...")
        params = {"showBilateral": 1}
        item = self.request(self.groups_url, params, self.process_group_members)
        yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

    def process_group_members(self, response):
        """
        获得分组数据
        :return:
        """
        if response.meta.get("raw_url") == self.groups_url:
            self.logger.info("第一次获取分组下的博主...")
            finder = JsonDataFinderFactory(response.text, mode="value")
            group_items = finder.get_same_level(self.settings.get("SPIDER_GROUP"))
            params = {"list_id": group_items[0].get("idstr"), "page": 1}
            item = self.request(self.group_members_url, params, self.process_group_members)
            yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

        elif response.meta.get("raw_url") == self.group_members_url:
            self.logger.info("获取分组下其他的博主...")
            finder = JsonDataFinderFactory(response.text)
            users = finder.find_first_value("users")
            if users:
                yield {"user": response.text}

                time.sleep(1)

                # 获取用户
                self.logger.info("获取博主...")
                params = response.meta.get("params")
                params["page"] = params["page"] + 1
                item = self.request(self.group_members_url, params, self.process_group_members)
                yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

                # 获取博客
                for user in extractor_user(response.text):
                    self.logger.info("获取博客：{}".format(user.screen_name))
                    params = {"uid": user.idstr, "page": 1, "since_id": "", "feature": 0}
                    item = self.request(self.user_blog_url, params, self.process_blogs)
                    yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

    def process_blogs(self, response):
        """
        获取博客
        :param response:
        :return:
        """
        finder = JsonDataFinderFactory(response.text)
        if finder.exist_key("list"):
            yield dict(blog=response.text)

            time.sleep(1)

            # 获取博客
            self.logger.info("获取博客...")
            since_id = finder.get_first_value("since_id")
            if since_id:
                query = response.meta["params"]
                params = {"uid": query["uid"], "page": query["page"] + 1, "since_id": since_id, "feature": 0}
                item = self.request(self.user_blog_url, params, self.process_blogs)
                yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)
