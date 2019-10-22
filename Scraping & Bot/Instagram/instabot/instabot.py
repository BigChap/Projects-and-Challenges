# import argparse
# import configparser
# import sys
# import numpy as np
# import requests
# from selenium.common.exceptions import (ElementNotInteractableException,
#                                         ElementNotVisibleException,
#                                         NoAlertPresentException,
#                                         NoSuchElementException,
#                                         TimeoutException, WebDriverException)

import glob
import itertools
import json
import logging as lg
import os
import re
import time
from datetime import datetime
from random import choice, randint, random, uniform

import pandas as pd
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import DesiredCapabilities, Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.remote_connection import LOGGER
from sqlalchemy import create_engine
from sqlalchemy.types import DATETIME

def name(func):
    def inner(*args, **kwargs):
        print('Running: ', func.__name__)
        return func(*args, **kwargs)
    return inner

class Error(Exception):
    pass


class ActionBloquee(Error):
    def __init__(self, message='Action bloquée'):
        self.message = message


class InstaBot:
    CO = webdriver.ChromeOptions()
    CAPS = DesiredCapabilities().CHROME
    lg.basicConfig(
        filename='logfile.log',
        filemode='a',
        format='%(asctime)s, line: %(lineno)d %(levelname)8s | %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=lg.INFO
        )
    # lg.getLogger('sqlalchemy.engine').setLevel(lg.INFO)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.CAPS["pageLoadStrategy"] = self.pageLoadStrategy
        self.CO.binary_location = self.binary_location
        for option, value in self.experimental_options.items():
            self.CO.add_experimental_option(option, value)
        for option in self.options:
            self.CO.add_argument(option)

        self.disk_engine = create_engine(f'sqlite:///{self.path_data+self.botname}.db')
        
        

    @classmethod
    def load_config(cls):
        configfile = "config.json"
        if not os.path.isfile(configfile):
            param={
                'PARAMS': dict(
                    botname=None,
                    login=None,
                    password =None,
                    runtime = 45,
                    like = True,
                    post_comment = False,
                    follow = False,
                    like_rate = 0.33,
                    post_rate = 0.2,
                    follow_rate = 0.3,
                    unfollow = False,
                    unfollow_limit = 50,
                    days_before_unfollow = 6,
                    min_delay = 2,
                    max_delay = 4,
                    scrap_data = True,
                    ),
                'DATA': dict(
                    path_data = './data/',
                    ),
                'WEBDRIVER': dict(
                    binary_location = r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe",
                    options = [
                        "--disable-plugins-discovery",
                        "--profile-directory=Default",
                        "--disable-internal-flash",
                        "--user-data-dir=chrome-data",
                        "--start-maximized",
                        # "--disable-infobars",
                        # "--disable-extensions",
                        # "--incognito",
                        # "--headless",
                        ],
                    experimental_options = dict(
                        excludeSwitches = ['enable-automation'],
                        useAutomationExtension = False,
                        prefs = {
                            "download.default_directory": os.getcwd()+r"\download",
                            "download.prompt_for_download": False,
                            "safebrowsing.enabled": False,
                            "intl.accept_languages": "fr",
                        #     'plugins.always_open_pdf_externally'= True,
                        #     "download.directory_upgrade"= True,
                            },
                        ),
                    # language = "fr",
                    pageLoadStrategy = "eager",
                    wait = 15,
                    poll = 3,
                    ),
                'ELEMENTS': dict(
                    main_profile='/html/body/div[3]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a/@href',
                    main_comment='/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/div/li/div/div/div[2]/span/text()',
                    main_arobas='/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/div/li/div/div/div[2]/span/a[@class="notranslate"]/@href',
                    main_tags='/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/div/li/div/div/div[2]/span/a[@class=""]/@href',
                    profiles='/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul[1]/div/li/div/div[1]/div[2]/h3/a/@href',
                    comments='/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul[1]/div/li/div/div[1]/div[2]/span/text()',
                    arobas='/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul[1]/div/li/div/div[1]/div[2]/span/a[@class="notranslate"]/@href',
                    tags='/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul[1]/div/li/div/div[1]/div[2]/span/a[@class=""]/@href',
                    likes='/html/body/div[3]/div[2]/div/article/div[2]/section[2]/div/div/button/span/text()',
                    img_src='/html/body/div[3]/div[2]/div/article/div[1]/div/div/div//img/@srcset',
                    img_info='/html/body/div[3]/div[2]/div/article/div[1]/div/div/div//img/@alt',
                    ),
            }
            with open(configfile, 'w') as cfg:
                json.dump(param,cfg)

        with open(configfile,'r') as cfg:
            config = json.load(cfg)

        return cls(**config['PARAMS'], **config['DATA'], **config['WEBDRIVER'], ELEMENTS = config['ELEMENTS'])

    def __login(self, driver):
        actionChains = ActionChains(driver)
        meConnecter_btn = WebDriverWait(driver, 5, self.poll).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Connectez-vous')))
        actionChains.move_to_element_with_offset(meConnecter_btn, randint(10,70), randint(5,18))
        actionChains.click().perform()
        time.sleep(uniform(0.5,1))
        
        login_elmt = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[2]/div/label/input')))
        login_elmt.send_keys(self.login)
        time.sleep(uniform(0.5,1))
        
        mdp_elmt = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input')))
        mdp_elmt.send_keys(self.password)
        time.sleep(uniform(0.5,1))

        connexion_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button')))
        actionChains = ActionChains(driver)
        actionChains.move_to_element_with_offset(connexion_btn, randint(25,250), randint(5,25))
        actionChains.click().perform()
        time.sleep(uniform(0.5,1))

        notification_off = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div/div[3]/button[2]')))
        actionChains = ActionChains(driver)
        actionChains.move_to_element_with_offset(notification_off, randint(35,350), randint(10,40))
        actionChains.click().perform()
        time.sleep(uniform(self.min_delay,self.max_delay))

    def __goTo_explore(self, driver):
        explore_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/nav/div/div/div/div/div/div[1]/a')))
        actionChains = ActionChains(driver)
        actionChains.move_to_element_with_offset(explore_btn, randint(5,20), randint(5,20))
        actionChains.click().perform()
        time.sleep(uniform(self.min_delay,self.max_delay))
    
    def __goTo_profile(self, driver):
        profile_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/nav/div/div/div/div/div/div[3]/a')))
        actionChains = ActionChains(driver)
        actionChains.move_to_element_with_offset(profile_btn, randint(5,20), randint(5,20))
        actionChains.click().perform()
        time.sleep(uniform(self.min_delay,self.max_delay))
    
    def __open_subscriptions(self, driver):
        subs_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((
            By.XPATH, '/html/body/span/section/main/div/header/section/ul/li[3]//a')))
        actionChains = ActionChains(driver)
        actionChains.move_to_element_with_offset(subs_btn, randint(5,10), randint(5,10))
        actionChains.click().perform()
        time.sleep(uniform(self.min_delay,self.max_delay))

    def __open_img(self, driver):
        alea_row = randint(1,8)
        alea_col = randint(1,3)
        first_img = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((
            By.XPATH,f'//*[@id="react-root"]/section/main/div/article/div[1]/div/div[{alea_row}]/div[{alea_col}]/a/div')))
        actionChains = ActionChains(driver)
        actionChains.move_to_element_with_offset(first_img, randint(25,250), randint(25,250))
        actionChains.click().perform()
        time.sleep(uniform(self.min_delay,self.max_delay))

    def __scroll_up_and_down(self, driver):
        for i in range(randint(1,5)):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        driver.execute_script("window.scrollTo(document.body.scrollHeight, 0);")

    def __like_img(self, driver):
        try:
            img = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div[2]/div/article/div[1]/div')))
            actionChains = ActionChains(driver)
            actionChains.move_to_element_with_offset(img, randint(35,350), randint(100,500))
            actionChains.double_click().perform()
        except Exception as e:
            lg.warning('Catch on like_img: '+ str(e))

    def __load_more_comments(self, driver):
        for _ in range(randint(3,5)):
            try:
                show_more_comment_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable(
                    (By.XPATH,'/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/li/div/button')))
                actionChains = ActionChains(driver)
                actionChains.move_to_element_with_offset(show_more_comment_btn, randint(10,250), randint(5,30))
                actionChains.click().perform()
                time.sleep(uniform(self.min_delay,self.max_delay))
            except Exception as e:
                lg.warning('Catch on load_more_comment: ' +str(e))
                try:
                    time.sleep(2)
                    e1 = driver.find_elements_by_xpath('/html/body//h3[contains(text(),"Action bloquée")]')
                    if e1 : raise ActionBloquee
                except ActionBloquee as e:
                    lg.warning('Catch on load_more_comment: ' +str(e.message))
                    print('\n'+str(e.message))
                    signaler_btn = driver.find_elements_by_xpath('/html/body//button[contains(text(),"Signaler un problème")]')[0]
                    actionChains = ActionChains(driver)
                    actionChains.move_to_element_with_offset(signaler_btn, randint(100,300), randint(10,30))
                    actionChains.click().perform()
                    quit()
                finally: break

    def __scrap_data(self, driver, liked, posted, followed):
        data = pd.DataFrame(columns=['Time', 'Page_URL']+list(self.ELEMENTS.keys())+['Liked','Posted','Followed','Unfollowed'])
        # if not os.path.exists(self.path_data+time.strftime('%Y-%m-%d')+'_'+self.botname+'.csv'):
        #     data.to_csv(self.path_data+time.strftime('%Y-%m-%d')+'_'+self.botname+'.csv', sep='|', header=True, index=False, encoding='utf8', mode='w')

        WebDriverWait(driver, self.wait, self.poll).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/div/article/div[1]/div/div/div//img')), message='No image found')
        # self.__load_more_comments(driver)

        parser = html.fromstring(driver.page_source)
        all_comments_size = len(parser.xpath('/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul/div/li/div/div[1]/div[2]/h3/a/@href'))
        for i in range(all_comments_size):
            ELEMENTS_upd = dict(profiles=f'/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul[{i+1}]/div/li/div/div[1]/div[2]/h3/a/@href',
                                comments=f'/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul[{i+1}]/div/li/div/div[1]/div[2]/span/text()',
                                arobas=f'/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul[{i+1}]/div/li/div/div[1]/div[2]/span/a[@class="notranslate"]/@href',
                                tags=f'/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul[{i+1}]/div/li/div/div[1]/div[2]/span/a[@class=""]/@href',)
            self.ELEMENTS.update(ELEMENTS_upd)
            data.loc[i,'Time'] = pd.to_datetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            data.loc[i,'Page_URL'] = driver.current_url
            data.loc[i,'Liked'] = liked
            data.loc[i,'Posted'] = posted
            data.loc[i,'Followed'] = followed
            data.loc[i,'Unfollowed'] = False
            for elmt, content in self.ELEMENTS.items():
                try:
                    data.loc[i,elmt] = parser.xpath(content)
                except Exception as e:
                    lg.warning('Catch on scraping_data: '+str(e))
                    continue

        for elmt in self.ELEMENTS.keys():
            data[elmt] = data[elmt].apply('\n'.join)
        data.main_profile = 'https://www.instagram.com'+data.main_profile
        # data.to_csv(self.path_data+time.strftime('%Y-%m-%d')+'_'+self.botname+'.csv', sep='|', header=False, index=False, encoding='utf8', mode='a')
        data.to_sql('session', self.disk_engine, if_exists='append', index=False, dtype={'Time': DATETIME})

    def __generate_comment(self, comment_list):
        c_list = list(itertools.product(*comment_list))
        repl = [("  ", " "), (" .", "."), (" !", "!")]
        res = " ".join(choice(c_list))
        for s, r in repl:
            res = res.replace(s, r)
        return res.capitalize()

    def __post_comment(self, driver):
        with open(os.path.dirname(__file__)+'/comments.json', 'r') as f:
            comment_list = json.load(f)['comment_list']
        post = self.__generate_comment(comment_list)
        c=0
        d=0
        while c<10 and d<10:
            c+=1
            try:
                post_elmt = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div[2]/div/article/div[2]/section[3]//form/textarea')))
                time.sleep(uniform(self.min_delay,self.max_delay))
                post_elmt.send_keys(post)
                time.sleep(uniform(self.min_delay,self.max_delay))
                lg.info('Message sent in box')
                while d<10:
                    d+=1
                    try:
                        post_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[2]/div/article/div[2]/section[3]//form/button')))
                        post_btn.click()
                        lg.info('Message posted')
                        chrono = 0
                        start_chrono = time.time()
                        while not driver.find_elements_by_xpath(f'/html/body/div[3]/div[2]/div/article/div[2]/div[1]/ul/ul/div/li/div/div[1]/div[2]/span[contains(text(),"{post}")]') and chrono<15:
                            time.sleep(uniform(self.min_delay,self.max_delay))
                            chrono = time.time() - start_chrono
                            lg.info('Wating for the post to appear')
                        break
                    except Exception as e:
                        lg.warning('Catch on post_comment clicking send button: '+str(e))
                break
            except Exception as e:
                lg.warning('Catch on post_comment sending keys: '+str(e))

    def __next_img(self, driver):
        while True:
            try:
                nxt_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div[1]/div/div/a[last()]')))
                actionChains = ActionChains(driver)
                actionChains.move_to_element_with_offset(nxt_btn, randint(10,35), randint(10,35))
                actionChains.click().perform()
                break
            except Exception as e:
                lg.warning('Catch on next_img: '+str(e))
                try:
                    time.sleep(2)
                    e1 = driver.find_elements_by_xpath('/html/body//h3[contains(text(),"Action bloquée")]')
                    if e1 : raise ActionBloquee
                except ActionBloquee as e:
                    lg.warning('Catch on next_img: '+str(e.message))
                    print('\n'+str(e.message))
                    signaler_btn = driver.find_elements_by_xpath('/html/body//button[contains(text(),"Signaler un problème")]')[0]
                    actionChains = ActionChains(driver)
                    actionChains.move_to_element_with_offset(signaler_btn, randint(100,300), randint(10,30))
                    actionChains.click().perform()
                    quit()

    def __close_img(self, driver):
        close_img_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/button[1]')))
        actionChains = ActionChains(driver)
        actionChains.move_to_element_with_offset(close_img_btn, randint(10,50), randint(5,30))
        actionChains.click().perform()
        time.sleep(uniform(self.min_delay,self.max_delay))

    def __follow(self, driver):
        c = 0
        while c<10:
            c+=1
            try:
                follow_elmt = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div[2]/div/article/header//button')))
                follow_elmt.click()
                time.sleep(uniform(self.min_delay,self.max_delay))
                while not driver.find_elements_by_xpath('/html/body/div[3]/div[2]/div/article/header//button[contains(text(),"Abonné(e)")]'):
                    time.sleep(uniform(self.min_delay,self.max_delay))
                break
            except Exception as e:
                lg.warning('Catch on click follow : '+str(e))

    def __unfollow(self, driver):
        df = pd.read_sql_table("session", self.disk_engine)
        unfollow_list = df[(datetime.now() - df.Time).dt.days >= self.days_before_unfollow]
        unfollow_list = unfollow_list[(unfollow_list.Followed) & ~(unfollow_list.Unfollowed)]
        unfollow_list.dropna(subset=['main_profile'], inplace=True)
        unfollow_list = list(unfollow_list.main_profile.drop_duplicates())
        
        i=0
        count = 0
        while len(unfollow_list)>0 and count < self.unfollow_limit:
            profile_elmt = WebDriverWait(driver, self.wait, self.poll).until(EC.presence_of_element_located((
                By.XPATH, f'/html/body/div[3]/div/div[2]/ul/div/li[{i+1}]//a')))
            profile_link = profile_elmt.get_attribute("href")
            unfollow_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((
                By.XPATH, f'/html/body/div[3]/div/div[2]/ul/div/li[{i+1}]//button')))
            unfollow_btn_txt = driver.find_element_by_xpath(f'/html/body/div[3]/div/div[2]/ul/div/li[{i+1}]//button').text

            if profile_link in unfollow_list and unfollow_btn_txt == 'Abonné(e)':
                # Unfollow
                actionChains = ActionChains(driver)
                actionChains.move_to_element_with_offset(unfollow_btn, randint(5,80), randint(5,25))
                actionChains.click().perform()
                time.sleep(uniform(2,4))
                # Confirm
                try:
                    confirm_btn = WebDriverWait(driver, self.wait, self.poll).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[4]/div/div//button[1]")))
                    actionChains = ActionChains(driver)
                    actionChains.move_to_element_with_offset(confirm_btn, randint(50,350), randint(10,38))
                    actionChains.click().perform()
                    time.sleep(uniform(2,4))
                    e1 = driver.find_elements_by_xpath('/html/body//h3[contains(text(),"Action bloquée")]')
                    if e1 : raise ActionBloquee
                except ActionBloquee as e:
                    lg.warning('Catch on exit of unfollow button: '+str(e.message))
                    print('\n'+str(e.message))
                    signaler_btn = driver.find_elements_by_xpath('/html/body//button[contains(text(),"Signaler un problème")]')[0]
                    actionChains = ActionChains(driver)
                    actionChains.move_to_element_with_offset(signaler_btn, randint(100,300), randint(10,30))
                    actionChains.click().perform()
                    quit()
                # Update file        
                df.Unfollowed.where(df.main_profile!=profile_link, True, inplace=True)
                df.to_sql('session', self.disk_engine, if_exists='replace', index=False, dtype={'Time': DATETIME})
                # Drop row
                unfollow_list.remove(profile_link)
                count+=1
                print(f'Unfollowed: {count}', end='\r')
            elif profile_link in unfollow_list and unfollow_btn_txt != 'Abonné(e)':
                # Update file        
                df.Unfollowed.where(df.main_profile!=profile_link, True, inplace=True)
                df.to_sql('session', self.disk_engine, if_exists='replace', index=False, dtype={'Time': DATETIME})
                # Drop row
                unfollow_list.remove(profile_link)
            i+=1        

    def start(self):
        begin = time.time()
        time_limit = self.runtime*uniform(0.85,1.15)
        start_time = time.strftime('%H:%M:%S', time.localtime(begin))
        end_time = time.strftime('%H:%M:%S', time.localtime(begin+time_limit*60))
        print(f'Bot started at {start_time} and will stop at {end_time}')
        nb_photos = 0
        nb_likes=0
        nb_comments=0
        nb_follows=0
        while True:
            try:
                with webdriver.Chrome(options=self.CO, desired_capabilities=self.CAPS) as driver:
                    print('Bot runing...')
                    driver.get('https://www.instagram.com')
                    try:
                        self.__login(driver)
                    except Exception:
                        print('Already logged in !')
                    self.__goTo_explore(driver)
                    self.__scroll_up_and_down(driver)
                    self.__open_img(driver)
                    while (time.time()-begin)/60 < time_limit:
                        liked=False
                        posted = False
                        followed = False
                        randLike = random()
                        randComment = random()
                        randFollow = random()
                        nb_photos+=1
                        lg.info(f'Nombre de photos visionées : {nb_photos}')
                        # ============= LIKE ==============
                        parser = html.fromstring(driver.page_source)
                        inMemory = parser.xpath('/html/body/div[3]/div[2]/div/article/div[2]/section[1]/span[1]/button/span[contains(@aria-label,"Je n’aime plus")]')
                        if randLike < self.like_rate and self.like and not inMemory:
                            try:
                                self.__like_img(driver)
                                time.sleep(uniform(1,1.5))
                                e1 = driver.find_elements_by_xpath('/html/body//h3[contains(text(),"Action bloquée")]')
                                if e1 : raise ActionBloquee
                            except ActionBloquee as e:
                                lg.warning('Catch on exit of like_img function: '+str(e.message))
                                print('\n'+str(e.message))
                                signaler_btn = driver.find_elements_by_xpath('/html/body//button[contains(text(),"Signaler un problème")]')[0]
                                actionChains = ActionChains(driver)
                                actionChains.move_to_element_with_offset(signaler_btn, randint(100,300), randint(10,30))
                                actionChains.click().perform()
                                quit()

                            nb_likes+=1
                            liked = True
                            lg.info(f'Nombre de photos likées : {nb_likes}')
                            time.sleep(uniform(self.min_delay,self.max_delay))
                            # ============= POST ==============
                            if randComment < self.post_rate and self.post_comment:
                                self.__post_comment(driver)
                                nb_comments+=1
                                posted = True
                                lg.info(f'Nombre de commentaires postés : {nb_comments}')
                                time.sleep(uniform(self.min_delay,self.max_delay))
                            # ============= FOLLOW ==============
                            if randFollow < self.follow_rate and self.follow:
                                self.__follow(driver)
                                nb_follows+=1
                                followed = True
                                lg.info(f'Nombre de follow : {nb_follows}')
                                time.sleep(uniform(self.min_delay,self.max_delay))
                        # ============= SCRAP ==============
                        if self.scrap_data:
                            self.__scrap_data(driver, liked, posted, followed)
                        # ============= NEXT ==============
                        print(f'Seen : {nb_photos} | Likes : {nb_likes} | Posts : {nb_comments} | Follow : {nb_follows}', end='\r')
                        self.__next_img(driver)
                        time.sleep(uniform(self.min_delay,self.max_delay))
                        # ============= LOOP ==============
                    now = time.time()
                    print(f'\nLe bot a bien travaillé pendant {(now-begin)//3600:1.0f}H{((now-begin)%3600)/60:1.0f}min\
                            \nPhotos likées: {nb_likes}\
                            \nCommentaires postés: {nb_comments}\
                            \nFollow: {nb_follows}')
                    lg.info(f'\nBot ran for {(now-begin)//3600:1.0f}H{((now-begin)%3600)/60:1.0f}min | Seen: {nb_photos} | Likes: {nb_likes} | Posts: {nb_comments} | Follow: {nb_follows}')
                break 
            except Exception as e:
                lg.error('Catch on start: '+str(e))

    def unfollow_profiles(self):
        while True:
            try:
                with webdriver.Chrome(options=self.CO, desired_capabilities=self.CAPS) as driver:
                    print(f'Bot will unfollow {self.unfollow_limit} profiles followed more than {self.days_before_unfollow} before')
                    print('Bot runing...')
                    driver.get('https://www.instagram.com')
                    self.__login(driver)
                    self.__goTo_profile(driver)
                    self.__open_subscriptions(driver)
                    self.__unfollow(driver)
                    break
            except Exception as e:
                lg.error('Catch on unfollow: '+str(e))
