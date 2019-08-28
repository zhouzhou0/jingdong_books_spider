# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from copy   import deepcopy
import urllib

class DangdangSpider(RedisSpider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    # start_urls = ['http://book.dangdang.com/']
    redis_key="dangdang"
    def parse(self, response):
        #大分类分组
        div_list=response.xpath("//div[@class='con flq_body']/div")
        for div in div_list:
            item={}
            item['big_cate']=div.xpath("./dl/dt//text()").extract()
            item['big_cate']=[i.strip() for i in item['big_cate'] if len(i.strip())>0]
            #中间分类分组
            dl_list=div.xpath("./div//dl[@class='inner_dl']")
            for dl in dl_list:
                item['middle_cate']=dl.xpath("./dt//text()").extract()
                item['middle_cate']=[i.strip() for i in item['middle_cate'] if len(i.strip())>0][0]
                #小分类分组
                a_list=dl.xpath("./dd/a")
                for a in a_list:
                    item['small_href']=a.xpath("./@href").extract_first()
                    item['small_cate']=a.xpath("./text()").extract_first()
                    if item['small_href'] is not None:
                        yield scrapy.Request(
                            item['small_href'],
                            callback=self.parse_book_list,
                            meta={"item":deepcopy(item)}
                        )

    def parse_book_list(self,response):
        item=response.meta['item']
        li_list=response.xpath("//ul[@class='bigimg']/li")
        for li in li_list:
            item["book_img"]=li.xpath("./a[@class='pic']/img/@data-original").extract_first()
            item["book_name"]=li.xpath("./p[@class='name']/a/@title").extract_first()
            item["book_desc"]=li.xpath("./p[@class='detail']/text()").extract_first()
            item["book_price"]=li.xpath("//span[@class='search_now_price']/text()").extract_first()
            item['book_author']=li.xpath("./p[@class='search_book_author']/span[1]/a/text()").extract()
            item['book_publish_data'] = li.xpath("./p[@class='search_book_author']/span[2]/text()").extract_first()
            item['book_press'] = li.xpath("./p[@class='search_book_author']/span[3]/a/text()").extract_first()

            print(item)
        #下一页
        next_url=response.xpath("//li[@class='next']/a/@href").extract_first()
        if next_url is not  None:
            next_url=urllib.parse.urljoin(response.url,next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item':item}
            )
            yield item