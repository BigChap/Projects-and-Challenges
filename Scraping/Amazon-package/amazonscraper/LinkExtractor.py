from amazonscraper.SuperScraper import *

class LinkExtractor(SuperScraper):

    __doc__ = SuperScraper.__doc__

    backup_page = True
    goNxtPage = True

    def __init__(self, items:dict, page_object:str, path:str, urls:list= None, user_agents:list= None,
                 proxy:bool= False, namespaces:str= None, sitemap:list= None, sleep:tuple=(2,4), category_links:dict=None):
        SuperScraper.__init__(self ,items, page_object, path, urls, user_agents, proxy, namespaces, sitemap, sleep)
        self.category_links:dict = category_links

    def _parse_page(self, driver, data, key, url):
        parser = html.fromstring(driver.page_source)
        refs = parser.xpath(self.items['asin'])
        for ref in refs:
            data['Time'].iloc[-1] = time.strftime('%Y-%m-%d %H:%M:%S')
            data['Category_Name'].iloc[-1] = key
            data['Category_URL'].iloc[-1] = url
            data['Page_URL'].iloc[-1] = driver.current_url
            data['Link'].iloc[-1] = self.items['root'] + str(ref) if ref else 'NaN'
            data.to_csv(self.path, mode='a', sep='@', header=False, index=False)
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', f'Links extracted | page : {driver.current_url}']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        return
    
    def _nxt_page(self, driver):
        global backup_page
        global goNxtPage
        try:
            nxt_page = WebDriverWait(driver, 15, 1).until(
                EC.element_to_be_clickable((By.XPATH, self.items['nxt_page'])), message='Time Out for next Page')
            nxt_page.click()
        except Exception as e:
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'No more next page for this category or HoneyPot. Go to next category']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
            backup_page = False
            goNxtPage = False
            return

        time.sleep(randint(self.sleep[0], self.sleep[1]))
        timer=time.time()
        while (driver.current_url==backup_page):
            if time.time()-timer >= 15: 
                raise TimeoutException(msg='Time Out for URL')
        backup_page = driver.current_url
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
        WebDriverWait(driver, 15, 1).until(EC.presence_of_element_located((By.XPATH, self.page_object)), message='Time Out for elements')
        return

    def start(self):
        global backup_page
        global goNxtPage

        begin = time.time()
        data = pd.DataFrame(columns=['Time','Category_Name','Category_URL','Page_URL','Link'], index=[0])
        print(f'Number of categories : {len(self.category_links)}')

        # inverted_cat_dict = {v: k for k, v in self.category_links.items()}

                    
        try:
            backup = pd.read_csv(self.path, sep='@', header=0, encoding='utf8')
            backup.drop_duplicates('Link', inplace=True)
            backup.to_csv(self.path, mode='w', sep='@', header=True, index=False)
            backup_page = backup.Page_URL.iloc[-1]
            backup_cat_name = backup.Category_Name.iloc[-1]
            copie = self.category_links.copy()
            for k,v in copie.items():
                if k==backup_cat_name:
                    break
                else: del self.category_links[k]
            # cat_list = list(copie.values())
            print(f'Backup has {len(backup)} rows | Number categories left: {len(self.category_links)}')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Backup has {len(backup)} rows | Number urls left: {len(self.category_links)}']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')

        except: 
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','No Backup to load']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
            print('No backup to load')
            data.to_csv(self.path, mode='a', sep='@', header=True, index=False)
            backup_page = False
            
        driver, proxy_pool = self._start_driver()
            
        while len(self.category_links) > 0:
            with tqdm(total=len(self.category_links)) as progress_bar:
                # urls = iter(cat_list)
                copie = self.category_links.copy()
                for key, url in copie.items():
                    url = url.strip()
                    start = time.time()
                    goNxtPage=True
                    while goNxtPage:
                        try:
                            # ===================== Start Page ========================
                            if backup_page:
                                self._get_page(driver, backup_page)
                            else: 
                                self._get_page(driver, url)
                            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', f'Page successfully loaded in {time.time()-start:.1f}s']
                            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                            # backup_page = driver.current_url

                            while goNxtPage:
                                # ===================== Parsing Page ========================
                                self._parse_page(driver, data, key, url)
                                # ===================== Go Next Page ========================
                                self._nxt_page(driver)

                            del self.category_links[key]
                            progress_bar.update(1)

                        # except HoneyPot as e:
                        #     self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'EXCEPTION',e.message]
                        #     self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                        #     print(f'Exception occured: {e.message}')
                        #     backup_page = False
                        #     goNxtPage = False
                        #     print("Go to next category")

                        except Exception as e:
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
                                os.system('taskkill /im chromedriver.exe /f')
                                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', 'Kill task']
                                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                driver, proxy_pool = self._start_driver(proxy_pool)
                                    
        final_result = pd.read_csv(self.path, sep='@', header=0, encoding='utf8')
        final_result.drop_duplicates(subset='Link', inplace=True)
        save_date = time.strftime('%Y-%m-%d')
        final_result.to_csv(f"./urls/{save_date}-all_urls.csv", sep='@', index=False, header=True, encoding='utf8')
        driver.quit()
        tps = time.strftime('%H:%M:%S', time.gmtime(time.time()-begin))
        print(f'{" END ":_^45}\nAll data extracted in {tps}')

        