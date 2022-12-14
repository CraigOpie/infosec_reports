#!/usr/bin/env python3
# coding: utf-8
"""
__description__ = "h1 vulnerability report scrapper"
__course__ = "ics691e"
__organization__ = "Information and Computer Sciences Department, University of Hawai'i at Mānoa"
__author__ = "Craig Opie"
__email__ = "opieca@hawaii.edu"
__version__ = "1.0.0"
__created__ = "2022-10-01"
__modified__ = "2022-10-10"
__maintainer__ = "Craig Opie"
"""
import sys
import os
import json
import csv
import argparse
import mybanner
import platform
import sqlite3 as sql
from bs4 import BeautifulSoup
from time import sleep
from time import perf_counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

## future imports
# import threading
# from selenium.common.exceptions import TimeoutException


class Scraper:
    # class constants
    DATABASE = {}
    CONN = sql.connect('h1.db')
    SCROLL_PAUSE_TIME = 1
    UNDISCLOSED_EXISTS = False
    WINDOWS_PLATFORM = False
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }

    def __init__(self, windows: bool, source: str, duration: float, key_word: str, order: str, type: str, filename: str):
        self.WINDOWS_PLATFORM = windows
        self.sources = {
            "hackerone": "https://hackerone.com/hacktivity?querystring=&filter=type:public&order_direction=DESC&order_field=popular&followed_only=false&collaboration_only=false",
        }
        self.url = str(self.sources[source])
        if (key_word != ''): self.url = str(self.sources[source].replace('=&', '= &').replace(' ', key_word))
        if (order != 'popular'): self.url = str(self.sources[source].replace('popular', 'latest_disclosable_activity_at'))
        if (type != 'public'): self.url = str(self.sources[source].replace('public', type))

        self.duration = float(duration)
        self.filename = filename


        ## headless mode is broken for linux
        self.options = Options()
        if self.WINDOWS_PLATFORM: self.options.add_argument('--headless')
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=self.options)

        self.CONN.execute('''CREATE TABLE IF NOT EXISTS REPORTS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            DATE TEXT,
            TITLE TEXT,
            REPORT_NUMBER TEXT NOT NULL,
            URL TEXT NOT NULL,
            SEVERITY_RATING TEXT,
            CVE TEXT,
            WEAKNESS TEXT,
            BOUNTY TEXT,
            UPVOTES TEXT,
            DETAILS TEXT);''')
        self.CONN.commit()
        self.CONN.close()


    def _load_page(self):
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "infinite-scroll-component")))
        except:
            print('ERROR: Unable to load page.')
            self.driver.quit()
            sys.exit(1)
        ## sleep to ensure javascript DOM has finished loading
        sleep(2)


    def _scroll_page(self):
        start_time = perf_counter()
        while (perf_counter() - start_time) < float(self.duration):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(self.SCROLL_PAUSE_TIME)

    def _parse_page(self):
        ## sleep to ensure javascript DOM has finished loading
        sleep(1)
        self.DATABASE['reports'] = []

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        items = soup.find_all('div', class_='hacktivity-item')
        for item in items:
            _report = {}
            index = 0
            title = ""
            report_number = ""
            url = ""
            cve = ""

            ## Javascript DOM broke BeautifulSoup so I had to use Garbage Code to get the data
            tags = str(item.find('a', class_='spec-hacktivity-item-title')).replace('<a class=\"daisy-link routerlink daisy-link hacktivity-item__publicly-disclosed spec-hacktivity-item-title\" href=\"', '').replace('\">', '').replace('</a>', '').replace('</strong>', '').split('<strong>')
            for tag in tags:
                if index == 1:
                    title = str(tag).strip().replace(',', '')
                else:
                    report_number = str(tag).split('/')[-1].replace(',', '')
                    url = str('https://hackerone.com' + tag)
                index += 1

            if ('CVE-' in title):
                cve = title.split('CVE-')[1].split(' ')[0].replace(':', '').replace(')', '')
                cve = 'CVE-' + cve
            
            ## Javascript DOM broke BeautifulSoup so I had to use Garbage Code to get the data
            rating = str(item.find('div', class_='spec-severity-rating')).replace('<div class=\"sc-bcXHqe NcSfA daisy-severity-label spec-severity-rating\">', '').replace('</div>', '')

            ## Javascript DOM broke BeautifulSoup so I had to use Garbage Code to get the data
            bounty = str(item.find('strong', class_='spec-hacktivity-item-bounty')).replace('<strong class=\"spec-hacktivity-item-bounty\">', '').replace('</strong>', '').replace(',', '')
            if str(bounty) == '':
                bounty = '0.00'

            ## Javascript DOM broke BeautifulSoup so I had to use Garbage Code to get the data
            upvotes = str(item.find('span', class_='inline-help')).replace('<span class=\"inline-help\" style=\"display: inline-flex;\">', '').replace('</span>', '').replace(',', '')
            if str(upvotes) == '':
                upvotes = '0'

            ## Publish the information for disclosed reports
            if title != '':
                _report['title'] = str(title)
                _report['report number'] = str(report_number).replace('" rel="" target="', '')
                _report['url'] = str(url)
                _report['severity rating'] = rating
                _report['bounty'] = str(bounty).replace('$', '').replace(',', '')
                _report['upvotes'] = str(upvotes)

                self.CONN = sql.connect('h1.db')
                self.DATABASE['reports'].append(_report)
                self.CONN.execute("INSERT INTO REPORTS (TITLE,REPORT_NUMBER,URL,SEVERITY_RATING,CVE,BOUNTY,UPVOTES) VALUES (?, ?, ?, ?, ?, ?, ?)", (str(title), str(report_number), str(url), str(rating), str(cve), str(bounty), str(upvotes)))    
                self.CONN.commit()
                self.CONN.close()

            ## Warn the user that there are undisclosed reports
            else:
                self.UNDISCLOSED_EXISTS = True

        self.driver.quit()

    def _save_data(self):
        if self.filename.split('.')[-1] == 'json':
            with open(self.filename, 'w') as file:
                json.dump(self.DATABASE, file, indent=4)
        elif self.filename.split('.')[-1] == 'csv':
            with open(self.filename, 'w') as file:
                writer = csv.writer(file)
                writer.writerow(self.DATABASE['reports'][0].keys())
                for report in self.DATABASE['reports']:
                    writer.writerow(report.values())

    def _sloppy_deep_dive(self):
        self.options = Options()
        if self.WINDOWS_PLATFORM: self.options.add_argument('--headless')
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=self.options)

        for report in self.DATABASE['reports']:
            try:
                self.driver.get(report['url'])
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "report-information")))

                start_time = perf_counter()
                while (perf_counter() - start_time) < 6:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    sleep(self.SCROLL_PAUSE_TIME)
                sleep(2)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                entries = soup.find_all('div', class_='timeline-container-content')
                md_string = ''
                for entry in entries:
                    md_string += entry.text.replace('"', "'").replace('\n', " ")
                report['details'] = md_string

                item = soup.find('div', class_='spec-weakness-meta-item')
                weakness = str(item.find('small')).replace('<small>', '').replace('</small>', '')

                item = soup.find('div', class_='spec-reported-at')
                date = str(item.find('div', class_='daisy-helper-text')).replace('<div class="daisy-helper-text">', '').replace('</div>', '').replace('Reported', '').replace(' +0000', '').strip()


                self.CONN = sql.connect('h1.db')
                self.CONN.execute("UPDATE REPORTS SET DETAILS = ? WHERE REPORT_NUMBER = ?", (str(md_string), str(report['report number'])))
                self.CONN.execute("UPDATE REPORTS SET WEAKNESS = ? WHERE REPORT_NUMBER = ?", (str(weakness), str(report['report number'])))
                self.CONN.execute("UPDATE REPORTS SET DATE = ? WHERE REPORT_NUMBER = ?", (str(date), str(report['report number'])))
                self.CONN.commit()
                self.CONN.close()
            except:
                self.CONN = sql.connect('h1.db')
                self.CONN.execute("DELETE FROM REPORTS WHERE REPORT_NUMBER = ?", (str(report['report number']),))
                self.CONN.commit()
                self.CONN.close()

        self.driver.quit()

    def _print_data(self):
        print(json.dumps(self.DATABASE, indent=4))
        if self.UNDISCLOSED_EXISTS:
            print('WARNING: Undisclosed reports exist. Please allow time for the report numbers to be published. Additionally, using a key word may help.')

    @staticmethod
    def _animated_loading():
        steps = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        for step in steps:
            sys.stdout.write("\r" + step)
            sleep(0.1)
            sys.stdout.flush()

    def _scan_report(self):
        pass


