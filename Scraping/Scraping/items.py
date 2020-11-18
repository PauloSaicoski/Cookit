# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ExampleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewItem(scrapy.Item):
    name = scrapy.Field()
    text = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()
    project = scrapy.Field()
    spider = scrapy.Field()

class Recipe(scrapy.Item):
    name = scrapy.Field()
    prepTime = scrapy.Field()
    portions = scrapy.Field()
    likes = scrapy.Field()
    comments = scrapy.Field()

    ingredients = scrapy.Field()

    url = scrapy.Field()
    project = scrapy.Field()
    spider = scrapy.Field()

class Test(scrapy.Item):
    names = scrapy.Field()
