#!/bin/sh

# 开启虚拟环境
source ~/.xuni/py3SpiderEnv/bin/activate

# 进入WeiboSpiderX
cd ~/PycharmProjects/Spider/WeiboSpiderX

# 执行Scrapy命令
scrapy crawl weibo