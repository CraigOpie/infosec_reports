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
import argparse
import platform
import sqlite3 as sql
from bs4 import BeautifulSoup
from cyberbanner import CyberBanner
from time import sleep
from time import perf_counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class Scraper:
    database = {}
    windows_platform = False
    undisclosed_exists = False
    scroll_pause_time = 1

    def __init__(self, windows: bool, source: str, duration: float, key_word: str, order: str, type: str, filename: str):
        self.windows_platform = windows
        self.sources = {
            "hackerone": "https://hackerone.com/hacktivity?querystring=&filter=type:public&order_direction=DESC&order_field=popular&followed_only=false&collaboration_only=false",
        }
        self.url = self.sources[source]
        self.url = self.url.replace('=&', '= &') if key_word != '' else self.url
        self.url = self.url.replace('popular', 'latest_disclosable_activity_at') if order != 'popular' else self.url
        self.url = self.url.replace('public', type) if type != 'public' else self.url

        self.duration = float(duration)
        self.filename = filename
        
        self.options = Options()
        self.options.add_argument('--headless') if self.windows_platform else None
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=self.options)
        self.conn = sql.connect('h1.db')

        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS REPORTS (
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
            self.conn.commit()

    def _load_page(self):
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "infinite-scroll-component")))
        except Exception as e:
            print(f'ERROR: Unable to load page. {e}')
            self.driver.quit()
            sys.exit(1)
        sleep(2)

    def _scroll_page(self):
        end_time = perf_counter() + float(self.duration)
        while perf_counter() < end_time:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(self.scroll_pause_time)

    def _parse_page(self):
        sleep(1)
        self.database['reports'] = []

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        items = soup.find_all('div', class_='hacktivity-item')
        for item in items:
            title, report_number, url = self._parse_header(item)
            cve = self._parse_cve(title)
            rating = self._parse_rating(item)
            bounty = self._parse_bounty(item)
            upvotes = self._parse_upvotes(item)

            if title:
                self.database['reports'].append({
                    'title': title,
                    'report number': report_number,
                    'url': url,
                    'severity rating': rating,
                    'bounty': bounty,
                    'upvotes': upvotes,
                    'cve': cve
                })

                with self.conn:
                    self.conn.execute(
                        "INSERT INTO REPORTS (TITLE, REPORT_NUMBER, URL, SEVERITY_RATING, CVE, BOUNTY, UPVOTES) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (title, report_number, url, rating, cve, bounty, upvotes)
                    )
                    self.conn.commit()
            else:
                self.undisclosed_exists = True

    def _deep_dive(self):
        report_scan_time = 6

        for report in self.database['reports']:
            try:
                end_time = perf_counter() + report_scan_time
                self.driver.get(report['url'])
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "report-information")))

                while perf_counter() < end_time:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    sleep(self.SCROLL_PAUSE_TIME)

                sleep(1)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                print(report)

                report['details'] = self._parse_details(soup)
                report['weakness'] = self._parse_weakness(soup)
                report['date'] = self._parse_date(soup)

                with self.conn:
                    self.conn.execute("UPDATE REPORTS SET DETAILS = ? WHERE REPORT_NUMBER = ?", \
                        (report['details'], report['report number']))
                    self.conn.execute("UPDATE REPORTS SET WEAKNESS = ? WHERE REPORT_NUMBER = ?", \
                        (report['weakness'], report['report number']))
                    self.conn.execute("UPDATE REPORTS SET DATE = ? WHERE REPORT_NUMBER = ?", \
                        (report['date'], report['report number']))
                    self.conn.commit()
            except:
                with self.conn:
                    self.conn.execute("DELETE FROM REPORTS WHERE REPORT_NUMBER = ?", (report['report number'],))
                    self.conn.commit()

    def _parse_header(self, item):
        header_element = item.find('a', class_='spec-hacktivity-item-title')
        href = header_element['href']
        title = header_element.strong.text.strip().replace(',', '')
        report_number = href.rstrip('/').split('/')[-1].replace(',', '')
        url = f'https://hackerone.com{href}'
        return title, report_number, url
    
    def _parse_cve(self, title):
        return 'CVE-' + title.split('CVE-')[1].split(' ')[0].replace(':', '').replace(')', '') if 'CVE-' in title else ""

    def _parse_rating(self, item):
        rating = str(item.find('div', class_='spec-severity-rating'))
        rating = rating.replace('<div class=\"sc-bcXHqe NcSfA daisy-severity-label spec-severity-rating\">', '')
        rating = rating.replace('</div>', '').strip()
        return rating

    def _parse_bounty(self, item):
        bounty = str(item.find('strong', class_='spec-hacktivity-item-bounty'))
        bounty = bounty.replace('<strong class=\"spec-hacktivity-item-bounty\">', '').replace('</strong>', '').replace(',', '')
        bounty = bounty.strip().replace('$', '').replace(',', '') if bounty else '0.00'
        return bounty

    def _parse_upvotes(self, item):
        upvotes = item.find('span', class_='inline-help').text
        upvotes = upvotes.strip().replace(',', '') if upvotes else '0'
        return upvotes

    def _parse_details(self, soup):
        entries = soup.find_all('div', class_='timeline-container-content')
        md_string = ''.join(entry.text.replace('"', "'").replace('\n', " ") for entry in entries)
        return md_string

    def _parse_weakness(self, soup):
        item = soup.find('div', class_='spec-weakness-meta-item')
        weakness = item.find('small').text
        return weakness

    def _parse_date(self, soup):
        item = soup.find('div', class_='spec-report-date')
        date = item.find('div', class_='daisy-helper-text').text.replace('Reported', '').replace(' +0000', '').strip()
        return date

    def _print_data(self):
        print(f"Total reports: {len(self.database['reports'])}")
        print("[DATA] DOES NOT INCLUDE DEEP DIVE INFORMATION")
        print(json.dumps(self.database, indent=4))
        if self.undisclosed_exists:
            print("WARNING: Undisclosed reports exist. Please allow time for the report numbers to be published. "
                "Additionally, using a keyword may help.")

    def _run(self):
        self._load_page()
        self._scroll_page()
        self._parse_page()
        self._deep_dive()
        self._save_data()
        self._print_data()
        self._deconstructor()

    def _deconstructor(self):
        self.conn.close()
        self.driver.quit()

