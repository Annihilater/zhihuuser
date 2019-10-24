#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019/10/24 11:00
# @Author: yanmiexingkong
# @email : yanmiexingkong@gmail.com
# @File  : zhihu_spider.py
from scrapy import cmdline

cmdline.execute('scrapy crawl zhihu'.split())
