#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/20 15:15
@Project:WeiboSpider-Plus
@File:tool.py
@Desc:
"""
import datetime
import json
import os
from typing import Union
from urllib.parse import urlparse, urlencode

from WeiboSpiderX.bean.base import BaseItem
from WeiboSpiderX.bean.item import RequestParam, RequestMeta


def requestQuery(raw_url, params, callback) -> RequestParam:
    """
    获取request
    :param raw_url: 不带任何参数的url
    :param params: 请求参数
    :param callback: 回调方法
    :return:
    """
    url = f'{raw_url}?{urlencode(params)}'
    meta = RequestMeta()
    meta.url = url
    meta.raw_url = raw_url
    meta.params = params

    p = RequestParam()
    p.url = url
    p.meta = meta.to_dict()
    p.callback = callback
    return p


def read_json_file(file_path: str) -> Union[dict, list]:
    """
    读取 JSON 文件并解析为字典或列表

    :param file_path: JSON 文件路径
    :return: 解析后的 JSON 数据，可以是字典或列表
    """
    with open(file_path, 'r') as file:
        json_data = file.read()

    try:
        parsed_data = json.loads(json_data)
        return parsed_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")


def set_attr(source, entity: BaseItem):
    """
    entity对象赋值
    :param entity:
    :param source:
    :return:
    """
    for k, v in entity.to_dict().items():
        setattr(entity, k, source.get(k, v))
    return entity


def get_file_suffix(url):
    """
    通过url确定文件后缀
    :param url: url
    :return: 文件后缀
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    query = parsed_url.query

    if "." in path:
        filename = os.path.basename(path).split("?")[0]
    else:
        filename = query.split("=")[-1]

    suffix = os.path.splitext(filename)[1][1:]
    return suffix


def file_time_formatting(created_at,fmt="%Y%m%d"):
    """
    文件时间格式化
    :param fmt:
    :param created_at: 'Fri Dec 24 03:49:03 +0800 2021'
    :return: 格式化后的时间字符串
    """
    dt_obj = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
    return dt_obj.strftime(fmt)


def blog_time_formatting(created_at):
    """
    博客时间格式化
    :param created_at: 'Fri Dec 24 03:49:03 +0800 2021'
    :return:
    """
    dt_obj = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
    return dt_obj.astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S')


def get_time_now(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(fmt)
