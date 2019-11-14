# coding: utf-8

import re
import requests
import unittest
import json
from bs4 import BeautifulSoup

website_prefix = "https://www.reuters.com"
search_prefix = "https://www.reuters.com/finance/stocks/lookup?searchType=any&comSortBy=marketcap&sortBy=&dateRange=&search="


def _handle_request_result_and_build_soup(request_result):
    if request_result.status_code == 200:
        html_doc = request_result.text
        soup = BeautifulSoup(html_doc, "lxml")
        return soup

def _search_company_pattern(query):
    url = search_prefix + query
    res = requests.get(url)
    soup = _handle_request_result_and_build_soup(res)
    mapy = map(lambda x: x.attrs["onclick"], soup.find_all("tr", attrs={"onclick": re.compile(".*parent.*")}))
    list1 = []
    list_pattern = []
    for i in mapy:
        list1.append(i.split("'"))
    for j in list1:
        list_pattern.append(j[1])
    return list_pattern

def _get_company_overview_urls(list_pattern):
    list_company_overview = []
    for pattern in list_pattern:
        url = website_prefix + str(pattern)
        list_company_overview.append(url)
    return list_company_overview

def _get_company_finance_urls(list_company_overview):
    list_urls_finance = []
    url_base = "https://www.reuters.com/finance/stocks/financial-highlights/"
    for overview in list_company_overview:
        str1 = overview.split("=")[1]
        list_urls_finance.append(url_base + str1)
    return list_urls_finance

def get_financial_information(list_urls_finance):
    data_reuters_byExchange = {}

    for url in  list_urls_finance[:3]:
        res = requests.get(url)
        soup = _handle_request_result_and_build_soup(res)

        title = soup.find("div", id="sectionTitle").find_next('h1').string

        data_reuters_byExchange[title] = []
        tab_quarter = soup.find("td", class_="dataTitle", text=re.compile(".*SALES.*")).find_next("td").parent.select("td")
        quarter_mean = float(tab_quarter[2].string.replace(',', '.').strip()[:-3])
        quarter_high = float(tab_quarter[3].string.replace(',', '.').strip()[:-3])
        quarter_low = float(tab_quarter[4].string.replace(',', '.').strip()[:-3])
        share_owned = soup.find("strong", text=re.compile(".*Owned.*")).find_next("td").string
        stock_price = soup.find("span", class_="nasdaqChangeHeader").find_next("span").string.strip()
        stock_change = soup.find("span", class_="valueContentPercent").find_next("span").string.strip()[1:-1]
        tab_divident_yield = soup.find("td", text= re.compile(".*Dividend Yield.*")).parent.select("td")
        div_yield_comapny = float(tab_divident_yield[1].string)
        div_yield_industry = float(tab_divident_yield[2].string)
        div_yield_sector = float(tab_divident_yield[3].string)

        data_reuters_byExchange[title].append("\nSales Quarter Ending Dec-18 (in millions): \nmean = " + str(quarter_mean) + "\nhigh = " + str(quarter_high) + "\nlow = " + str(quarter_low) + "\nShares Owned (%): " + share_owned + "\nStock Price: " + str(stock_price) + "\nStock change (%): "+stock_change+"\nDividend Yield: " + "nCompany = "+ str(div_yield_comapny) + "\nIndustry = " + str(div_yield_industry)+"\nSector = " + str(div_yield_sector))
        
    return data_reuters_byExchange

def main():
    company_list = ["Airbus", "LVMH", "Danone"]
    data_reuters = []
    for company in company_list:
        data_reuters_company = {}
        data_reuters_company["company"] = []
        data_reuters_company["company"].append(get_financial_information(_get_company_finance_urls(_get_company_overview_urls(_search_company_pattern(company)))))
        data_reuters.append(data_reuters_company)

    with open('C:/Users/sebas/OneDrive/Telecom/Git/Chaps/Scrap_Reuters/data_reuters.json', 'w') as outfile:  
        json.dump(data_reuters, outfile)
    

if __name__ == '__main__':
    main()
