"""
This file will scrap products pages.
Just inform the parameters of the function and run the file.

- namespace : Is the name space of XML pages. Not supposed to change.
- path : Path of the backup.csv file to be saved/loaded. Must be given by the user.
- url_list : urls list to load from ./urls/url_list.csv. If not given, must run mapSite.py and extractLinks.py first.
- ua_list : user agent list to load from ./user_agent.csv. If not given, will automatically scrap user agent from website (cf. SuperScraper from package).
- page_object : xpath of the most important element to be scrap on products pages. Might change as Amazon website changes. 
                Must be given by the user and will affect the wait time on page.
- items : Dictionnary of element to be scrap on products pages. Might change as Amazon website changes. Must be given by the user.
"""

import amazonscraper as ams
import pandas as pd
import os

if __name__ == '__main__':

    # Extract data from links
    namespaces = "http://www.sitemaps.org/schemas/sitemap/0.9"
    path = r'C:\Users\sebastien.chapeland\OneDrive - Ekimetrics\R&D\backup.csv'

    url_list = pd.read_csv('./urls/url_list.csv', sep='@', skiprows=[1], header=0).Link.to_list()
    ua_list = pd.read_csv('user_agent.csv', header=None)[0].to_list()

    page_object = '//*[(@id = "imgTagWrapperId")]/img'
    items = {
        'name': '//*[@id="productTitle"]/text()',
        'salePrice': '//*[@id="priceblock_ourprice"]/text()',
        'rating': '//*[@id="acrPopover"]/span[1]/a/i[1]/span/text()',
        'reviews_count': '//*[@id="acrCustomerReviewText"]/text()',
        'short_description': '//*[@id="feature-bullets"]/ul/child::li/span/text()',
        'long_description': '//*[(@id = "aplus")]//p/text()',
        'product_info_col1' : '//*[@id="productDetails_detailBullets_sections1"]/tbody/child::tr/th/text()',
        'product_info_col2' : '//*[@id="productDetails_detailBullets_sections1"]/tbody/child::tr/td/text()',
        'top_reviews' : '//*[@data-hook="top-customer-reviews-widget"]//*/div/span/text()',
        'image': '//*[(@id = "imgTagWrapperId")]/img/@src',
            }

    scraper_amazon = ams.Scraper(items=items, path=path, urls=url_list, user_agents=ua_list, proxy=True, namespaces=namespaces, page_object=page_object)
    scraper_amazon.start()
