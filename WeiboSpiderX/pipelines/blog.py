#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/24 23:31
@Project:WeiboSpiderX
@File:blog.py
@Desc:博客管道
"""
import json
import logging
import os
from typing import List, Union, Dict

from WeiboSpiderX.bean.blog import BlogItem
from WeiboSpiderX.bean.blog import BlogTypeItem
from WeiboSpiderX.bean.media import MediaItem
from WeiboSpiderX.cache import CacheFactory
from WeiboSpiderX.constants import ORIGINAL, FORWARD, MEDIA_KEY, USER_KEY
from WeiboSpiderX.extractor.wb_extractor import ExtractorBlog
from WeiboSpiderX.utils.tool import file_time_formatting, get_file_suffix

logger = logging.getLogger(__name__)


class BlogPipeline(CacheFactory):

    def __init__(self, server, filter_type, images_store, files_store):
        super(BlogPipeline, self).__init__()
        self.server = server
        self.filter_type = filter_type
        self.images_store = images_store
        self.files_store = files_store

        self.redis_media_name = MEDIA_KEY
        self.redis_user_name = USER_KEY
        self.original = ORIGINAL
        self.forward = FORWARD

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        server = crawler.spider.server
        filter_type = crawler.settings.get("SPIDER_BLOG_TYPE")
        images_store = crawler.settings.get("IMAGES_STORE")
        files_store = crawler.settings.get("FILES_STORE")
        return cls(server, filter_type, images_store, files_store)

    @staticmethod
    def create_media_item(blog: BlogItem, filename, folder_name, url, is_live, is_image, is_video) -> MediaItem:
        """
        创建媒体对象
        :param blog: 博客对象
        :param filename: 文件名
        :param folder_name: 文件夹名
        :param url: 媒体地址
        :param is_live: 是否是live图片
        :param is_image: 是否是图片（非live）
        :param is_video: 是否是视频
        :return: 媒体对象
        """
        media_item = MediaItem()
        media_item.blog = blog
        media_item.blog_id = blog.blog_id
        media_item.filename = filename
        media_item.folder_name = folder_name
        media_item.filepath = f"{blog.screen_name}/{folder_name}/{filename}"
        media_item.url = url
        media_item.is_live = is_live
        media_item.is_image = is_image
        media_item.is_video = is_video
        return media_item

    def extract_media(self, blogs: List[BlogItem]) -> List[MediaItem]:
        """
        提取媒体
        :param blogs: 博客列表
        :return:
        """
        medias = []
        for blog in blogs:
            if blog.videos:
                base_filename = f"{file_time_formatting(blog.created_at)}_{blog.blog_id}"
                filename = f"{base_filename}.mp4"
                url = blog.videos.url
                video_media = self.create_media_item(blog, filename, blog.video_str, url, False, False, True)
                medias.append(video_media)

            for index, image in enumerate(blog.images):
                url = image['url']
                suffix = get_file_suffix(url)
                base_filename = f"{file_time_formatting(blog.created_at)}_{blog.blog_id}"
                filename = f"{base_filename}_{index}.{suffix}"
                image_media = self.create_media_item(blog, filename, blog.image_str, url, False, True, False)
                medias.append(image_media)

            for index, live in enumerate(blog.livephoto_video):
                url = live['url']
                suffix = get_file_suffix(url)
                base_filename = f"{file_time_formatting(blog.created_at)}_{blog.blog_id}"
                filename = f"{base_filename}_{index}.{suffix}"
                live_media = self.create_media_item(blog, filename, blog.video_str, url, True, False, False)
                medias.append(live_media)

        return medias

    def adapt_blog_type(self, blog_items: List[BlogTypeItem]) -> List[BlogItem]:
        """
        适配博客类型
        :param blog_items:
        :return:
        """
        original_blogs = []
        forward_blogs = []
        # 原创
        if self.filter_type == self.original:
            original_blogs = [blog.original for blog in blog_items if blog.original]
            return original_blogs
        # 转发
        elif self.filter_type == self.forward:
            forward_blogs = [blog.forward for blog in blog_items if blog.forward]
            return forward_blogs
        else:
            return original_blogs + forward_blogs

    def separation_media(self, medias: List[MediaItem]) -> Dict[str, List[MediaItem]]:
        """
        将媒体分离为图片与视频
        :param medias: 媒体列表
        :return: 包含图片和视频的字典
        """
        images = [media for media in medias if media.is_image]
        videos = [media for media in medias if media.is_video or media.is_live]

        for media in medias:
            if not self.server.hexists(self.redis_media_name, media.blog_id):
                self.server.hset(self.redis_media_name, media.blog_id, media.to_json())

        return {'images': images, 'videos': videos}

    def rename_file(self, medias: List[MediaItem]):
        """
        修改文件
        :return:
        """
        for media in medias:
            root = self.images_store if media.is_image else self.files_store
            new_screen_name = media.filepath.split("/")[0]
            folder = os.path.join(root, new_screen_name)

            if not os.path.exists(folder):
                user = json.loads(self.server.hget(self.redis_user_name, media.blog.id))
                old_screen_name = user.get("list")[-1].get("user").get("screen_name")

                if old_screen_name != new_screen_name:
                    logger.info("用户修改了昵称,准备修改文件夹")
                    old_folder = os.path.join(root, old_screen_name)

                    try:
                        os.renames(old_folder, folder)
                    except Exception as e:
                        logger.error(f"Failed to rename {str(e)}")

    def process_item(self, item: dict, spider) -> Union[Dict[str, List[MediaItem]], dict]:
        """
        处理响应过来的博客json数据
            1. 提取博客
            2. 根据设置类型适配博客（原创 or 转发）
            3. 提取博客中的媒体数据
            4. 添加到缓存（用于增量爬取）
            5. 分离媒体数据中的图片和视频
        :param item: 管道的数据
        :param spider: 爬虫对象
        :return: 管道的数据 or 分离媒体数据中的图片和视频
        """
        if isinstance(item, dict) and (item.get("blog") or item.get("refresh")):
            ext = ExtractorBlog()
            blog_str = item.get("blog") if item.get("blog") else item.get("refresh")
            blogs = ext.extractor_blog(blog_str)
            # 适配博客类型
            blog_items = self.adapt_blog_type(blogs)
            # 提取媒体
            medias = self.extract_media(blog_items)
            # 修改文件名 避免用户更改昵称
            self.rename_file(medias)
            # 分离图片与视频
            return self.separation_media(medias)

        return item
