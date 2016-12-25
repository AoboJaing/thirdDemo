# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from thirdDemo.items import ThirddemoItem
import urllib

class TaobaoSpider(scrapy.Spider):
    name = "taobao"
    allowed_domains = ["taobao.com"]
    start_urls = ['http://taobao.com/']

    def parse(self, response):
        key = '小吃'
        for i in range(0, 2):
            url = 'https://s.taobao.com/search?q=' + str(key) + '&s=' + str(44*i)
            print(url)
            yield Request(url=url, callback=self.page)
        pass

    def page(self, response):
        body = response.body.decode('utf-8','ignore')
        pattam_id = '"nid":"(.*?)"'
        all_id = re.compile(pattam_id).findall(body)
        # print(all_id)
        # print(len(all_id))
        for i in range(0, len(all_id)):
            this_id = all_id[i]
            url = 'https://item.taobao.com/item.htm?id=' + str(this_id)
            yield Request(url=url, callback=self.next)
            pass
        pass


    def next(self, response):
        item = ThirddemoItem()
        # print(response.url)
        url = response.url
        # 获取商品是属于天猫的、天猫超市的、还是淘宝的。
        pattam_url = 'https://(.*?).com'
        subdomain = re.compile(pattam_url).findall(url)
        # print(subdomain)

        # 获取商品的标题
        if subdomain[0] != 'item.taobao': # 如果不属于淘宝子域名，执行if语句里面的代码
            title = response.xpath("//div[@class='tb-detail-hd']/h1/text()").extract()
            pass
        else:
            title = response.xpath("//h3[@class='tb-main-title']/@data-title").extract()
            pass
        # print(title)
        item['title'] = title
        # print(item['title'])

        # 获取商品的链接网址
        item['link'] = url

        # 获取商品的正常的价格
        if subdomain[0] != 'item.taobao': # 如果不属于淘宝子域名，执行if语句里面的代码
            pattam_price = '"defaultItemPrice":"(.*?)"'
            price = re.compile(pattam_price).findall(response.body.decode('utf-8', 'ignore')) # 天猫
            pass
        else:
            price = response.xpath("//em[@class = 'tb-rmb-num']/text()").extract() # 淘宝
            pass
        # print(price)
        item['price'] = price

        # 获取商品的id（用于构造商品评论数量的抓包网址）
        if subdomain[0] != 'item.taobao': # 如果不属于淘宝子域名，执行if语句里面的代码
            pattam_id = 'id=(.*?)&'
            pass
        else:
            # 这种情况（只有上文没有下文）时，使用正则表达式，在最末端用 $ 表示
            pattam_id = 'id=(.*?)$'
            pass
        this_id = re.compile(pattam_id).findall(url)[0]
        # print(this_id)
        # 构造具有评论数量信息的包的网址
        comment_url = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=' + str(this_id)

        # 这个获取网址源代码的代码永远也不会出现错误，因为这个URL的问题，就算URL是错误的，也可以获取到对应错误网址的源代码。
        # 所以不需要使用 try 和 except urllib.URLError as e 来包装。
        comment_data = urllib.request.urlopen(comment_url).read().decode('utf-8', 'ignore')
        pattam_comment = '"rateTotal":(.*?),"'
        comment = re.compile(pattam_comment).findall(comment_data)
        # print(comment)
        item['comment'] = comment
        yield item
