# -*- coding: utf-8 -*-
import scrapy
import urllib
from copy   import deepcopy
import re
import json
class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['jd.com','p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        dt_list=response.xpath("//div[@class='mc']//dt")#大分类列表
        for dt in dt_list:
            item={}
            item['b_cate']=dt.xpath("./a/text()").extract_first()
                            #取兄弟节点
            em_list=dt.xpath("./following-sibling::dd[1]/em")#小分类
            for em in em_list:
                item['s_href']=em.xpath("./a/@href").extract_first()
                item['s_cate']=em.xpath("./a/text()").extract_first()
                if item['s_href'] is not None:
                    item['s_href']='https:'+item['s_href']
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_book_list,
                        meta={'item':deepcopy(item)}
                    )

    def parse_book_list(self,response):#解析列表页
        item=response.meta['item']
        li_list=response.xpath("//div[@id='plist']/ul[contains(@class,gl-warp)]/li")
        for li in li_list:
            item['book_img']=li.xpath(".//div[@class='p-img']//img/@src").extract_first()
            if item['book_img'] is None:
                item['book_img']=li.xpath(".//div[@class='p-img']//img/@data-lazy-img").extract_first()
            item['book_img']=urllib.parse.urljoin(response.url,item['book_img'])
            item['book_name']=li.xpath(".//div[@class='p-name']/a/em/text()").extract_first()
            item['book_name']=item['book_name'].strip()
            item['book_author']=li.xpath(".//div[@class='p-bookdetails']//span[@class='author_type_1']/a/text()").extract()
            item['book_press']=li.xpath(".//div[@class='p-bookdetails']//span[@class='p-bi-store']/a/@title").extract_first()
            item["book_publist_data"]=li.xpath(".//div[@class='p-bookdetails']//span[@class='p-bi-date']/text()").extract_first().strip()
            item['book_sku']=li.xpath("./div/@data-sku").extract_first()
            yield scrapy.Request(
                "https://p.3.cn/prices/mgets?skuIds=J_{}".format(item['book_sku']),
                callback=self.parse_book_price,
                meta={'item':deepcopy(item)}
            )
            yield scrapy.Request(
                "https://sclub.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1".format(item['book_sku']),
                callback=self.pares_book_comment,
                meta={'item':deepcopy(item)}
            )
        #列表页翻页
        next_url=response.xpath("//a[@class='pn-next']/@href").extract_first()
        if next_url is not None:
            next_url=urllib.parse.urljoin(response.url,next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item':deepcopy(item)}
            )
    def parse_book_price(self,response):
        item=response.meta['item']

        item['price']=json.loads(response.body.decode())[0]['op']

        print(item)
        yield item
    def pares_book_comment(self,response):
        pass
        item=response.meta['item']
        # a=response.body.decode("gbk")
        # if a is not None:
        #     comment=json.loads(a)["comments"]
        #     if comment is not None:
        #         item['comment']=[]
        #         for i in comment:
        #             item['comment'].extend(i['content'])
        #
        # print(item)
        # yield item
