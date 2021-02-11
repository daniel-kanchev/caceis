import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from caceis.items import Article


class CacSpider(scrapy.Spider):
    name = 'cac'
    start_urls = ['https://www.caceis.com/whats-new/news/']

    def parse(self, response):
        links = response.xpath('//div[@itemtype="http://schema.org/Article"]//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="last next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="page-title-date"]/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%m/%d/%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@itemprop="articleBody"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        category = ",".join(response.xpath('//span[@class="page-title-taglist"]/a/text()').getall())

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('category', category)

        return item.load_item()
