from amazonscraper.SuperScraper import *

class Scraper(SuperScraper):
    __doc__ = SuperScraper.__doc__
    
    def __init__(self, items:dict, page_object:str, path:str, urls:list= None, user_agents:list= None,
                 proxy:bool= False, namespaces:str= None, sitemap:list= None, sleep=(2,4)):
        SuperScraper.__init__(self ,items, page_object, path, urls, user_agents, proxy, namespaces, sitemap, sleep)

    def _parse_page(self, driver, data, url):
        parser = html.fromstring(driver.page_source)
        data['Time'].iloc[-1] = time.strftime('%Y-%m-%d %H:%M:%S')
        data['Page_URL'].iloc[-1] = driver.current_url
        for item, content in self.items.items():
            value = parser.xpath(content)
            data[item].iloc[-1] = value if value else 'NaN'
        data.to_csv(self.path, mode='a', sep='@', header=False, index=False)
        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', f'Data extracted | page: {driver.current_url}']
        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
        return #print('Data extracted')

    def start(self):
        begin = time.time()
        data = pd.DataFrame(columns=['Time', 'Page_URL']+list(self.items.keys()), index=[0])

        url_list = self.get_urls()
        print(f'Number urls : {len(url_list)}')
            
        try:
            backup = pd.read_csv(self.path, sep='@', header=0, encoding='utf8')
            backup.drop_duplicates('Page_URL', inplace=True)
            backup.to_csv(self.path, mode='w', sep='@', header=True, index=False)
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
        
        driver, proxy_pool = self._start_driver()

        while len(url_list) > 0:
            with tqdm(total=len(url_list)) as progress_bar:
                urls = iter(url_list)
                for url in urls:
                    start = time.time()
                    try:
                        # ===================== Getting Page ========================
                        self._get_page(driver, url)
                        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', f'Page successfully loaded in {time.time()-start:.1f}s']
                        self.log.to_csv('log.csv', sep=';', index=False, mode='a')
                        # ===================== Parsing page ========================
                        self._parse_page(driver, data, url)
                        # ===================== Remove URL ========================
                        progress_bar.update(1)
                        url_list.remove(url)
                        self.log.columns = [time.strftime("%Y-%m-%d %H:%M:%S"), 'INFO', f'Removing url: {url}']
                        self.log.to_csv('log.csv', sep=';', index=False, mode='a')

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
        save_date = time.strftime('%Y-%m-%d')
        final_result.to_csv(f"{save_date}-final_result.csv", sep='@', index=False, header=True, encoding='utf8')
        driver.quit()
        os.system('taskkill /im chromedriver.exe /f')
        tps = time.strftime('%H:%M:%S', time.gmtime(time.time()-begin))
        print(f'{" END ":_^45}\nAll data extracted in {tps}')