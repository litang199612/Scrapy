# -*- coding: utf-8 -*-
import base64

import scrapy
from scrapy import Request
from tenement.items import TenementItem
import sqlite3

db = sqlite3.connect("./../tenement.db")
cursor = db.cursor()

i = 0


def select_from_sql():
    """
    :return: 当前数据库中数据的总数
    """
    count = cursor.execute("select * from house")
    return len(count.fetchall())


class HouseSpider(scrapy.Spider):
    name = 'house'
    # allowed_domains = ['sh.58.com/']
    # start_urls = ['https://sh.zu.anjuke.com']

    def start_requests(self):
        url_str = 'https://sh.58.com/chuzu/?PGTID=0d0090a7-0000-05a3-03cc-ad6f70708357&ClickID=1'
        yield Request(url=url_str, callback=self.parse, meta={'page': '0'})

    def parse(self, response):
        """
        解析出房源的url以及下一页的url
        :param response:
        :return:
        """
        all_href = response.xpath('//div[@class="img_list"]/a/@href').extract()
        next_page = response.xpath('//a[@class="next"]/@href').extract_first()
        href_count = len(all_href)

        for href in all_href:
            yield Request(url='https:' + href, callback=self.parse_one_house, meta={'next_page': next_page, 'href_count': href_count, 'page': '0'})

    def parse_one_house(self, response):
        """
        通过xpath获取租金，租赁方式，房屋类型，朝向楼层，所在小区，所属区域，详细地址等信息
        :param response:
        :return:
        """
        global i
        next_page = response.meta['next_page']
        href_count = response.meta['href_count']
        count = select_from_sql()

        if len(response.text.split("base64,")) > 1:
            base64_string = response.text.split("base64,")[1].split("'")[0].strip()
            bin_data = base64.decodebytes(base64_string.encode())
            with open("base.woff", r"wb") as f:
                f.write(bin_data)

        rental = response.xpath('//div[@class="house-desc-item fl c_333"]/div[@class="house-pay-way f16"]/span[1]/b/text()').extract_first()
        lease_way = response.xpath('//ul[@class="f14"]/li[1]/span[2]/text()').extract_first()
        house_type = response.xpath('normalize-space(//ul[@class="f14"]/li[2]/span[2]/text())').extract_first()
        toward_floor = response.xpath('normalize-space(//ul[@class="f14"]/li[3]/span[2]/text())').extract_first()
        housing_estate = response.xpath('//ul[@class="f14"]/li[4]/span[2]/a[@class="c_333 ah"]/text()').extract_first()
        region = response.xpath('//ul[@class="f14"]/li[5]/span[2]/a/text()').extract_first()
        address = response.xpath('normalize-space(//ul/li[6]/span[2]/text())').extract_first()

        item = TenementItem()
        item["rental"] = rental
        item["lease_way"] = lease_way
        item["house_type"] = house_type
        item["toward_floor"] = toward_floor
        if housing_estate:
            item["housing_estate"] = housing_estate
        else:
            item["housing_estate"] = "无"
        item["region"] = region
        item["address"] = address
        item["url"] = next_page

        # if count - i >= href_count - 1:
        if next_page:
            i = count
            yield Request(url=next_page, callback=self.parse, meta={"page": "2"}, dont_filter=True)

        yield item

