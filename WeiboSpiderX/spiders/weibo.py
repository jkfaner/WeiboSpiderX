import time
from abc import ABC

import scrapy

from WeiboSpiderX.aop import ScrapyLogger
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.extractor.wb_extractor import extractor_user
from WeiboSpiderX.spiders.refresh import RefreshWeibo
from WeiboSpiderX.utils.tool import requestQuery


class WeiboSpider(RefreshWeibo, ABC):
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

    def start_requests(self):
        """
        爬虫入口
        :return:
        """
        return self.process_groups()

    @ScrapyLogger(start={"info": "首次获取分组下的博主..."})
    def parse_groups(self, response):
        """
        解析分组
        :param response:
        :return:
        """
        finder = JsonDataFinderFactory(response.text, mode="value")
        group_items = finder.get_same_level(self.settings.get("SPIDER_GROUP"))
        self.list_id = group_items[0].get("idstr")
        params = {"list_id": self.list_id, "page": 1}
        item = requestQuery(self.group_members_url, params, self.process_group_members)
        yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

    @ScrapyLogger(start={"info": "获取分组下的博主..."})
    def process_group_members(self, response):
        finder = JsonDataFinderFactory(response.text)
        users = finder.find_first_value("users")
        if users:
            yield {"user": response.text}

            time.sleep(2)

            params = response.meta.get("params")
            params["page"] = params["page"] + 1
            item = requestQuery(self.group_members_url, params, self.process_group_members)
            yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

            for blogs_first in self.process_blogs_first(response):
                yield blogs_first

        else:
            self.logger.info("博主获取完毕...")

    def process_blogs_first(self, response):
        users = extractor_user(response.text)
        blogs_first_list = []
        for user in users:
            self.logger.info("首次获取【{}->{}】的博客".format(user.screen_name,user.idstr))
            params = {"uid": user.idstr, "page": 1, "since_id": "", "feature": 0}
            item = requestQuery(self.user_blog_url, params, self.process_blogs)
            blogs_first_list.append(scrapy.Request(url=item.url, meta=item.meta, callback=item.callback))
        return blogs_first_list

    @ScrapyLogger(start={"info": "获取博客..."})
    def process_blogs(self, response):
        """
        获取博客
        :param response:
        :return:
        """
        finder = JsonDataFinderFactory(response.text)
        if finder.exist_key("list"):
            yield dict(blog=response.text)
            time.sleep(2)
            # 获取博客
            since_id = finder.get_first_value("since_id")
            query = response.meta["params"]
            uid = query["uid"]
            self.logger.info("获取其他博客...")
            if since_id:
                params = {"uid": uid, "page": query["page"] + 1, "since_id": since_id, "feature": 0}
                item = requestQuery(self.user_blog_url, params, self.process_blogs)
                yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)
            else:
                # 刷新本地
                full = self.get_redis(uid)
                full.is_end = True
                self.set_redis(uid=uid, value=full)
                self.logger.info("微博获取结束:{}".format(uid))
                self.logger.info(full.to_json())