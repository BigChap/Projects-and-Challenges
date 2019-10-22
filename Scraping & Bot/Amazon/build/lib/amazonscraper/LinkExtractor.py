#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SuperScraper import SuperScraper
class LinkExtractor(SuperScraper):
    __doc__ = SuperScraper.__doc__

    def __init__(self, items:dict, path:str, urls= None, user_agents= None,
                 proxy:bool= False, namespaces:str= None, sitemap:list= None, sleep=(2,4)):
        SuperScraper.__init__(self ,items, path, urls, user_agents, proxy, namespaces, sitemap, sleep)
    
    def start(self):
        begin = time.time()
        a = ['Time','Category_URL','Page_URL']
        b = ['Link']
        c = ['Proxy']
        data = pd.DataFrame(columns=a+b+c, index=[0])

        cat_list = self.get_urls()
        print(f'Number of categories : {len(cat_list)}')
        
        if self.proxy:
            ua_list = self.get_user_agent()
            proxies = self.get_proxies()
            proxy_pool = iter(proxies)
            prox = next(proxy_pool)
            user_agent = choice(ua_list)
            self.chrome_options.add_argument(f'--proxy-server=http://{prox}')
            self.chrome_options.add_argument(f"--user-agent={user_agent}")
        else:
            prox = None
            user_agent = None
            
        try:
            backup = pd.read_csv(self.path, sep='@', header=0, encoding='utf8')
            backup.drop_duplicates('Link', inplace=True)
            backup_page = backup.Page_URL.iloc[-1]
            backup_cat = backup.Category_URL.iloc[-1]
            cat_list = cat_list[cat_list.index(backup_cat):]
#             cat_list = list(set(backup.Category_URL.dropna()).symmetric_difference(set(cat_list)))
#             cat_list.append(backup_cat)
            print(f'Backup has {len(backup)} rows | Number categories left: {cat_list}')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Backup has {len(backup)} rows | Number urls left: {cat_list}']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
#             print(f'Still {len(cat_list)} URL to scrap ')
        except: 
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','No Backup to load']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
            print('No backup to load')
            data.to_csv(self.path, mode='a', sep='@', header=True, index=False)
            backup_page = False
#             backup_cat = None
            
        driver = webdriver.Chrome(options=self.chrome_options, desired_capabilities=self.caps)
        driver.maximize_window()
        last_url = driver.current_url
        
#         goNxt = True
        with tqdm(total=len(cat_list)) as progress_bar:
            while len(cat_list) > 0:
                urls = iter(cat_list)
                parsePage=True
                for url in urls:
                    url = url.strip()
                    goNxt=False
#                     retry = 0
                    while True:
#                         retry += 1
                        if goNxt:
                            break
    #                     while True:
                        try_nxt_page=0
                        start = time.time()
    #                         print('Enter TRY')
#                         if retry >=20:
#                             url = next(urls)
#                         start = time.time()
                        try:
                            driver.delete_all_cookies()
                            if backup_page:
                                print(f'Getting page: {backup_page}\nProxy: {prox} | UA: {user_agent}')
                                driver.get(backup_page)
#                                 pdb.set_trace()
    #                             url = backup_cat
                            else : 
                                print(f'Getting page: {url}\nProxy: {prox} | UA: {user_agent}')
                                driver.get(url)
                            time.sleep(randint(self.sleep[0], self.sleep[1]))
                            timer=time.time()
                            while (driver.current_url==last_url):
                                if time.time()-timer >= 15: 
                                    raise TimeoutException(msg='Time Out for URL')
#                                 pass
                            last_url = driver.current_url if not backup_page else 'data:,'
                            e1 = driver.find_elements_by_xpath('//h1[contains(text(),"Access Denied")]')
                            e2 = driver.find_elements_by_xpath('//h1[contains(text(),"page ne fonctionne pas")]')
                            e3 = driver.find_elements_by_xpath('//h1[contains(text(),"inaccessible")]')
                            e4 = driver.find_elements_by_xpath('//h1[contains(text(),"connexion")]')
                            e5 = driver.find_elements_by_xpath('//*[contains(text(),"web site is temporarily unavailable")]')
                            e6 = driver.find_elements_by_xpath('//*[contains(text(),"Try checking your spelling")]')
                            if e6: raise AmazonError
                            if (e1 or e5): raise AccessDenied
                            if (e2 or e3): raise Inaccessible
                            if e4: raise AucuneConnexion
                            print('Waiting for elements')
                            WebDriverWait(driver, 20, 1).until(EC.presence_of_element_located(
                                (By.XPATH,  self.items['link_object'])), message='Time Out for elements')
    #                         break

    #                     if parsePage:
                            print("Enter category page")
        #                     nxtPage=True
# =================================== PARSE START ===================================
                            while True:
                                current_page = driver.current_url
                                print(f'Parse page:\n {driver.current_url}')#, flush=True, end='\r')
                                parser = html.fromstring(driver.page_source)
                                link_object = parser.xpath(self.items['link_object'])
                                for i in range(len(link_object)):
                                    data['Time'].iloc[-1] = time.strftime('%Y-%m-%d %H:%M:%S')
                                    data['Category_URL'].iloc[-1] = url
                                    data['Page_URL'].iloc[-1] = driver.current_url
                                    try:
                                        data['Link'].iloc[-1] = self.items['root'] + str(link_object[i].get(self.items['link_attr']))
                                    except:
                                        data['Link'].iloc[-1] = 'NaN'                
                                    data['Proxy'].iloc[-1] = prox if prox else "False"
                                    data.to_csv(self.path, mode='a', sep='@', header=False, index=False)
                                print(f'Links from page extracted')#, flush=True, end='\r')
