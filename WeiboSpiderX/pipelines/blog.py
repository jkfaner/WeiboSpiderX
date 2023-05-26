#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/24 23:31
@Project:WeiboSpiderX
@File:blog.py
@Desc:
"""
from typing import List, Union

from WeiboSpiderX import constants
from WeiboSpiderX.extractor.wb_extractor import ExtractorBlog, extract_media
from WeiboSpiderX.filter import filter_type
from WeiboSpiderX.items.blogType import BlogType
from WeiboSpiderX.items.media import Media


class BlogPipeline:

    def __init__(self, settings, server):
        self.settings = settings
        self.server = server
        self.redis_name = constants.MEDIA_KEY

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        server = crawler.spider.server
        return cls(settings, server)

    @staticmethod
    def filter_blog_type(item) -> List[Media]:
        blogs = []
        if isinstance(item, list) and item:
            if isinstance(item[0], BlogType):
                blogs = filter_type(item)
                blogs = extract_media(blogs)
        return blogs

    def process_item(self, item: dict, spider) -> Union[List[Media], dict]:
        if isinstance(item, dict) and item.get("blog"):
            ext = ExtractorBlog()
            blogs = ext.extractor_blog(item["blog"])
            medias = self.filter_blog_type(blogs)
            for media in medias:
                if not self.server.hexists(self.redis_name, media.blog_id):
                    self.server.hset(self.redis_name, media.blog_id, media.to_json())
            return medias
        return item
