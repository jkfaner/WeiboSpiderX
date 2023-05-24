#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/24 23:32
@Project:WeiboSpiderX
@File:video.py
@Desc:
"""

import logging
from urllib.parse import quote

import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.project import get_project_settings

from WeiboSpiderX.items.media import Media


class VideoDownloadPipeline(FilesPipeline):

    def __init__(self, *args, **kwargs):
        super(VideoDownloadPipeline, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.settings = get_project_settings()

    def file_path(self, request, response=None, info=None, *, item=None):
        # 重写文件路径的生成方法
        media = request.meta["media"]
        return media.filepath

    def get_media_requests(self, item, info):
        # 获取视频URL并生成下载请求
        for media in item:
            if isinstance(media, Media):
                if media.is_video or media.is_live:
                    yield scrapy.Request(media.url, meta=dict(media=media))

    def item_completed(self, results, item, info):
        completed_list = [x for ok, x in results if ok]
        for x in completed_list:
            self.logger.info(f"视频下载成功: file://{self.settings.get('FILES_STORE')}/{quote(x.get('path'))}")
        return completed_list
