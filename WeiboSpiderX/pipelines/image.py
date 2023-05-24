#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/24 23:31
@Project:WeiboSpiderX
@File:image.py
@Desc:
"""
import logging
from urllib.parse import quote

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

from WeiboSpiderX.items.media import Media


class CustomImagesPipeline(ImagesPipeline):

    def __init__(self, *args, **kwargs):
        super(CustomImagesPipeline, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.settings = get_project_settings()

    def file_path(self, request, response=None, info=None, *, item=None):
        # 重写文件路径的生成方法
        media = request.meta["media"]
        return media.filepath

    def get_media_requests(self, item, info):
        # 在这里生成下载图片的请求
        for media in item:
            if isinstance(media, Media):
                if media.is_image:
                    yield scrapy.Request(media.url, meta=dict(media=media))

    def item_completed(self, results, item, info):
        completed_list = [x for ok, x in results if ok]
        for x in completed_list:
            self.logger.info(f"图片下载成功: file://{self.settings.get('IMAGES_STORE')}/{quote(x.get('path'))}")
        return completed_list
