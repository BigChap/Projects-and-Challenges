"""I have to make docstring but I'm lazy"""

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
class HoneyPot(Error):
    def __init__(self, message='Honey Pot'):
        self.message = message
class Captcha(Error):
    def __init__(self, message='Captcha'):
        self.message = message



class SuperScraper:
    """
    - items : Dictionary of xpath to be parsed (ex: {'name': 'xpath'}).

    - path : Path of the backup to be saved/loaded.

    - page_object : xpath of the most important object to scrap on the page.
                    Will affect the waiting time for page elements

    - urls : List of urls to be scraped. If urls are given, sitemap must be None.
             If None, will search urls from urls folder in the main folder if exists.

    - user_agents : List of user agent to use from .csv in main folder. If None, will scrap user agents from
                    https://developers.whatismybrowser.com/useragents/explore/software_name/chrome

    - proxy : Bool. If True, will use proxy scraped from https://free-proxy-list.net/
                    If False, won't use any proxy.

    - namespace : Namespace to be used with sitemap. Sitemap list must be given

    - sitemap : List of sitemap urls to used. If sitemap, urls must be None.

    - sleep : Tuple. min and max time to wait between two requests.
    """
    
    chrome_options = webdriver.ChromeOptions()
    caps = DesiredCapabilities().CHROME
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument("--start-maximized")
    caps["pageLoadStrategy"] = "none"
    log = pd.DataFrame(columns=['TIME', 'TYPE', 'MESSAGE'])
    
    def __init__(self, items:dict, page_object:str, path:str, urls:list= None, user_agents:list= False,
                 proxy:bool= False, namespaces:str= None, sitemap:list= None, sleep:tuple=(2,4)):
        self.items:dict = items
        self.path:str = path
        self.urls:list = urls
        self.ua_list:list = user_agents
        self.proxy:bool = proxy
        self.page_object:str = page_object
        self.namespaces:str = namespaces
        self.sitemap:list = sitemap
        self.sleep:tuple = sleep

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
        else:
            try:
                url_list = pd.read_csv("./urls/url_list.csv", header=None)[0].to_list()
                print('Urls loaded')
                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Urls loaded: {len(url_list)}']
                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
            except:
                print('No URLs to load')
                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','No URLs to load']
                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        return url_list
    
    def get_proxies(self):
        url = 'https://free-proxy-list.net/'
        while True:
            try:
                driver = requests.get(url, timeout=10)
                break
            except Exception as e:
                print(e)
                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e]
                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
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

    def _start_driver(self, proxy_pool=None):
        if self.proxy:
            try:
                prox = next(proxy_pool)
            except:
                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','Creating proxy pool']
                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                proxies = self.get_proxies()
                proxy_pool = iter(proxies)
                prox = next(proxy_pool)
            if not self.ua_list:
                self.ua_list = self.get_user_agent()
            user_agent = choice(self.ua_list)
            self.chrome_options.add_argument(f'--proxy-server=http://{prox}')
            self.chrome_options.add_argument(f"--user-agent={user_agent}")
        else:
            prox = None
            user_agent = None
        print(f'Proxy: {prox} | UA: {user_agent}')
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Proxy: {prox}']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'UA: {user_agent}']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        driver = webdriver.Chrome(options=self.chrome_options, desired_capabilities=self.caps)
        driver.maximize_window()
        # driver.set_window_size(600,800)
        # driver.set_page_load_timeout(15)
        # driver.set_window_position(0, 0)
        return driver, proxy_pool

    def _get_page(self, driver, url):
        current_url = driver.current_url
        driver.delete_all_cookies()
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Getting page: {url}']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        # print(f'Getting page: {url}')
        driver.get(url)
        time.sleep(randint(self.sleep[0], self.sleep[1]))
        timer=time.time()
        while driver.current_url == current_url:
            if time.time()-timer >= 15: 
                raise TimeoutException(msg='Time Out for URL')
        current_url = driver.current_url
        e1 = driver.find_elements_by_xpath('//*/h1/span[contains(text(),"Access Denied")]')
        e2 = driver.find_elements_by_xpath('//*/h1/span[contains(text(),"Cette page ne fonctionne pas")]')
        e3 = driver.find_elements_by_xpath('//*/h1/span[contains(text(),"Ce site est inaccessible")]')
        e4 = driver.find_elements_by_xpath('//*/h1/span[contains(text(),"Aucune connexion")]')
        e5 = driver.find_elements_by_xpath('//*/h1/span[contains(text(),"web site is temporarily unavailable")]')
        e6 = driver.find_elements_by_xpath('//*[contains(text(),"Try checking your spelling")]')
        e7 = driver.find_elements_by_xpath('//*/h1/span[contains(text(),"Enter the characters you see below")]')
        e8 = driver.find_elements_by_xpath('//*/h1/span[contains(text(),"Aucun accès à Internet")]')
        if (e1 or e5): raise AccessDenied
        if (e2 or e3): raise Inaccessible
        if (e4 or e8): raise AucuneConnexion
        if e6: raise HoneyPot
        if e7: raise Captcha
        # print('Waiting for elements')
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','Waiting for elements']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        WebDriverWait(driver, 15, 1).until(EC.presence_of_element_located((By.XPATH, self.page_object)), message='Time Out for elements')
        # print(f'Page successfully loaded in {time.time()-start:.1f}s')
        return 