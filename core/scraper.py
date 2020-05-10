#!/usr/bin/env python3

import re
import time
import random
import asyncio
import urllib3
import requests
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from random import randint
from time import sleep
import lxml.html
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
"""A Search Engine scraper for LinkedIn profile names."""

class Scraper:

    # Asyncio Event Loop
    loop = asyncio.get_event_loop()

    # List of found employee names - use a set to keep unique across search engines
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    def __init__(self, company, cookies=None, depth=5, timeout=25, proxy=None, keyword="", location="", config={}):
        self.company = company
        self.depth   = depth
        self.keyword = keyword
        self.location = location
        self.timeout = timeout
        self.employees = set()
        self.config = config
        self.cookies = None if not cookies else self.__set_cookie(cookies)
        self.proxy   = None if not proxy else {
            "http": proxy, "https": proxy
        }
        self.data = { # Data sets for each search engine
            "bing": {
                "url":  'https://www.bing.com/search?q=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22+%22{keyword}%22+%22{location}%22&start={INDEX}',
                "element": ["li", "class", "b_algo"],
                "html": ["a"],
                "idx":  lambda x: x * 14,
                'content': 'aside',
                'by': By.TAG_NAME
            },
            "google": {
                "url":  'https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22+%22{keyword}%22+%22{location}%22&start={INDEX}',
                "html": ["h3", "class", "LC20lb"],
                "element": ["div", "class", "g"],
                "idx":  lambda x: x * 10,
                'content': 'main',
                'by': By.ID
            },
            "yahoo": {
                "button": "agree",
                "url":  'https://search.yahoo.com/search?p=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22+%22{keyword}%22+%22{location}%22&b={INDEX}',
                "element": ["a", "class", "ac-algo fz-l ac-21th lh-24"],
                "idx":  lambda x: (x * 10) + 1,
                "content": 'ys',
                'by': By.ID#
            }
        }

        self.linked_in_driver = webdriver.Chrome(ChromeDriverManager().install())
        self.linked_in_driver.get('https://www.linkedin.com/')
        self.linked_in_driver.find_element_by_xpath('//a[text()="Sign in"]').click()
        self.username_input = self.linked_in_driver.find_element_by_name('session_key')
        self.username_input.send_keys(self.config['linkedin_login'])
        self.password_input = self.linked_in_driver.find_element_by_name('session_password')
        self.password_input.send_keys(self.config['linkedin_password'])
        self.linked_in_driver.find_element_by_xpath('//button[text()="Sign in"]').click()

        # Keep track of current depth of each search engine
        self.cur_d = {'google': 0, 'yahoo': 0, 'bing': 0}
        self.tot_d = self.depth * 3

    def __set_cookie(self, cookie_file):
        cookies  = {}
        _cookies = [x.strip() for x in open(cookie_file).readlines()]
        for _cook in _cookies:
            for cookie in _cook.split(';'):
              cookie = cookie.strip()
              name,value = cookie.split('=', 1)
              cookies[name] = value

        return cookies

    def get_random_moves(self):
        import numpy as np
        import scipy.interpolate as si

        # Curve base:
        points = [[0, 0], [0, 2], [2, 3], [4, 0], [6, 3], [8, 2], [8, 0]];
        points = np.array(points)

        x = points[:,0]
        y = points[:,1]


        t = range(len(points))
        ipl_t = np.linspace(0.0, len(points) - 1, 100)

        x_tup = si.splrep(t, x, k=3)
        y_tup = si.splrep(t, y, k=3)

        x_list = list(x_tup)
        xl = x.tolist()
        x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

        y_list = list(y_tup)
        yl = y.tolist()
        y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

        x_i = si.splev(ipl_t, x_list) # x interpolate values
        y_i = si.splev(ipl_t, y_list) # y interpolate values
        return x_i, y_i

    def perform_random_browser_moves(self, driver, content, by):
        x_i, y_i = self.get_random_moves()
        action =  ActionChains(driver);
        WebDriverWait(driver, 3600000).until(EC.presence_of_element_located((by, content)))
        startElement = driver.find_element(by, content)

        # First, go to your start point or Element:
        action.move_to_element(startElement);
        action.perform();

        for mouse_x, mouse_y in zip():
            action.move_by_offset(mouse_x,mouse_y);
            action.perform();
            print(mouse_x, mouse_y)

    def __get_name(self, data, se):
        if se == 'bing':
            return re.sub(' (-|–|\xe2\x80\x93).*', '', data.findAll('a')[0].getText()) # re.search('((?<=>)[A-Z].+?) - ', str(data)).group(1)

        return re.sub(' (-|–|\xe2\x80\x93).*', '', data.getText())

    def __get_job(self, data, se, link):
        if se == 'bing':
            result = re.search('.*-(.*)-.*|.*', data.getText()).group(1) # re.search('((?<=>)[A-Z].+?) - ', str(data)).group(1)

        result = re.search('.*-(.*)-.*|.*', data.getText()).group(1)
        if result:
            return result
        try:


            self.linked_in_driver.get(link)
            result = BeautifulSoup(linked_in_driver.page_source, "lxml")
            result = result.findAll('h2', {'class': 'mt1 t-18 t-black t-normal break-words'})[0].text
            result = result[:result.index('at')]
            result = result[:result.index('@')]
            result = result.strip()
        except:
            pass
        return result

    def __clean(self, data):
        # From: https://github.com/initstring/linkedin2username/blob/master/linkedin2username.py
        accents = {
            'a':  u"[àáâãäå]",
            'e':  u"[èéêë]",
            'i':  u"[ìíîï]",
            'o':  u"[òóôõö]",
            'u':  u"[ùúûü]",
            'y':  u"[ýÿ]",
            'n':  u"[ñ]",
            'ss': u"[ß]"
        }
        for k,v in accents.items():
            data = re.sub(u"%s" % v, k, data)

        # Remove Prefixes/Titles/Certs in names and clean
        for r in [",.*", "\(.+?\)", "(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)", "I[IV][I]?", "'", "(Jr\.|Sr\.)"]:
            data = re.sub(r, '', data)
        data = re.sub("\.", ' ', data)
        data = re.sub("\s+", ' ', data)
        data = re.sub("Web results", '', data)
        chr_map = re.compile("[^a-zA-Z -]")
        data    = chr_map.sub('', data)

        return data.strip()

    def http_req(self, se):
        print('[*] Gathering names from %s (depth=%d)' % (se.title(), self.depth))
        people = set()
        names   = []
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
          "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        cookies = None if se != "google" else self.cookies
        index = 1
        stop = False
        for index in range(self.depth):
            if stop:
                break
            print("Serving page "+str(index)+" from search engine "+se)
            driver.get(self.data[se]["url"].format(COMPANY=self.company, location=self.location, keyword=self.keyword, INDEX=(self.data[se]["idx"](index))))
            if("button" in self.data[se]):
                try:
                    driver.find_element_by_xpath('//button[text()="I agree"]').click()
                except:
                    pass
            self.perform_random_browser_moves(driver, self.data[se]["content"], self.data[se]["by"])
            if 'solving the above CAPTCHA' not in driver.page_source:
                self.cur_d[se] += 1
                result = BeautifulSoup(driver.page_source, "lxml")
                if 'element' in self.data[se]:
                    element = self.data[se]['element']
                    result = result.findAll(element[0], {element[1]: element[2]})

                if result:
                    seen = 0
                    for soup in result:
                        text = soup
                        if 'html' in self.data[se]:
                            html = self.data[se]['html']
                            if(len(html) > 1):
                                text = soup.findAll(html[0], {html[1]: html[2]})[0]
                            else:
                                text = soup.findAll(html[0])[0]
                        name = ''
                        link =''
                        name = self.__get_name(soup, se)
                        try:
                            link = soup['href']
                        except:
                            pass
                        for a in soup.findAll('a'):
                            try:
                                if (a['href'].startswith('https://uk.linkedin.com/in')) and ('related' not in a['href']):
                                    link = a['href']
                            except:
                                pass
                        job  = self.__get_job(text, se, link)
                        if link and job :
                            name_to_add = self.__clean(name)
                            if name_to_add not in people:
                                seen = seen + 1
                                people.add(self.__clean(name))
                            if job and (self.keyword.lower() in job.lower()) :
                                names.append(",".join([name_to_add,link,job.strip()]))
                    if seen == 0:
                        stop = True
                        print("Reached end of records in search engine " + se)
                    else:
                        print("Found "+ str(seen) + " records in search engine " + se)
                else:
                    print("Reached end of records in search engine " + se)
                    # Assume we hit the final page
                    break
                from selenium.webdriver.common.keys import Keys
                html = driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                # Search engine blacklist evasion technique
                # Sleep for random times between a half second and a full second
                time.sleep(round(random.uniform(1.0, 4.0), 2))

            else:
                self.cur_d[se] = self.depth
                print("[!] CAPTCHA triggered for %s, solve it in browser" % se)
                WebDriverWait(driver, 360000000).until(EC.presence_of_element_located((self.data[se]["by"], self.data[se]["content"])))
            index = index + 1

        return names

    async def run(self):
        """ Asynchronously send HTTP requests
        Here we are going to create three coroutines - one for each
        search engine. To avoid overloading the search engines and getting
        blacklisted, we are going to sleep after each request - if we don't
        contain the coroutines then asyncio will dump requests without waiting. """
        print("[*] Starting %d coroutines to throttle requests to each search engine." % (len(self.data)))
        futures = [
            self.loop.run_in_executor(
                None, self.http_req, se
            ) for se in self.data.keys()
        ]

        for data in asyncio.as_completed(futures):
            names = await data
            self.employees.update(names)