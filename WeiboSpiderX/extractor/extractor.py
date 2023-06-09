#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:jkfaner & chatGPT
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2022/1/23 18:58
@Project:WeiboSpider
@File:extractor.py
@Desc:json提取器
"""
import json

from typing import Any, List, Union, Optional


class JsonPathFinder:
    """用于查找 JSON 数据的路径"""

    def __init__(self, json_data: Union[dict, list, str], mode='key'):
        """
        初始化 JsonPathFinder 对象

        :param json_data: JSON 数据
        :param mode: 模式，'key' 或 'value'，默认为 'key'
        """
        self.data = self._parse_json(json_data)
        self.mode = mode

    @staticmethod
    def _parse_json(json_data: Union[dict, list, str]) -> Union[dict, list]:
        """
        解析 JSON 数据

        :param json_data: JSON 数据
        :return: 解析后的 JSON 数据
        """
        if isinstance(json_data, (dict, list)):
            return json_data
        elif isinstance(json_data, str):
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {e}")
        else:
            raise ValueError(f"Invalid data type: {type(json_data)}")

    def iter_node(self, target: Any) -> List[List[Any]]:
        """
        迭代遍历 JSON 数据的节点，查找匹配的路径

        :param target: 目标值
        :return: 匹配的路径顺序列表
        """
        stack = [(self.data, [])]  # 使用栈来存储节点和路径
        paths = []  # 存储匹配的路径

        while stack:
            node, current_path = stack.pop()  # 从栈中取出节点和当前路径

            if isinstance(node, dict):
                for key, value in node.items():
                    new_path = current_path + [key]  # 更新路径
                    if self.mode == 'key':
                        if key == target:
                            paths.append(new_path)  # 如果匹配，将路径加入结果列表
                    elif self.mode == 'value':
                        if value == target:
                            paths.append(new_path)  # 如果匹配，将路径加入结果列表
                    if isinstance(value, (dict, list)):
                        stack.append((value, new_path))  # 将子节点和对应路径压入栈中

            elif isinstance(node, list):
                for index, value in enumerate(node):
                    new_path = current_path + [index]  # 更新路径
                    if self.mode == 'key':
                        if isinstance(value, (dict, list)):
                            stack.append((value, new_path))  # 将子节点和对应路径压入栈中
                    elif self.mode == 'value':
                        if value == target:
                            paths.append(new_path)  # 如果匹配，将路径加入结果列表
                        if isinstance(value, (dict, list)):
                            stack.append((value, new_path))  # 将子节点和对应路径压入栈中

        return paths[::-1]

    def join_path(self, target_paths: List[List[Any]]) -> Any:
        """
        通过路径查找数据


        :param target_paths: 目标路径列表
        :return: 查找到的数据
        """
        if not target_paths:
            return []
        if not isinstance(target_paths, list):
            return []

        if isinstance(target_paths[0], list):
            values_data = list()
            for targets in target_paths:
                cache_data = self.data
                for target in targets:
                    cache_data = cache_data[target]
                values_data.append(cache_data)
            if len(values_data) == 1:
                return values_data[0]
            return values_data

        data = self.data
        for target in target_paths:
            data = data[target]
        return data

    def find_first(self, target: Any) -> List[Any]:
        """
        获取第一个匹配路径

        :param target: 目标值
        :return: 第一个匹配到的路径列表，如果没有匹配项则返回空列表 []
        """
        path_iter = self.iter_node(target)
        if path_iter:
            return path_iter[0]
        else:
            return []

    def find_last(self, target: Any) -> List[Any]:
        """
        获取最后一个匹配路径

        :param target: 目标值
        :return: 最后一个匹配到的路径列表，如果没有匹配项则返回空列表 []
        """
        path_iter = self.iter_node(target)
        if path_iter:
            return path_iter[-1]
        return []

    def find_all(self, target: Any) -> List[List[Any]]:
        """
        获取所有匹配路径

        :param target: 目标值
        :return: 所有匹配到的路径列表
        """
        path_iter = self.iter_node(target)
        return list(path_iter)

    def exist_key(self, target: Any) -> bool:
        """
        判断是否存在某个键

        :param target: 目标值
        :return: 如果存在该键则返回 True，否则返回 False
        """
        paths = self.find_all(target)
        return len(paths) > 0


class JsonDataFinder(JsonPathFinder):
    """用于查找 JSON 数据的路径和值"""

    def get_same_level(self, target: Any) -> Optional[Any]:
        """
        获取同级json内容
        :param target: 目标值
        :return:
        """
        paths = self.find_all(target)
        return [self.join_path(p[:-1]) for p in paths]

    def get_first_value(self, key: str) -> Optional[Any]:
        """
        根据键获取第一个值

        :param key: 键
        :return: 第一个值，如果不存在则返回 None
        """
        paths = self.find_first(key)
        if paths:
            data = self.join_path(paths)
            if not isinstance(data, list):
                return data
            return data[0]
        else:
            return None

    def get_last_value(self, key: str) -> Optional[Any]:
        """
        根据键获取最后一个值

        :param key: 键
        :return: 最后一个值，如果不存在则返回 None
        """
        last_paths = self.find_last(key)
        if last_paths:
            return self.join_path(last_paths)[0]
        else:
            return None

    def get_value_by_key_and_index(self, key: str, index: int) -> Optional[Any]:
        """
        根据键和索引获取值

        :param key: 键
        :param index: 索引
        :return: 值，如果不存在则返回 None
        """
        paths = self.find_all(key)
        paths_with_index = [path + [index] for path in paths]
        result = self.join_path(paths_with_index)
        if result:
            return result[0]
        else:
            return None

    def get_all_data_by_key(self, key: str) -> List[Any]:
        """
        根据键获取所有数据

        :param key: 键
        :return: 所有数据列表，如果不存在则返回空列表 []
        """
        paths = self.find_all(key)
        return self.join_path(paths)

    def get_sibling_data_by_key(self, key: str) -> List[Any]:
        """
        根据键获取同层数据

        :param key: 键
        :return: 同层数据列表，如果不存在则返回空列表 []
        """
        paths = self.find_all(key)
        sibling_paths = [path[:-1] for path in paths]
        return self.join_path(sibling_paths)

    def get_parent_data_by_key(self, key: str) -> List[Any]:
        """
        根据键获取上一层数据

        :param key: 键
        :return: 上一层数据列表，如果不存在则返回空列表 []
        """
        paths = self.find_all(key)
        parent_paths = [path[:-2] if len(path) >= 2 else [] for path in paths]
        return self.join_path(parent_paths)

    def get_child_data_by_key(self, key: str) -> List[Any]:
        """
        根据键获取下一层数据

        :param key: 键
        :return: 下一层数据列表，如果不存在则返回空列表 []
        """
        paths = self.find_all(key)
        child_paths = [path + [path[-1] + 1] for path in paths if len(path) > 0]
        return self.join_path(child_paths)


class JsonDataFinderFactory(JsonDataFinder):

    def find_all_values(self, key: str) -> List[Any]:
        """
        查找目标键的所有值

        :param key: 目标键
        :return: 匹配的所有值列表
        """
        values = self.join_path(self.find_all(key))
        if len(values) == 1:
            return values[0]
        return values

    def find_first_value(self, key: str) -> Union[Any]:
        """
        查找目标键的第一个值

        :param key: 目标键
        :return: 第一个匹配到的值，如果没有匹配项则返回 None
        """
        path = self.find_first(key)
        if path:
            value = self.join_path(path)
            return value
        else:
            return []
