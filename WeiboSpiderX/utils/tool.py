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
from urllib.parse import parse_qs, urlparse

from WeiboSpiderX.items.base import BaseItem


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


def set_attr(source: dict, entity: BaseItem):
    """
    entity对象赋值
    :param entity:
    :param source:
    :return:
    """
    for k, v in entity.to_dict().items():
        setattr(entity, k, source.get(k))
    return entity


def parse_query_params(url):
    # 解析 URL
    parsed_url = urlparse(url)

    # 获取查询参数部分，并将其解析为字典形式
    query_params = parse_qs(parsed_url.query)

    # 将多值参数字典转换为单值参数字典
    params_dict = {k: v[0] for k, v in query_params.items()}

    return params_dict


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


def time_formatting(created_at, usefilename=True, strftime=None):
    """
    时间格式化
    :param created_at: 'Fri Dec 24 03:49:03 +0800 2021'
    :param usefilename: 启用文件名格式：20211224
    :param strftime: 含有时分秒格式 2021-12-24 3:49:03
    :return: 格式化后的时间字符串
    """
    dt_obj = datetime.datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')

    if usefilename:
        strftime = '%Y%m%d'
    elif strftime:
        strftime = '%Y-%m-%d %H:%M:%S'
    else:
        strftime = '%Y-%m-%d'

    return dt_obj.strftime(strftime)