if __name__ == "__main__":
    argv = argparse.ArgumentParser(usage = "main.py -s [ SOURCE ] -d [ DURATION ] -k [ KEY_WORD ] -o [ ORDER ] -t [ TYPE ]")
    argv.add_argument("-s", "--source", default="hackerone", help="Source to scrape from <hackerone>")
    argv.add_argument("-d","--duration", default=5, help="Duration to scrape for <seconds>")
    argv.add_argument("-k", "--key_word", default="", help="Key word to search for <api>")
    argv.add_argument("-o", "--order", default="popular", help="Order to sort by <popular | new>")
    argv.add_argument("-t", "--type", default="public", help="<all | bounty-awarded | hacker-published | public>")
    argv.add_argument("-f", "--file_out", default="outfile_db.json", help="<name and extension of the file to create>")

    parser = argv.parse_args()
    source = parser.source
    key_word = parser.key_word
    duration = parser.duration
    order = parser.order
    type = parser.type
    filename = parser.file_out
    windows = False

    if(platform.system() == 'Windows'):
        os.system('cls')
        windows = True
    if (platform.system() == 'Linux'):
        os.system('clear')

    cyber_banner = mybanner.CyberBanner()
    cyber_banner.print_banner()

    scraper = Scraper(windows, source, duration, key_word, order, type, filename)
    scraper._load_page()
    scraper._scroll_page()
    scraper._parse_page()
    scraper._sloppy_deep_dive()
    scraper._save_data()
    scraper._print_data()
