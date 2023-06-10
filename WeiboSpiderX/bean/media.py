#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/21 03:09
@Project:WeiboSpiderX
@File:media.py
@Desc:
"""
import json

from WeiboSpiderX.bean.base import BaseItem
from WeiboSpiderX.bean.video import Video


class MediaItem(BaseItem):

    def __init__(self):
        self._blog = None
        self._blog_id = None
        self._url = None
        self._filename = None
        self._filepath = None
        self._folder_name = None
        self._is_image = None
        self._is_live = None
        self._is_video = None

    @property
    def blog(self):
        return self._blog

    @blog.setter
    def blog(self, blog):
        self._blog = blog

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def folder_name(self):
        return self._folder_name

    @folder_name.setter
    def folder_name(self, folder_name):
        self._folder_name = folder_name

    @property
    def blog_id(self):
        return self._blog_id

    @blog_id.setter
    def blog_id(self, blog_id):
        self._blog_id = blog_id

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        self._filepath = filepath

    @property
    def is_image(self):
        return self._is_image

    @is_image.setter
    def is_image(self, value):
        self._is_image = value

    @property
    def is_live(self):
        return self._is_live

    @is_live.setter
    def is_live(self, value):
        self._is_live = value

    @property
    def is_video(self):
        return self._is_video

    @is_video.setter
    def is_video(self, value):
        self._is_video = value
