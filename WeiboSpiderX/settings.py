# Scrapy settings for WeiboSpiderX project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import os.path
from datetime import datetime

from scrapy.utils.log import configure_logging

BOT_NAME = "WeiboSpiderX"  # 项目名称

SPIDER_MODULES = ["WeiboSpiderX.spiders"]  # 爬虫模块路径
NEWSPIDER_MODULE = "WeiboSpiderX.spiders"  # 新建爬虫模块路径

# USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"

ROBOTSTXT_OBEY = False  # 是否遵循 robots.txt 规则

CONCURRENT_REQUESTS = 16  # 并发请求的最大数量

# 下载延迟设置，单位为秒
# DOWNLOAD_DELAY = 3
# 设置每个域名（domain）或 IP 可以同时进行的最大并发请求数量
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# 是否启用 cookies
# 开启后使用自定义cookie
# COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# 是否启用 Telnet 控制台
# 如果设置为 True，则启用 Telnet 控制台，允许通过 Telnet 连接到 Scrapy 以进行调试和控制。
# 如果设置为 False，则禁用 Telnet 控制台，不允许通过 Telnet 连接到 Scrapy。
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,da;q=0.7,zh-TW;q=0.6",
# }

# SPIDER_MIDDLEWARES = {
#     "WeiboSpiderX.middlewares.RefreshCookieMiddleware": 299,
#     "WeiboSpiderX.middlewares.TooManyRequestsRetryMiddleware": 300,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# 数字越小请求越先执行 同时响应越晚执行
DOWNLOADER_MIDDLEWARES = {
    "WeiboSpiderX.middleware.cookie.HandleCookieMiddleware": 300,
    "WeiboSpiderX.middleware.retry.TooManyRequestsRetryMiddleware": 301,
    "WeiboSpiderX.middleware.flow.URLFilterMiddleware": 302,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "WeiboSpiderX.pipelines.user.UserPipeline": 299,
    "WeiboSpiderX.pipelines.blog.BlogPipeline": 300,
    "WeiboSpiderX.pipelines.image.ImageDownloadPipeline": 301,
    "WeiboSpiderX.pipelines.video.VideoDownloadPipeline": 302,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html

# 是否启用自动限速
# 如果设置为 True，则启用自动限速功能。自动限速功能可根据网络状况和服务器响应情况自动调整下载延迟，以防止对目标网站造成过大负荷
# AUTOTHROTTLE_ENABLED = True

# 初始下载延迟
# 自动限速功能启用后，第一个请求的下载延迟。单位为秒。
# AUTOTHROTTLE_START_DELAY = 5

# 最大下载延迟
# 自动限速功能启用后，最大的下载延迟。如果网络延迟过高，下载延迟会逐步增加，但不会超过该设置的值。单位为秒。
# AUTOTHROTTLE_MAX_DELAY = 60

# 目标并发请求数
# 自动限速功能启用后，Scrapy 平均应同时发送到每个远程服务器的并发请求数。
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# 是否启用限速调试模式
# 如果设置为 True，则显示每个接收到的响应的限速统计信息。限速统计信息包括当前下载延迟、目标下载延迟、当前并发请求数等。如果设置为 False，则不显示限速统计信息。
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings

# 是否启用HTTP缓存
# 如果设置为 True，则启用HTTP缓存功能。启用HTTP缓存后，Scrapy将自动缓存HTTP响应，以便后续的请求可以直接从缓存中获取数据，而不必发送新的请求。
# HTTPCACHE_ENABLED = True

# 缓存过期时间（秒）
# 缓存的有效期时间，以秒为单位。默认情况下，缓存的响应将一直有效，除非服务器返回了"Cache-Control"或"Expires"标头指定的过期时间。
# HTTPCACHE_EXPIRATION_SECS = 0

# 缓存目录
# 缓存文件存储的目录路径。默认情况下，缓存文件将保存在名为 "httpcache" 的子目录下。
# HTTPCACHE_DIR = "httpcache"

# 忽略的HTTP响应状态码列表
# 列出应被忽略的HTTP响应状态码。当收到这些状态码的响应时，它们将不会被缓存。
# HTTPCACHE_IGNORE_HTTP_CODES = []

# 缓存存储方式
# 指定缓存存储方式。默认情况下，使用 "scrapy.extensions.httpcache.FilesystemCacheStorage" 存储方式，将缓存文件保存在本地文件系统中。你也可以自定义缓存存储方式。
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# ===================Log========================
# 日志
# LOG_ENABLED = True

# 配置日志格式
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

# 配置日志级别，默认为 DEBUG
LOG_LEVEL = logging.ERROR

# 配置日志文件名
LOG_FILE = f'../logs/scrapy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.makedirs(os.path.dirname(LOG_FILE))
# 配置日志输出
configure_logging(install_root_handler=False)
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler(LOG_FILE)  # 文件输出
    ]
)

# ===================Redis========================
# 启用Scrapy-Redis调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 启用Scrapy-Redis去重过滤器
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 设置Redis作为Scrapy-Redis调度器和去重过滤器的存储
REDIS_URL = 'redis://localhost:6379'
# 启用分布式爬虫，允许多个爬虫实例共享相同的队列
SCHEDULER_PERSIST = True
# 可选：设置Redis的其他配置，如密码等
REDIS_PARAMS = {
    'password': "",
}

# ===================Download========================
MEDIA_ALLOW_REDIRECTS = True  # 下载时允许重定向
FILES_STORE = 'ftp://admin:jkjkjkjk_LaimL.@222.222.222.2/photo/weibo-ftp'  # 通用文件（包括图片和视频）的保存路径
IMAGES_STORE = FILES_STORE
DOWNLOAD_FAIL_ON_DATALOSS = False  # 文件过大警告

SPIDER_BLOG_TYPE = "original"  # 爬取规则：original or forward
SPIDER_UID = "7367188627"  # cookie的uid
SPIDER_GROUP = "特别关注"  # 根据分组爬取

# ===================mongodb========================
MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'weibo'

