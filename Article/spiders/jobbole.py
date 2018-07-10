# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse  # 如果url不是完整的就加上这个
from Article.items import JobboleItem


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1获取文章列表中的url并交给解析函数做具体的字段的解析
        2获取下一页的url并交给scrapy下载
        """
        # 1获取文章列表中的url并交给解析函数做具体的字段的解析
        # //div[@id="archive"]//div//div/a/@href
        all_nodes = response.xpath('//div[@id="archive"]//div//div/a')
        for everynode in all_nodes:
            # 如果url是完整的就这样写
            # yield Request(url=post_url, callback=self.parse_detail)
            # 如果url不是完整的就这样写

            post_url = everynode.xpath("./@href").extract_first("")
            img_url = everynode.xpath("./img/@src").extract_first("")

            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_img_url": img_url}, callback=self.parse_detail)

        # 2获取下一页的url并交给scrapy下载
        next_url = response.xpath("//a[@class='next page-numbers']/@href").extract_first("")
        if next_url:
            # yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)
            yield Request(url=next_url, callback=self.parse)

    def parse_detail(self, response):
        jobboleItem = JobboleItem()
        front_img_url = response.meta.get("front_img_url", "")
        # 提取具体字段
        # //*[@id="post-114164"]/div[1]/h1
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract_first(
            "").strip().replace("·", "").strip()
        likes = response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()")

        # create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip(
        # ).replace("·","").strip() extract()[0]数组有可能为空可能抛异常  等于extract——first()不用抛异常 print(create_date)
        jobboleItem["title"] = title
        jobboleItem["create_date"] = create_date
        jobboleItem["likes"] = likes
        jobboleItem["front_img_url"] = [front_img_url]
        yield jobboleItem
