# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from urllib.parse import quote

import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

from WeiboSpiderX.extractor.wb_extractor import extractor_user, ExtractorBlog, extract_media
from WeiboSpiderX.filter import filter_type
from WeiboSpiderX.items.blogType import BlogType
from WeiboSpiderX.items.media import Media

# 获取项目设置参数
settings = get_project_settings()
FILES_STORE = settings.get('FILES_STORE')
IMAGES_STORE = settings.get('IMAGES_STORE')

class UserPipeline:

    def process_item(self, users: dict, spider):
        if isinstance(users, dict) and users.get("user"):
            user_items = extractor_user(users["user"])
            return user_items
        return users


class BlogPipeline:

    @staticmethod
    def filter_blog_type(item) -> list[Media]:
        blogs = []
        if isinstance(item, list) and item:
            if isinstance(item[0], BlogType):
                blogs = filter_type(item)
                blogs = extract_media(blogs)
        return blogs

    def process_item(self, blogs: dict, spider):
        if isinstance(blogs, dict) and blogs.get("blog"):
            ext = ExtractorBlog()
            blog_items = ext.extractor_blog(blogs["blog"])
            media_list = self.filter_blog_type(blog_items)
            return media_list
        return blogs


class CustomImagesPipeline(ImagesPipeline):

    def __init__(self, *args, **kwargs):
        super(CustomImagesPipeline, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

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
            self.logger.info(f"图片下载成功: file://{IMAGES_STORE}/{quote(x.get('path'))}")
        return completed_list


class VideoDownloadPipeline(FilesPipeline):

    def __init__(self, *args, **kwargs):
        super(VideoDownloadPipeline, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

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
            self.logger.info(f"视频下载成功: file://{IMAGES_STORE}/{quote(x.get('path'))}")
        return completed_list
