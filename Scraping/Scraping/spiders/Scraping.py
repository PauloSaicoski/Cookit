import scrapy
import re
from Scraping.items import Recipe
import json
import requests

class RecipeSpider(scrapy.Spider):
    name = "RecipeSpider"
    awllowed_domains = ['https://www.tudogostoso.com.br/']
    start_urls = ['https://www.tudogostoso.com.br/categorias/1004-carnes']
    listaIngredientes = list()

    def parse(self, response):
        for recipes in response.css('div.mb-3 a::attr(href)'):
            recipe_url = response.urljoin(recipes.get())
            if recipe_url is not None:
                # self.popula(response)
                yield scrapy.Request(recipe_url, callback=self.parse_dir_contents)
        next_page = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "next", " " ))]/@href').get()
        print("next_page: ", next_page)
        yield response.follow(next_page, callback=self.parse)

    def findIngredientInString(self, frase):
        lista = frase.split()
        espaco = " "
        for j in range(len(lista),0,-1):
            for i in range(0, j):
                if lista[i:j] in self.listaIngredientes:
                    # print("\n\n\n\n",espaco.join(lista[i:j]),"\n\n\n\n\n")
                    return espaco.join(lista[i:j])
        # print("None")
        return None

    def parse_dir_contents(self, response):
        regraName = re.compile("(\\n)*(.+)(\\n)*")
        regraInt = re.compile("\\n(\d+(.\d*)?)\\n")
        regraPortions = re.compile("\\n(\d+) p")
        r = Recipe()
        # print("\n\n",, ,"\n\n")
        # titulo = regraName.match(response.css("title::text").get())
        r['name'] = regraName.match(response.xpath("//h1/text()").get()).group(2)
        r['author'] = regraName.match(response.xpath('//*[(@class="author-name")]//span/text()').get()).group(2)
        r['imgUrl'] = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "pic", " " ))]/@src').get()
        r['preptime'] = int(regraInt.match(response.css("time.dt-duration::text").get()).group(1).replace(".",""))
        r['portions'] = int(regraPortions.match(response.css("data.p-yield.num.yield::text").get()).group(1))
        r['likes'] = int(regraInt.match(response.css(".num::text")[4].get()).group(1).replace(".",""))
        # r['comments'] = int(regraInt.match(response.css(".num::text")[5].get()).group(1).replace(".",""))
        r['ingredients'] = response.xpath('//*[(@itemprop="recipeIngredient")]//p/text() | //*[contains(concat( " ", @class, " " ), concat( " ", "p-ingredient", " " ))]/text()').getall()
        regraIngrediente = re.compile(r"\d+((\se\s\d/\d)|(/\d)(\s+de)?)?(\s+\w+((\s+de\s+sopa)|(\s+\(.+\)))?(\s+de))?\s+(?P<ingrediente>(\w|-)+(\s+\w+)*)(\s+\(.+\))?$")
        aGosto = re.compile("a gosto")
        i = 0
        while i < len(r['ingredients']):
            r['ingredients'][i] = r['ingredients'][i].replace("\xa0", "")
            match = regraIngrediente.match(r['ingredients'][i])
            if aGosto.search(r['ingredients'][i]) is not None:
                r['ingredients'].remove(r['ingredients'][i])
                i-=1
            elif match:
                r['ingredients'][i] = match.group('ingrediente')
                self.listaIngredientes.append(r['ingredients'][i])
            else:
                result = self.findIngredientInString(r['ingredients'][i])
                if result is not None:
                    r['ingredients'][i] = result
            i+=1

        r['url'] = response.url
        
        recipe = {"name": r['name'], "author" : r['author'], "imgUrl" : r['imgUrl'], "preptime": r['preptime'], "portions": r['portions'], "likes": r['likes'], "ingredients": json.dumps(r['ingredients'], ensure_ascii=False), "url": r['url']}
        # requests.post('https://cookitweb.herokuapp.com/recipe', data=recipe)
        requests.post('http://localhost:5000/recipe', data=recipe)
        
        yield r
        #scrapy.Request('https://cookitweb.herokuapp.com/recipe', callback=self.parse_dir_contents)

        # for related in response.css('div.col-lg-6 a::attr(href)'):
        #     next_page = related.get()
        #     if next_page is not None:
        #         yield response.follow(next_page, callback=self.popula)
        #     print(related.get())


