#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/24 23:32
@Project:WeiboSpiderX
@File:video.py
@Desc:视频下载管道
"""
import logging
from urllib.parse import quote

import scrapy
from scrapy.pipelines.files import FilesPipeline

from WeiboSpiderX.cache import CacheFactory

logger = logging.getLogger(__name__)


class VideoDownloadPipeline(FilesPipeline, CacheFactory):

    def __init__(self, *args, **kwargs):
        super(VideoDownloadPipeline, self).__init__(*args, **kwargs)
        self.files_store = args[0]

    def file_path(self, request, response=None, info=None, *, item=None):
        # 重写文件路径的生成方法
        # 修改文件夹
        media = request.meta["media"]
        return media.filepath

    def get_media_requests(self, item, info):
        # 获取视频URL并生成下载请求
        if isinstance(item, dict):
            for media in item.get("videos", []):
                yield scrapy.Request(media.url, meta=dict(media=media))
        return item

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
            logger.info(f"视频下载成功:{x.get('path')} -> file://{self.files_store}/{quote(x.get('path'))}")
        if completed_list:
            self.spider_record(completes=completed_list, item=item["videos"])
        return item
