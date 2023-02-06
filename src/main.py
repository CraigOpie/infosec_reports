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
from spinner import Spinner
from time import sleep
from time import perf_counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class Scraper:
    database = {}
    db_name = 'h1.db'
    scroll_pause_time = 1

    def __init__(self, source: str, duration: float, key_word: str, order: str, type: str, print_: bool, filename: str, headless: bool):
        self.headless = headless
        self.sources = {
            "hackerone": "https://hackerone.com/hacktivity?querystring=&filter=type:public&order_direction=DESC&order_field=popular&followed_only=false&collaboration_only=false",
        }
        self.url = self.sources[source]
        self.url = self.url.replace('=&', '= &') if key_word != '' else self.url
        self.url = self.url.replace('popular', 'latest_disclosable_activity_at') if order != 'popular' else self.url
        self.url = self.url.replace('public', type) if type != 'public' else self.url
        self.print_results = print_
        self.undisclosed_exists = False

        self.duration = float(duration)
        self.filename = filename
        
        self.options = Options()
        self.options.add_argument('--headless') if self.headless else None
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=self.options)

        try:
            with sql.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS REPORTS (
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
                conn.commit()
        except sql.Error as e:
            print()
            print(f'ERROR: Unable to connect to database. {e}')
        finally:
            sql.connect(self.db_name).close()

    def _load_page(self):
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "infinite-scroll-component")))
        except Exception as e:
            print()
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

                try:
                    with sql.connect(self.db_name) as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO REPORTS (TITLE, REPORT_NUMBER, URL, SEVERITY_RATING, CVE, BOUNTY, UPVOTES) VALUES (?, ?, ?, ?, ?, ?, ?)", (title, report_number, url, rating, cve, bounty, upvotes))
                        conn.commit()
                except sql.Error as e:
                    print()
                    print(f'ERROR: Unable to connect to database. {e}')
                finally:
                    sql.connect(self.db_name).close()
            else:
                self.undisclosed_exists = True

    def _deep_dive(self):
        report_scan_time = 6

        for report in self.database['reports']:
            end_time = perf_counter() + report_scan_time
            self.driver.get(report['url'])
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "report-information")))

            while perf_counter() <= end_time:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(self.scroll_pause_time)

            sleep(1)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            try:
                report['details'] = self._parse_details(soup)
                report['weakness'] = self._parse_weakness(soup)
                report['date'] = self._parse_date(soup)

                try:
                    with sql.connect(self.db_name) as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE REPORTS SET DETAILS = ? WHERE REPORT_NUMBER = ?", (report['details'], report['report number']))
                        cursor.execute("UPDATE REPORTS SET WEAKNESS = ? WHERE REPORT_NUMBER = ?", (report['weakness'], report['report number']))
                        cursor.execute("UPDATE REPORTS SET DATE = ? WHERE REPORT_NUMBER = ?", (report['date'], report['report number']))
                        conn.commit()
                except sql.Error as e:
                    print()
                    print(f'ERROR: Unable to connect to database. {e}')
                finally:
                    sql.connect(self.db_name).close()

            except:
                try:
                    with sql.connect(self.db_name) as conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM REPORTS WHERE REPORT_NUMBER = ?", (report['report number'],))
                        conn.commit()
                except sql.Error as e:
                    print()
                    print(f'ERROR: Unable to connect to database. {e}')
                finally:
                    sql.connect(self.db_name).close()

    def _parse_header(self, item):
        header_element = item.find('a', class_='spec-hacktivity-item-title')
        href = header_element['href']
        title = header_element.strong.text.strip().replace(',', '')
        report_number = href.rstrip('/').split('/')[-1].replace(',', '')
        url = f'https://hackerone.com{href}'
        return str(title), str(report_number), str(url)
    
    def _parse_cve(self, title):
        return 'CVE-' + title.split('CVE-')[1].split(' ')[0].replace(':', '').replace(')', '') if 'CVE-' in title else ""

    def _parse_rating(self, item):
        rating = str(item.find('div', class_='spec-severity-rating'))
        rating = rating.replace('<div class=\"sc-bcXHqe NcSfA daisy-severity-label spec-severity-rating\">', '')
        rating = rating.replace('</div>', '').strip()
        return str(rating)

    def _parse_bounty(self, item):
        bounty = str(item.find('strong', class_='spec-hacktivity-item-bounty'))
        bounty = bounty.replace('<strong class=\"spec-hacktivity-item-bounty\">', '').replace('</strong>', '').replace(',', '')
        bounty = bounty.strip().replace('$', '').replace(',', '') if bounty else '0.00'
        return str(bounty)

    def _parse_upvotes(self, item):
        upvotes = item.find('span', class_='inline-help').text
        upvotes = upvotes.strip().replace(',', '') if upvotes else '0'
        return str(upvotes)

    def _parse_details(self, soup):
        md_string = ''
        entries = soup.find_all('div', class_='timeline-container-content')
        for entry in entries:
            md_string += entry.text.replace('"', "'").replace('\n', " ")
        return str(md_string)

    def _parse_weakness(self, soup):
        item = soup.find('div', class_='spec-weakness-meta-item')
        weakness = str(item.find('small')).replace('<small>', '').replace('</small>', '')
        return str(weakness)

    def _parse_date(self, soup):
        item = soup.find('div', class_='spec-reported-at')
        date = str(item.find('div', class_='daisy-helper-text')).replace('<div class="daisy-helper-text">', '')
        date = date.replace('</div>', '').replace('Reported', '').replace(' +0000', '').strip()
        return str(date)

    def _print_data(self):
        print()
        print(f"Total reports: {len(self.database['reports'])}")
        print("[DATA] DOES NOT INCLUDE DEEP DIVE INFORMATION")
        print(json.dumps(self.database, indent=4))

    def _run(self):
        print('[INFO] Scraping data from HackerOne', end=' ')
        with Spinner():
            try:
                self._load_page()
                self._scroll_page()
                self._parse_page()
                self._deep_dive()
                self._print_data() if self.print_results else None
            except Exception as e:
                print()
                print(e)
            finally:
                self._deconstructor()
        if self.undisclosed_exists:
            print()
            print("[WARNING] Undisclosed reports exist. Please allow time for the report numbers to be published. "
                "Additionally, using a keyword may help.")

    def _deconstructor(self):
        self.driver.quit()

