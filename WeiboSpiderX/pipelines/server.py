#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/6/8 18:18
@Project:WeiboSpiderX
@File:server.py
@Desc:
"""
import logging

import pymongo


class MongoDBHandler(object):

    def __init__(self, settings):
        self.logger = logging.getLogger(__name__)

        mongo_uri = settings.get('MONGO_URI')
        mongo_db = settings.get('MONGO_DATABASE')
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings=settings)

    def close_connection(self):
        """
        关闭 MongoDB 连接
        """
        self.client.close()

    def insert_one(self, collection_name, data):
        """
        插入单个文档到集合中
        :param collection_name: 文档名称
        :param data: 待插入的文档数据
        :return: 插入文档的 _id 值
        """
        result = self.db[collection_name].insert_one(data)
        return result.inserted_id

    def insert_many(self, collection_name, data_list):
        """
        批量插入文档到集合中
        :param collection_name: 文档名称
        :param data_list: 待插入的文档数据列表
        :return: 插入文档的 _id 值列表
        """
        result = self.db[collection_name].insert_many(data_list)
        return result.inserted_ids

    def update_many(self, collection_name, filter_query, update_data):
        """
        更新匹配到的多个文档
        :param collection_name: 文档名称
        :param filter_query: 过滤查询条件
        :param update_data: 更新的数据
        :return: 被修改的文档数量
        """
        result = self.db[collection_name].update_many(filter_query, {"$set": update_data})
        return result.modified_count

    def find_one_and_update(self, collection_name, filter_query, update_data):
        """
        查找并修改匹配到的单个文档
        :param collection_name: 文档名称
        :param filter_query: 过滤查询条件
        :param update_data: 更新的数据
        :return: 被修改的文档
        """
        result = self.db[collection_name].find_one_and_update(filter_query, {"$set": update_data})
        return result

    def find_by_filter(self, collection_name, filter_query):
        """
        根据过滤查询条件查找文档
        :param collection_name: 文档名称
        :param filter_query: 过滤查询条件
        :return: 查询结果
        """
        result = self.db[collection_name].find(filter_query)
        return result

    def find_one_by_filter(self, collection_name, filter_query):
        """
        根据过滤查询条件查找单个文档
        :param collection_name: 文档名称
        :param filter_query: 过滤查询条件
        :return: 查询结果
        """
        result = self.db[collection_name].find_one(filter_query)
        return result

    def find_all(self, collection_name):
        """
        查找集合中的所有文档
        :param collection_name: 文档名称
        :return: 查询结果
        """
        result = self.db[collection_name].find()
        return result

    def delete_by_filter(self, collection_name, filter_query):
        """
        根据过滤查询条件删除文档
        :param collection_name: 文档名称
        :param filter_query: 过滤查询条件
        :return: 成功删除的数量
        """
        result = self.db[collection_name].delete_many(filter_query)
        return result.deleted_count