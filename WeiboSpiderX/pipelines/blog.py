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
from WeiboSpiderX.bean.blog import BlogItem
from WeiboSpiderX.bean.blogType import BlogTypeItem
from WeiboSpiderX.bean.media import MediaItem
from WeiboSpiderX.cache import CacheFactory
from WeiboSpiderX.extractor.wb_extractor import ExtractorBlog, extract_media


class BlogPipeline(CacheFactory):

    def __init__(self, settings, server):
        super(BlogPipeline, self).__init__()
        self.settings = settings
        self.server = server
        self.redis_name = constants.MEDIA_KEY
        self.type = settings.get("SPIDER_BLOG_TYPE")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        server = crawler.spider.server
        return cls(settings, server)

    def filter_type(self, blogs: List[BlogTypeItem]) -> List[BlogItem]:
        new_blogs = list()
        for blog in blogs:
            if self.type == constants.BLOG_FILTER_ORIGINAL:
                # 获取原创
                if blog.original:
                    new_blogs.append(blog.original)
            elif self.type == constants.BLOG_FILTER_FORWARD:
                # 获取转发
                if blog.forward:
                    new_blogs.append(blog.forward)
            else:
                # 原创+转发
                if blog.original:
                    new_blogs.append(blog.original)
                if blog.forward:
                    new_blogs.append(blog.forward)
        return new_blogs

    def filter_blog_type(self, item: List[BlogTypeItem]) -> List[MediaItem]:
        blogs = self.filter_type(item)  # 过滤类型
        medias = extract_media(blogs)  # 提取媒体
        self.update_cache(medias)  # 添加缓存
        return medias

    def process_item(self, item: dict, spider) -> Union[List[MediaItem], dict]:
        if isinstance(item, dict) and item.get("blog"):
            ext = ExtractorBlog()
            blogs = ext.extractor_blog(item["blog"])
            medias = self.filter_blog_type(item=blogs)
            # for media in medias:
            #     if not self.server.hexists(self.redis_name, media.blog_id):
            #         self.server.hset(self.redis_name, media.blog_id, media.to_json())
            return medias