def main():
    argv = argparse.ArgumentParser(usage = "main.py -s [ SOURCE ] -d [ DURATION ] -k [ KEY_WORD ] -o [ ORDER ] -t [ TYPE ]")
    argv.add_argument("-s", "--source", default="hackerone", help="Source to scrape from <hackerone>")
    argv.add_argument("-d","--duration", default=5, help="Duration to scrape for <seconds>")
    argv.add_argument("-k", "--key_word", default="", help="Key word to search for <api>")
    argv.add_argument("-o", "--order", default="popular", help="Order to sort by <popular | new>")
    argv.add_argument("-t", "--type", default="public", help="<all | bounty-awarded | hacker-published | public>")
    argv.add_argument("-f", "--file_out", default="outfile_db.json", help="<name and extension of the file to create>")
    arguments = argv.parse_args()

    windows = False
    if(platform.system() == 'Windows'):
        os.system('cls')
        windows = True
    if (platform.system() == 'Linux'):
        os.system('clear')

    cyber_banner = CyberBanner()
    cyber_banner.print_banner()

    start = perf_counter()
    scraper = Scraper(windows, arguments.source, arguments.duration, arguments.key_word, arguments.order, arguments.type, arguments.file_out)
    scraper._run()
    end = perf_counter()
    print(f'[INFO] Completed in {round(end-start, 2)} second(s)')

if __name__ == "__main__":
    main()
