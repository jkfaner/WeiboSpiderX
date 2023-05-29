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

from WeiboSpiderX.bean.media import MediaItem
from WeiboSpiderX.cache import CacheFactory


class VideoDownloadPipeline(FilesPipeline, CacheFactory):

    def __init__(self, *args, **kwargs):
        super(VideoDownloadPipeline, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.settings = get_project_settings()
        self.files_store = self.settings.get('FILES_STORE')

    def file_path(self, request, response=None, info=None, *, item=None):
        # 重写文件路径的生成方法
        media = request.meta["media"]
        return media.filepath

    def get_media_requests(self, item, info):
        # 获取视频URL并生成下载请求
        video_live_list = []
        if isinstance(item, list):
            for media in item:
                if isinstance(media, MediaItem):
                    if media.is_video or media.is_live:
                        video_live_list.append(scrapy.Request(media.url, meta=dict(media=media)))
        return video_live_list

    def item_completed(self, results, item, info):
        """
        处理已完成下载的Item对象
        :param results:一个包含元组的列表，每个元组代表一个媒体文件的下载结果。
                        每个元组的第一个元素是布尔值，指示下载是否成功；
                        第二个元素是下载结果，通常是一个字典或文件路径。
        :param item:原始的Item对象，其中包含与媒体文件相关的字段和属性。
        :param info:一个包含有关当前请求和响应的信息的字典。
        :return:返回处理后的Item对象
        """
        completed_list = [x for ok, x in results if ok]
        for x in completed_list:
            self.logger.info(f"视频下载成功:{x.get('path')} -> file://{self.files_store}/{quote(x.get('path'))}")
        if completed_list:
            self.spider_record(completes=completed_list, item=item)
        return completed_list
