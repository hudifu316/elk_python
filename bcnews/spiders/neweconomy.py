import scrapy
from bcnews.items import BcnewsItem

class NeweconomySpider(scrapy.Spider):
    name = 'neweconomy'
    allowed_domains = ['www.neweconomy.jp']
    start_urls = ['https://www.neweconomy.jp/categories/news']

    def parse(self, response):
        # ニュースカテゴリから個々のニュースへのリンクを抜き出す
        for url in response.css('div.p-article__inner > a::attr("href")').extract():
            yield scrapy.Request(response.urljoin(url), self.parse_topics)

    def parse_topics(self, response):
        item = BcnewsItem()
        item['date'] = response.css('time.p-hero__time').re(r'\d{4}-\d{2}-\d{2}')
        item['title'] = response.css('h1::text').extract_first()
        item['body'] = ''.join(response.css('.p-articleContent__contents > p::text, span::text').extract())
        item['link'] = response.url
        yield item

