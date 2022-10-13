#!/usr/bin/env python3
# coding: utf-8
"""
__description__ = "h1 vulnerability report scrapper"
__course__ = "ics691e"
__organization__ = "Information and Computer Sciences Department, University of Hawai‘i at Mānoa"
__author__ = "Craig Opie"
__email__ = "opieca@hawaii.edu"
__version__ = "1.0.0"
__created__ = "2022-10-01"
__modified__ = "2022-10-10"
__maintainer__ = "Craig Opie"
"""
import os
import platform
import termcolor
import terminal_banner


class CyberBanner:
    def __init__(self):
        self.banner_title = \
            """
            ██     ██  █████  ██████  ███    ██ ██ ███    ██  ██████     
            ██     ██ ██   ██ ██   ██ ████   ██ ██ ████   ██ ██       ██ 
            ██  █  ██ ███████ ██████  ██ ██  ██ ██ ██ ██  ██ ██   ███    
            ██ ███ ██ ██   ██ ██   ██ ██  ██ ██ ██ ██  ██ ██ ██    ██ ██ 
             ███ ███  ██   ██ ██   ██ ██   ████ ██ ██   ████  ██████     
                                                                         
            """
        self.banner_statement = \
            """
            By using this tool, you agree to the terms and conditions of the HackerOne API
            and the HackerOne Terms of Service.  Additionally, you agree to the terms and
            conditions as outlined in the README.md file and will:
            - Not use this tool for any illegal or malicious purposes.
            - Keep private and confidential information gained in your professional work,
            (in particular as it pertains to client lists and client personal information).
            - Not collect, give, sell, or transfer any personal information (such as name,
            e-mail address, Social Security number, or other unique identifier) to a third
            party without client prior consent.
            - Protect the intellectual property of others by relying on your own innovation
            and efforts, thus ensuring that all benefits vest with its originator.
            - Disclose to appropriate persons or authorities potential dangers to any
            ecommerce clients, the Internet community, or the public, that you reasonably
            believe to be associated with a particular set or type of electronic
            transactions or related software or hardware.
            - Never knowingly use software or process that is obtained or retained either
            illegally or unethically.
            - Ensure ethical conduct and professional care at all times on all professional
            assignments without prejudice.
            - Not to purposefully compromise or allow the client organization’s systems to
            be compromised in the course of your professional dealings.
            - Ensure all penetration testing activities are authorized and within legal
            limits.
            
            This tool is for educational purposes only. The author is not responsible for
            any misuse of this tool. This tool is not affiliated with HackerOne in any way.
            Use at your own risk.
            """
        self.banner_author = "            Tool Developed by: Craig Opie"
        self.banner_version = "            Version: 1.0.0\n"

        self.banner = terminal_banner.Banner(self.banner_title)

    def print_banner(self):
        if platform.system() == 'Windows':
            os.system('cls')
        if platform.system() == 'Linux':
            os.system('clear')
        print(termcolor.colored(self.banner.text, 'white'))
        print(termcolor.colored(self.banner_statement, 'red', attrs=['bold']))
        print(termcolor.colored(self.banner_author, 'white', attrs=['bold']))
        print(termcolor.colored(self.banner_version, 'white'))
