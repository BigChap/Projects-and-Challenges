# %%
from SuperScraper import SuperScraper
class Scraper(SuperScraper):
    __doc__ = SuperScraper.__doc__
    
    def __init__(self, items:dict, path:str, urls:list= None, user_agents:list= None,
                 proxy:bool= False, namespaces:str= None, sitemap:list= None, sleep=(2,4)):
        SuperScraper.__init__(self ,items, path, urls, user_agents, proxy, namespaces, sitemap, sleep)

    def _parse_page(self, data, driver, prox, start, url_list, progress_bar):
        print(f'Page successfully loaded in {time.time()-start:.1f}s')
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', f'Page successfully loaded in {time.time()-start:.1f}s']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        parser = html.fromstring(driver.page_source)
        data['Time'].iloc[-1] = time.strftime('%Y-%m-%d %H:%M:%S')
        data['Page_URL'].iloc[-1] = driver.current_url
        for item, content in self.items.items():
            value = parser.xpath(content)
            data[item].iloc[-1] = value if value else 'NaN'
        data['Proxy'].iloc[-1] = prox if prox else "False"
        data.to_csv(self.path, mode='a', sep='@', header=False, index=False)
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', 'Data extracted']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        print('Data extracted')
        progress_bar.update(1)
        url_list.remove(url)
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', f'Removing url: {url}']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        return 

        
    def start(self):
        begin = time.time()
        a = ['Time', 'Page_URL']
        b = list(self.items.keys())
        c = ['Proxy']
        data = pd.DataFrame(columns=a+b+c, index=[0])

        url_list = self.get_urls()
        print(f'Number urls : {len(url_list)}')
        
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
            url_list = list(set(backup.Page_URL.dropna()).symmetric_difference(set(url_list)))
            print(f'Backup has {len(backup)} rows')
            print(f'Still {len(url_list)} URL to scrap ')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Backup has {len(backup)} rows']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Still {len(url_list)} URL to scrap ']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')

        except: 
            print('No backup to load')
            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','No Backup to load']
            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
            data.to_csv(self.path, mode='a', sep='@', header=True, index=False)
        
        driver = webdriver.Chrome(options=self.chrome_options, desired_capabilities=self.caps)
        driver.maximize_window()
        last_url = driver.current_url
#         driver.set_window_size(600,1080)
#         driver.set_page_load_timeout(15)
#         driver.set_window_position(0, 0)
        with tqdm(total=len(url_list)) as progress_bar:
            while len(url_list) > 0:
                urls = iter(url_list)
                for url in urls:
                    url = url.strip()
#                     parsePage=True
#                     retry = 0
#                     while True:
#                     retry += 1
                    start = time.time()
                    try:
                        driver.delete_all_cookies()
                        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO',f'Getting page: {url}\nProxy: {prox} | UA: {user_agent}']
                        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
#                         print(f'Try: {retry} | Getting page: {url}\nProxy: {prox} | UA: {user_agent}')
                        print(f'Getting page: {url}\nProxy: {prox} | UA: {user_agent}')
                        driver.get(url)
                        time.sleep(randint(self.sleep[0], self.sleep[1]))
                        timer=time.time()
                        while driver.current_url == last_url:
                            if time.time()-timer >= 15: 
                                raise TimeoutException(msg='Time Out for URL')
#                             pass
                        last_url = driver.current_url
                        e1 = driver.find_elements_by_xpath('//h1[contains(text(),"Access Denied")]')
                        e2 = driver.find_elements_by_xpath('//h1[contains(text(),"page ne fonctionne pas")]')
                        e3 = driver.find_elements_by_xpath('//h1[contains(text(),"inaccessible")]')
                        e4 = driver.find_elements_by_xpath('//h1[contains(text(),"connexion")]')
                        e5 = driver.find_elements_by_xpath('//*[contains(text(),"web site is temporarily unavailable")]')
                        e6 = driver.find_elements_by_xpath('//*[contains(text(),"Try checking your spelling")]')
                        if (e1 or e5): raise AccessDenied
                        if (e2 or e3): raise Inaccessible
                        if e4: raise AucuneConnexion
                        if e6: raise AmazonError
                        print('Waiting for elements')
                        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','Waiting for elements']
                        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                        elmt_xpath = list(self.items.values())
                        WebDriverWait(driver, 30, 1).until(EC.presence_of_element_located((By.XPATH, elmt_xpath[-1][:-5])),
                                                           message='Time Out for elements')

# ======================================================================== PARSE START ========================================================================
                        self._parse_page(data, driver, prox, start, url_list, progress_bar)
# ======================================================================== PARSE END ========================================================================

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
                            print('Kill task')
                            os.system('taskkill /im chromedriver.exe /f')
                            self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', 'Kill task']
                            self.log.to_csv('log.csv', sep=';', index=False, mode='a')
#                             pdb.set_trace()
                            try:
                                prox = next(proxy_pool)
                            except StopIteration as e:
                                print('Changing proxy pool')
                                self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO','Changing proxy pool:\n'+str(e)]
                                self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                                proxies = self.get_proxies()
                                proxy_pool = iter(proxies)
                                prox = next(proxy_pool)
                                
                            user_agent = choice(ua_list)
                            self.chrome_options.add_argument(f'--proxy-server=http://{prox}')
                            self.chrome_options.add_argument(f"--user-agent={user_agent}")
                            driver = webdriver.Chrome(options=self.chrome_options, desired_capabilities=self.caps)
                            driver.maximize_window()
#                         parsePage=False
#                         break
                                
#                     if parsePage:
        
        final_result = pd.read_csv(self.path, sep='@', header=0, encoding='utf8')
        save_date = time.strftime('%Y-%m-%d')
        final_result.to_csv(f"{save_date}-final_result.csv", sep='@', index=False, header=True, encoding='utf8')
        driver.quit()
        os.system('taskkill /im chromedriver.exe /f')
        tps = time.strftime('%H:%M:%S', time.gmtime(time.time()-begin))
        print(f'{" END ":_^45}\nAll data extracted in {tps}')