def main():
    argv = argparse.ArgumentParser(usage = "main.py -s [ SOURCE ] -d [ DURATION ] -k [ KEY_WORD ] -o [ ORDER ] -t [ TYPE ] -p [ PRINT ] -f [ FILE_OUT ] -h [ HEADLESS]")
    argv.add_argument("-s", "--source", default="hackerone", help="Source to scrape from <hackerone>")
    argv.add_argument("-d","--duration", default=5, help="Duration to scrape for <seconds>")
    argv.add_argument("-k", "--key_word", default="", help="Key word to search for <api>")
    argv.add_argument("-o", "--order", default="popular", help="Order to sort by <popular | new>")
    argv.add_argument("-t", "--type", default="public", help="<all | bounty-awarded | hacker-published | public>")
    argv.add_argument("-p", "--print", default="False", help="Print output to console <True | False>")
    argv.add_argument("-f", "--file_out", default="outfile_db.json", help="<name and extension of the file to create>")
    argv.add_argument("-H", "--headless", default="False", help="Use headless mode for selenium <True | False>")
    arguments = argv.parse_args()

    headless = False
    if(platform.system() == 'Windows'):
        os.system('cls')
        headless = True
    if arguments.headless.title() == "True":
        headless = True
    if (platform.system() == 'Linux'):
        os.system('clear')

    cyber_banner = CyberBanner()
    cyber_banner.print_banner()

    start = perf_counter()
    scraper = Scraper(arguments.source, arguments.duration, arguments.key_word, arguments.order, arguments.type, arguments.print, arguments.file_out, headless)
    scraper._run()
    end = perf_counter()
    print(f'[INFO] Completed in {round(end-start, 2)} second(s)')

if __name__ == "__main__":
    main()
