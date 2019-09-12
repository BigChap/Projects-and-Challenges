"""
Nothing to change in this file, just infor the parameters and run it.
"""

import amazonscraper as ams
import pandas as pd
import json
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException

if __name__ == '__main__':

    # Load categories mapping
    with open('./urls/category_links.json', 'r') as fp:
        category_links = json.load(fp)
        fp.close()

    # Extract all links from the mapping :
    namespaces = "http://www.sitemaps.org/schemas/sitemap/0.9"
    path = './urls/url_list.csv'
    ua_list = pd.read_csv('user_agent.csv', header=None)[0].to_list()

    page_object = "//*[@data-asin]"
    items = {
        'root': 'https://www.amazon.com/dp/',
        'asin': '//*[@data-asin]/@data-asin',
        'nxt_page': '//ul[@class="a-pagination"]/li[last()]/a'}

    amazon_links = ams.LinkExtractor(items=items, path=path, page_object= page_object, category_links= category_links, user_agents=ua_list, proxy=True)
    amazon_links.start()

