"""
root : Must be given by the user. Is the root url from all categories and subcategories to scrap. 
Example: (2019/09/12)
    root for Furniture category : https://www.amazon.com/s?i=kitchen-intl-ship&bbn=16225011011&rh=n%3A%2116225011011%2Cn%3A1063306&s=price-desc-rank&lo=list&dc&_encoding=UTF8&qid=1566148253&rnid=16225011011&ref=sr_nr_n_5
    - List of categories:
        - Bedroom Furniture:
            (subcategories of Bedromm Furniture)
            - Beds, Frames & Bases
            - Bedroom Armoires
            - Dressers
            - Mattresses & Box Springs
            - Nightstands
            - Vanities & Vanity Benches
            - Bedroom Sets
            - Quilt Stands
        - Living Room Furniture
        - Kitchen & Dining Room Furniture
        - Home Office Furniture
        - Kids' Furniture
        - Entryway Furniture
        - Game & Recreation Room Furniture
        - Bathroom Furniture
        - Nursery Furniture
        - Accent Furniture
        - Replacement Parts

"""

import amazonscraper as ams
import pandas as pd
import json
import time
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException

def get_link_by_text(text):
    """Find link in the page with given text"""
    element = driver.find_element_by_link_text(text.strip())
    return element.get_attribute("href")

def get_list_by_xpath(xpath):
    """Get list of text in all element by xpath"""
    try:
        driver.implicitly_wait(15)
        all_categories = driver.find_elements_by_xpath(xpath)
        categorie_list = [x.text for x in all_categories if len(x.text) > 0]
    except (NoSuchElementException, WebDriverException) as e:
        print(e)
    return categorie_list

if __name__ == '__main__':

    root = 'https://www.amazon.com/s?i=kitchen-intl-ship&bbn=16225011011&rh=n%3A%2116225011011%2Cn%3A1063306&s=price-desc-rank&lo=list&dc&_encoding=UTF8&qid=1566148253&rnid=16225011011&ref=sr_nr_n_5'
    driver = webdriver.Chrome()
    driver.get(root)

    # Extract categories link (mapping)
    category_links = {x: get_link_by_text(x) for x in get_list_by_xpath('//*[@id="departments"]/ul/li/span/a')}
    del category_links[list(category_links.keys())[0]]
    driver.quit()
    os.system('taskkill /im chromedriver.exe /f')

    ## Extract sub-categories link (mapping)
    sub_category_links = {}
    for category, url in category_links.items():
        driver.get(url)
        time.sleep(2)
        sub_category_links[category] = {x: get_link_by_text(x) for x in get_list_by_xpath('//*[@id="departments"]/ul/li/span/a')[2:]}

    # Save mapping
    with open('./urls/category_links.json', 'w') as fp:
        json.dump(category_links, fp)
        fp.close()

    with open('./urls/sub_category_links.json', 'w') as fp:
        json.dump(sub_category_links, fp)
        fp.close()
