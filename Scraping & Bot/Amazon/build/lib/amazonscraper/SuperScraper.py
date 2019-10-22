#%%
import os
import csv
import json
import time
import requests
import itertools
import numpy as np
import pandas as pd
from tqdm import tqdm
from lxml import html, etree
from random import randint, choice, shuffle
# from tqdm import tqdm_notebook as tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options, DesiredCapabilities
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException, WebDriverException, ElementNotInteractableException
# from selenium.webdriver.common.proxy import Proxy, ProxyType

class Error(Exception):
    pass
class AccessDenied(Error):
    def __init__(self, message='Access Denied'):
        self.message = message
class Inaccessible(Error):
    def __init__(self, message='Page Inaccessible'):
        self.message = message
class AucuneConnexion(Error):
    def __init__(self, message='Aucune Connexion'):
        self.message = message
class AmazonError(Error):
    def __init__(self, message='Honey Pot'):
        self.message = message

class SuperScraper:
    """
    - items : Dictionary of xpath to be parsed (ex: {'name': 'xpath'})
    - path : Path of the backup to be loaded
    - urls : List of urls to be scraped. If urls sitemap must be None. If None, 
             will load urls from urls folder if exists
    - user_agents : List of user agent to use. If None, will scrap user agents from: 
                    https://developers.whatismybrowser.com/useragents/explore/software_name/chrome
    - proxy : Bool. If True, will use proxy scraped from : https://free-proxy-list.net/
    - namespace : namespace to be used with sitemap. Sitemap must not be None
    - sitemap : List of sitemap urls to use. If sitemap, urls must be None.
    - sleep : Tuple. min and max time to wait between two requests.
    """
    
    chrome_options = webdriver.ChromeOptions()
    caps = DesiredCapabilities().CHROME
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument("--start-maximized")
    caps["pageLoadStrategy"] = "none"
    log = pd.DataFrame(columns=['TIME', 'TYPE', 'MESSAGE'])
    log.to_csv('log.csv', sep=';', index=False, mode='a')
#     chrome_options.add_argument("log-level=3")
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--incognito")
#     chrome_options.add_argument('--disable-extensions')
#     chrome_options.add_argument("--disable-plugins-discovery");
#     caps["pageLoadStrategy"] = "eager"
#     args = ["--log-path=logfile.log"]
    
    def __init__(self, items:dict, path:str, urls:list= None, user_agents:list= None,
                 proxy:bool= False, namespaces:str= None, sitemap:list= None, sleep=(2,4)):
        self.items:dict = items
        self.path:str = path
        self.urls:list = urls
        self.ua_list:list = user_agents
        self.proxy:bool = proxy
        self.namespaces:str = namespaces
        self.sitemap:list = sitemap
        self.sleep = sleep

    def get_urls(self):
        url_list = []
        if self.sitemap:
            print('Getting URLs')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','Getting URLs']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
            ns = {"d": self.namespaces}
            for i in range(len(self.sitemap)):
                r = requests.get(self.sitemap[i])
                root = etree.fromstring(r.content)
                url_list = url_list + root.xpath("//d:loc/text()", namespaces=ns)
            np.savetxt("./urls/url_list.csv", url_list, delimiter=",", fmt='%s')
            print('Urls loaded')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Urls loaded: {len(url_list)}']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        elif self.urls:
            url_list = self.urls
            print('Urls loaded')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Urls loaded: {len(url_list)}']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        elif self.urls is None:
            url_list = pd.read_csv("./urls/url_list.csv", header=None)[0].to_list()
            print('Urls loaded')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Urls loaded: {len(url_list)}']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        else:
            print('No URLs to load')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','No URLs to load']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        return url_list
    
    def get_proxies(self):
        url = 'https://free-proxy-list.net/'
        driver = requests.get(url)
        parser = html.fromstring(driver.content)
        proxies = []
        for i in parser.xpath('//tbody/tr'):
            if i.xpath('.//td[5][contains(text(),"elite") or contains(text(),"anonymous")]'):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0],i.xpath('.//td[2]/text()')[0]])
                proxies.append(proxy)
                shuffle(proxies)
        print('Proxies loaded')
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Proxies loaded: {len(proxies)}']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        return proxies

    def get_user_agent(self):
        if self.ua_list:
            ua_list = self.ua_list
            print('User-agents Loaded')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'User-agents loaded : {len(ua_list)}']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        else:
            print('Getting user-agent')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','Getting user-agents']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
            while True:
                try:
                    ua_list = []
                    driver = webdriver.Chrome()
                    for i in range(1,6):
                        driver.get(f'https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/{i}')
                        print(driver.current_url)
                        parser = html.fromstring(driver.page_source)
                        for j in range(1,51):
                            ua_list.append(parser.xpath(f'/html/body/div[2]/section/div/table/tbody/tr[{j}]/td[1]/a/text()')[0])
                        time.sleep(randint(2,3))
                    break
                    
                except Exception as e:
                    print(e)
                    self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e]
                    self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                    driver.quit()
            driver.quit()
            print('User-agents loaded')  
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'User-agents loaded : {len(ua_list)}']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        return list(set(ua_list))
