import json
import sys
import time

from DecryptLogin.core import weibo
from requests.utils import dict_from_cookiejar
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

from WeiboSpiderX import constants


class TooManyRequestsRetryMiddleware(RetryMiddleware):

    def __init__(self, crawler):
        super(TooManyRequestsRetryMiddleware, self).__init__(crawler.settings)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        if response.status == 403:
            self.crawler.engine.pause()
            time.sleep(60 * 10)  # If the rate limit is renewed in a minute, put 60 seconds, and so on.
            self.crawler.engine.unpause()
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        elif response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response


class HandleCookieMiddleware:

    def __init__(self, uid, redis, apis):
        self.uid = uid
        self.redis = redis
        self.api_list = apis
        self.logged_in = False  # 标志变量，表示是否已登录成功

    @classmethod
    def from_crawler(cls, crawler):
        uid = crawler.settings.get('SPIDER_UID')
        redis = crawler.spider.server
        apis = crawler.spider.api_list
        return cls(uid, redis, apis)

    def get_cookies(self):
        # 返回登录后的Cookie
        # 如果登录操作成功，返回最新的Cookie
        # 如果登录操作失败，返回上一次成功登录时的Cookie
        if self.redis.hexists(constants.LOGIN_KEY, self.uid):
            cookie = self.redis.hget(constants.LOGIN_KEY, self.uid)
            return json.loads(cookie)

    def login(self):
        if not self.logged_in:
            result, session = weibo().login()
            uid = result["uid"]
            if uid != self.uid:
                sys.exit("当前登录用户与设置用户不一致！")
            cookie = dict_from_cookiejar(session.cookies)
            self.redis.hset(constants.LOGIN_KEY, self.uid, json.dumps(cookie))
            self.logged_in = True

    def process_response(self, request, response, spider):
        # 检查响应是否表示登录失败
        if self.is_login_failed(response):
            # 登录失败，重新登录
            self.login()

            # 重新发送原始请求
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request

        return response

    def process_request(self, request, spider):
        # 检查请求是否需要登录
        if self.should_login(request):
            # 模拟登录操作
            self.login()
        # 在请求中添加Cookie
        request.cookies = self.get_cookies()

    def should_login(self, request):
        # 根据请求的URL、响应内容等判断是否需要登录
        # 返回True表示需要登录，False表示无需登录
        if request.url.split("?")[0] not in self.api_list and not self.logged_in:
            self.logged_in = False
            return True
        return False

    def is_login_failed(self, response):
        # 根据响应内容、状态码等判断是否登录失败
        # 返回True表示登录失败，False表示登录成功
        if response.url.split("?")[0] not in self.api_list and not self.logged_in:
            self.logged_in = False
            return True
        return False
