# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request

from zhihuuser.items import UserItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    offset = 0
    limit = 20

    # 以轮子哥的账户作为起始账户
    start_user = 'excited-vczh'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,' \
                 'articles_count,gender,badge[?(type=best_answerer)].topics'

    # 关注列表接口地址
    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followees_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,' \
                      'badge[?(type=best_answerer)].topics '

    # 粉丝列表接口地址
    fllowers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include{include}&offset={offset}&limit={' \
                   'limit} '
    fllowers_query = 'data[*].gender,answer_count,articles_count,follower_count,is_following,is_followed'

    def start_requests(self):
        """
        1.获取用户信息
        2.获取关注列表
        3.获取粉丝列表
        :return:
        """
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse_user)
        yield Request(self.fllowers_url.format(user=self.start_user, include=self.fllowers_query, offset=self.offset,
                                               limit=self.limit), callback=self.parse_follows)
        yield Request(self.followees_url.format(user=self.start_user, include=self.followees_query, offset=self.offset,
                                                limit=self.limit), callback=self.parse_follows)

    def parse_user(self, response):
        """
        1.解析用户详细信息
        2.获取用户的关注列表，进行下一步递归调用
        3.获取用户的粉丝列表，进行下一步递归调用
        :param response:
        :return:
        """
        with open('data/user.html', 'w') as f:
            f.write(response.text)

        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

        yield Request(
            self.fllowers_url.format(user=result.get('url_token'), include=self.fllowers_query, offset=self.offset,
                                     limit=self.limit), callback=self.parse_follows)
        yield Request(
            self.followees_url.format(user=result.get('url_token'), include=self.fllowers_query, offset=self.offset,
                                      limit=self.limit), callback=self.parse_follows)

    def parse_follows(self, response):
        """
        1.解析关注列表或者粉丝列表，获取 url_token，通过 url_token 获取用户详细信息，进行递归调用
        2.递归分页
        :param response:
        :return:
        """
        with open('data/follows.html', 'w') as f:
            f.write(response.text)

        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              callback=self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') is False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_follows)