# =================================== PARSE END ===================================
# =================================== GO NEXT PAGE ===================================
                                try:
        # #                         if try_nxt_page<5:
                                    print(f'Try {try_nxt_page} for next page')
                                    print('Waiting for next page button')
        #                                 nxt_page = driver.find_elements_by_xpath(self.items['nxt_page'])
                                    nxt_page = WebDriverWait(driver, 15, 1).until(
                                        EC.element_to_be_clickable((By.XPATH, self.items['nxt_page'])), message='Time Out for next Page')
                                    nxt_page.click()
                                    try:
                                        print('Waiting for next page elements to appear')
                                        time.sleep(randint(self.sleep[0], self.sleep[1]))
                                        timer=time.time()
                                        while (driver.current_url==current_page):
                                            pass
                                            if time.time()-timer >= 15: 
                                                raise TimeoutException(msg='Time Out for URL')
            #                                         Check si y'a pas moyen de ralentir le nombre de tries
                                        WebDriverWait(driver, 20, 1).until(EC.presence_of_element_located((By.XPATH, self.items['link_object'])), message='Time Out for elements')
                                        try_nxt_page=0
# =================================== ####### ===================================
                                    except Exception as e:
                                        print("Exception Next Page")
                                        backup_page = current_page
            #                             try_nxt_page+=1
            #                             print('ok1')
            #                                 nxtPage=False
                                        if hasattr(e, 'message'):
                                            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e.message]
                                            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                            print(f'Exception occured: {e.message}')
                                        else:
                                            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e]
                                            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                            print(f'Exception occured: {e}')
                                        if self.proxy:
                                            driver.quit()
                                            time.sleep(1)
                                            print('Kill task')
                                            os.system('taskkill /im chromedriver.exe /f')
                                            try:
                                                prox = next(proxy_pool)
                                            except StopIteration:
                                                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e]
                                                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                                print('Changing proxy pool')
                                                proxies = self.get_proxies()
                                                proxy_pool = iter(proxies)
                                                prox = next(proxy_pool)
            #                                     print('ok4')
            #                                 print('ok5')
                                            user_agent = choice(ua_list)
                                            self.chrome_options.add_argument(f'--proxy-server=http://{prox}')
                                            self.chrome_options.add_argument(f"--user-agent={user_agent}")
                                            driver = webdriver.Chrome(options=self.chrome_options, desired_capabilities=self.caps)
                                            driver.maximize_window()
                                        break
# =================================== ####### ===================================
                                except Exception as e:
                                    self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e]
                                    self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                    print('No next page or captcha')
        #                             try_nxt_page+=1
        #                             if try_nxt_page>5:
                                    cat_list.remove(url)
                                    progress_bar.update(1)
                                    backup_page = False
                                    goNxt = True
                                    print("Go to next category")
                                    break
# =================================== ####### ===================================
                        except AmazonError as e:
                            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e.message]
                            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                            print(f'Exception occured: {e.message}')
                            backup_page = False
#                             parsePage = False
#                             cat_list.remove(url)
                            progress_bar.update(1)
                            print("Go to next category")
                            break

                        except Exception as e:
                            print("Exception Loading Page")
                            if hasattr(e, 'message'):
                                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e.message]
                                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                print(f'Exception occured: {e.message}')
                            else:
                                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e]
                                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                print(f'Exception occured: {e}')
                                
                            if self.proxy:
                                driver.quit()
                                time.sleep(1)
                                print('Kill task')
                                os.system('taskkill /im chromedriver.exe /f')
                                try:
                                    print('next proxy')
                                    prox = next(proxy_pool)
                                except StopIteration:
                                    self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e]
                                    self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                    print('Changing proxy pool')
                                    proxies = self.get_proxies()
                                    proxy_pool = iter(proxies)
                                    prox = next(proxy_pool)
                                user_agent = choice(ua_list)
                                self.chrome_options.add_argument(f'--proxy-server=http://{prox}')
                                self.chrome_options.add_argument(f"--user-agent={user_agent}")
                                driver = webdriver.Chrome(options=self.chrome_options, desired_capabilities=self.caps)
                                driver.maximize_window()
                            
                            
                                    
#                         progress_bar.update(1)
#                         cat_list.remove(url)
#                         print("next category")
                        
        final_result = pd.read_csv(self.path, sep='@', header=0, encoding='utf8')
        final_result.drop_duplicates(subset='Link', inplace=True)
        save_date = time.strftime('%Y-%m-%d')
        final_result.to_csv(f"./urls/{save_date}-all_urls.csv", sep='@', index=False, header=True, encoding='utf8')
        driver.quit()
        tps = time.strftime('%H:%M:%S', time.gmtime(time.time()-begin))
        print(f'{" END ":_^45}\nAll data extracted in {tps}')
        