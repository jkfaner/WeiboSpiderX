#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/21 00:24
@Project:WeiboSpiderX
@File:wb_extractor.py
@Desc:
"""
import sys
from typing import List

from WeiboSpiderX import constants
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.items.blog import Blog
from WeiboSpiderX.items.blogType import BlogType
from WeiboSpiderX.items.media import Media
from WeiboSpiderX.items.user import UserItem
from WeiboSpiderX.items.video import Video
from WeiboSpiderX.utils.tool import set_attr, time_formatting, get_file_suffix


def extractor_user(json_str) -> List[UserItem]:
    finder = JsonDataFinderFactory(json_str)
    users = list()
    if not json_str:
        users.append(UserItem())
        return users

    user = finder.find_all_values("users")
    user = user if user else finder.find_first_value('user')
    if isinstance(user, list):
        for _user in user:
            if isinstance(_user,dict):
                users.append(set_attr(source=_user, entity=UserItem()))
            else:
                print(json_str)
                print(user)
                sys.exit("extractor_user")
    elif isinstance(user, dict):
        users.append(set_attr(source=user, entity=UserItem()))
    else:
        users.append(UserItem())
    return users


class ExtractorBlog:

    def extractor_blog(self, json_str: str) -> List[BlogType]:
        finder = JsonDataFinderFactory(json_str)
        statuses_blogs = [self._clean_blog(item) for item in finder.find_first_value("statuses")]
        list_blogs = [self._clean_blog(item) for item in finder.find_first_value("list")]
        statuses_blogs.extend(list_blogs)
        return statuses_blogs

    def _clean_blog(self, item: dict) -> BlogType:
        blogType = BlogType()
        # 点赞 快转 出现的按钮标签 followBtnCode
        # 快转了 screen_name_suffix_new
        if "followBtnCode" in item:
            return blogType

        finder = JsonDataFinderFactory(item)

        screen_name_suffix_new = finder.find_first_value("screen_name_suffix_new")
        if screen_name_suffix_new:
            if "快转了" in str(screen_name_suffix_new):
                return blogType

        promotion = finder.find_first_value("promotion")
        if promotion:
            if "广告" in str(promotion):
                return blogType

        if item.get("title"):
            # 很多很多 包括赞过的 评论过的。。。
            if item["title"].get("text"):
                return blogType

        # 原创与转发分离
        # page_info包含视频内容
        # 如果是转发 即有retweeted_status对象 则page_info应该属于retweeted_status对象中
        # 如果是原创 即retweeted_status对象为空（或不存在）则的page_info应该属于weiboObj对象中
        retweeted_item = finder.find_first_value("retweeted_status")
        if "retweeted_status" in item:
            del item['retweeted_status']

        original_blog = self._process_blog(item=item, is_original=True)
        blogType.original = original_blog

        if retweeted_item:
            forward_weiboEntity = self._process_blog(item=retweeted_item, is_original=False)
            blogType.forward = forward_weiboEntity

        return blogType

    def _process_blog(self, item: dict, is_original: bool) -> Blog:
        """
        加工博客
        :param item:
        :param is_original: 是否原创
        :return:
        """
        blog = Blog()
        finder = JsonDataFinderFactory(item)

        # 检查是否是置顶 置顶数据在筛选过程中不中断
        is_top = finder.find_first_value("isTop")
        if is_top and isinstance(is_top, int) and is_top == 1:
            blog.is_top = True
        else:
            blog.is_top = False

        user_items = extractor_user(item)
        if len(user_items) == 1:
            created_at = finder.find_first_value("created_at")
            images, live_photo = self._choose_image(item=item)
            videos = self._choose_video(item=item)
            # 获取质量最佳的视频 即第一个
            videos = videos[0] if videos else videos

            blog.blog_id = item["id"]
            blog.id = user_items[0].id
            blog.screen_name = user_items[0].screen_name
            blog.created_at = created_at
            blog.livephoto_video = live_photo
            blog.images = images
            blog.videos = videos
            if is_original:
                blog.image_str = constants.DOWNLOAD_PATH_IMG_ORIGINAL_STR
                blog.video_str = constants.DOWNLOAD_PATH_VIDEO_ORIGINAL_STR
            else:
                blog.image_str = constants.DOWNLOAD_PATH_IMG_FORWARD_STR
                blog.video_str = constants.DOWNLOAD_PATH_VIDEO_FORWARD_STR
        return blog

    @staticmethod
    def _choose_image(item) -> tuple:
        """
        选择图片
        :param item:
        :return:
        """
        large_images = list()
        videos = list()
        # 图片 pic_ids
        # 图片 pic_infos
        finder = JsonDataFinderFactory(item)
        pic_ids = finder.find_first_value("pic_ids")
        pic_infos = finder.find_first_value("pic_infos")
        for index, _id in enumerate(pic_ids, 1):
            try:
                pic = pic_infos.get(_id)
            except AttributeError:
                continue
            if not pic:
                continue
            # 图片尺寸大小：large>mw2000>orj1080>orj960>wap360>wap180
            # 对应的对象是：largest>mw2000>original>large>bmiddle>thumbnail
            # 优先下载large尺寸的图片
            if pic.get("largest"):
                pic["largest"].update(dict(index=index))
                large_images.append(pic["largest"])

            elif pic.get("mw2000"):
                pic["mw2000"].update(dict(index=index))
                large_images.append(pic["mw2000"])

            elif pic.get("original"):
                pic["original"].update(dict(index=index))
                large_images.append(pic["original"])

            elif pic.get("large"):
                pic["large"].update(dict(index=index))
                large_images.append(pic["large"])

            elif pic.get("bmiddle"):
                pic["bmiddle"].update(dict(index=index))
                large_images.append(pic["bmiddle"])

            elif pic.get("thumbnail"):
                pic["thumbnail"].update(dict(index=index))
                large_images.append(pic["thumbnail"])

            if pic.get("Video"):
                videos.append(dict(url=pic["Video"], index=index))

        return large_images, videos

    @staticmethod
    def _choose_video(item: dict) -> List[Video]:
        """
        选择视频
        :param item:
        :return:
        """
        finder = JsonDataFinderFactory(item)
        return [set_attr(video, Video()) for video in finder.find_all_values("play_info")]


def extract_media(blogs: List[Blog]) -> List[Media]:
    medias = []
    for blog in blogs:

        # 视频
        if blog.videos:
            base_filename = f"{time_formatting(blog.created_at)}_{blog.blog_id}"
            filename = f"{base_filename}.mp4"

            video_media = Media()
            video_media.blog = blog
            video_media.blog_id = blog.blog_id
            video_media.filename = filename
            video_media.filepath = f"{blog.screen_name}/{blog.video_str}/{filename}"
            video_media.folder_name = blog.video_str
            video_media.url = blog.videos.url
            video_media.is_live = False
            video_media.is_image = False
            video_media.is_video = True
            medias.append(video_media)

        # 图片
        for index, image in enumerate(blog.images):
            suffix = get_file_suffix(image["url"])
            base_filename = f"{time_formatting(blog.created_at)}_{blog.blog_id}"
            filename = f"{base_filename}_{index}.{suffix}"

            image_media = Media()
            image_media.blog = blog
            image_media.blog_id = blog.blog_id
            image_media.filename = filename
            image_media.folder_name = blog.image_str
            image_media.filepath = f"{blog.screen_name}/{blog.image_str}/{filename}"
            image_media.url = image['url']
            image_media.is_live = False
            image_media.is_image = True
            image_media.is_video = False
            medias.append(image_media)

        # livephoto
        for index, livephoto in enumerate(blog.livephoto_video):
            suffix = get_file_suffix(livephoto["url"])
            base_filename = f"{time_formatting(blog.created_at)}_{blog.blog_id}"
            filename = f"{base_filename}_{index}.{suffix}"

            live_media = Media()
            live_media.blog = blog
            live_media.blog_id = blog.blog_id
            live_media.filename = filename
            live_media.filepath = f"{blog.screen_name}/{blog.video_str}/{filename}"
            live_media.folder_name = blog.video_str
            live_media.url = livephoto['url']
            live_media.is_live = True
            live_media.is_image = False
            live_media.is_video = False
            medias.append(live_media)

    return medias