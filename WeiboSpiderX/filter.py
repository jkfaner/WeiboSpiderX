#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/21 02:34
@Project:WeiboSpiderX
@File:filter.py
@Desc:
"""
from typing import List

from scrapy.utils.project import get_project_settings

from WeiboSpiderX import constants
from WeiboSpiderX.items.blog import Blog
from WeiboSpiderX.items.blogType import BlogType

# 获取项目设置参数
settings = get_project_settings()
SPIDER_BLOG_TYPE = settings.get('SPIDER_BLOG_TYPE')


def filter_type(blogs: List[BlogType]) -> List[Blog]:

    new_blogs = list()
    for blog in blogs:
        if SPIDER_BLOG_TYPE == constants.BLOG_FILTER_ORIGINAL:
            # 获取原创
            if blog.original:
                new_blogs.append(blog.original)
        elif SPIDER_BLOG_TYPE == constants.BLOG_FILTER_FORWARD:
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
