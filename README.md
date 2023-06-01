<a href="https://github.com/jkfaner/WeiboSpider">
 <img alt="weibo-spider-Logo" src="assets/image/icons8-微博.svg">
</a>

# WeiboSpider

> 微博爬虫分布式系统，高效率博主图片视频爬取。数据接口均来自weibo.com
- 单机版：https://github.com/jkfaner/WeiboSpider
- 分布式版：https://github.com/jkfaner/WeiboSpiderX

[![GitHub stars](https://img.shields.io/github/stars/jkfaner/apple-monitor.svg)](https://github.com/jkfaner/apple-monitor)

### 功能
微博数据采集

### 更新

- 20230601：实现数据增量式采集，已采集过的数据不再采集，执行效率更高
- 20230523：取消自定义用户，更改为爬取特别关注
- 20230522：可自定义博主
- 20230521：实现博主的媒体数据采集，包括但不限于图片、视频、live图片

### 使用说明

1. 环境支持

```
- python 3 # 脚本执行环境
- redis # 缓存
```

2. 依赖安装
3. 可直接执行run.py 或 修改并执行`run.sh`
#### 部署
- Gerapy客户端
```angular2html
pip install gerapy
gerapy init
cd gerapy
gerapy migrate
gerapy createsuperuser
gerapy runserver
```
- 服务端
```angular2html
pip install scrapyd
scrapyd
```
### 参考

- 部分脚本代码由chatGPT生成
- https://github.com/dataabc/weiboSpider
- https://github.com/CharlesPikachu/DecryptLogin
- https://github.com/kingname/JsonPathFinder

### 鸣谢

<a target="_blank" href="https://icons8.com/icon/20910/微博">微博</a> icon by <a target="_blank" href="https://icons8.com">
Icons8</a>

### 支持

<p align="center">
  <a href="https://github.com/jkfaner/apple-monitor/blob/master/image/sponsor.jpg">
   <img alt="apple-monitor" src="https://github.com/jkfaner/apple-monitor/blob/master/image/sponsor.jpg">
  </a>
</p>