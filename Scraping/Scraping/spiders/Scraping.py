import scrapy
import re
from Scraping.items import Recipe

class RecipeSpider(scrapy.Spider):
    name = "RecipeSpider"
    awllowed_domains = ['https://www.tudogostoso.com.br/']
    start_urls = ['https://www.tudogostoso.com.br/receitas.html']

    def parse(self, response):
        for recipes in response.css('div.mb-3 a::attr(href)'):
            recipe_url = response.urljoin(recipes.get())
            if recipe_url is not None:
                # self.popula(response)
                yield scrapy.Request(recipe_url, callback=self.parse_dir_contents)
        print("\n\n\n\nnext\n")
        next_page = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "next", " " ))]/@href').get()
        print(next_page)
        print("\n\n\n\nnext\n")
        yield response.follow(next_page, callback=self.parse)
                
    def parse_dir_contents(self, response):
        print("\n\n\n\n", "a", "\n\n\n\n")
        regraName = re.compile("\\n(.+), enviada por (.+) - TudoGostoso\\n")
        regraInt = re.compile("\\n(\d+(.\d*)?)\\n")
        regraPortions = re.compile("\\n(\d+) p")
        r = Recipe()
        r['name'] = regraName.match(response.css("title::text").get()).group(1)
        r['prepTime'] = int(regraInt.match(response.css("time.dt-duration::text").get()).group(1).replace(".",""))
        r['portions'] = int(regraPortions.match(response.css("data.p-yield.num.yield::text").get()).group(1))
        r['likes'] = int(regraInt.match(response.css(".num::text")[4].get()).group(1).replace(".",""))
        r['comments'] = int(regraInt.match(response.css(".num::text")[5].get()).group(1).replace(".",""))
        r['ingredients'] = response.xpath('//*[(@itemprop="recipeIngredient")]//p/text()').getall()
        

        r['url'] = response.url
        r['project'] = self.settings.get('BOT_NAME')
        r['spider'] = self.name
        
        yield r
        # print("##############PRINTANDO##############")
        # for related in response.css('div.col-lg-6 a::attr(href)'):
        #     next_page = related.get()
        #     if next_page is not None:
        #         yield response.follow(next_page, callback=self.popula)
        #     print(related.get())


