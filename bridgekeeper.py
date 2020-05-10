#!/usr/bin/env python3

import re
import time
import argparse
from core.hunter import Hunter
from core.scraper import Scraper
from core.transformer import Transformer
import os.path
from os import path
import json

def update_row(name, idx, new_row):
    import pygsheets
    import pandas as pd
    #authorization
    gc = pygsheets.authorize(service_file='creds.json')

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open(name).sheet1
    #select the first sheet
    sh.update_row(idx + 1, values= new_row)

def write_row(name, idx, new_row):
    import pygsheets
    import pandas as pd
    #authorization
    gc = pygsheets.authorize(service_file='creds.json')

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open(name).sheet1
    #select the first sheet
    sh.insert_rows(row = idx, number = 1)
    sh.update_row(idx + 1, values= new_row)
    sh.sync()

def read_in_sheet(name):
    import pygsheets
    import pandas as pd
    #authorization
    gc = pygsheets.authorize(service_file='creds.json')

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open(name).sheet1
    #select the first sheet
    column_names = [i for i in sh.get_all_values()[0]]
    values = []
    rows = []
    for row in sh.get_all_values()[1:]:
        row = [i for i in row]
        row_value = {}
        for (x,y) in zip(column_names, row):
            if(y):
                row_value[x] = y
        if(row_value):
            rows.append(row_value)
    return rows, column_names

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape employee names from search engine LinkedIn profiles. Convert employee names to a specified username format.")

    # Allow a user to scrape names or just convert an already generated list of names
    parser.add_argument("-d", "--depth",   type=int, help="Number of pages to search each search engine. Default: 5", default=100)
    parser.add_argument("-t", "--timeout", type=int, help="Specify request timeout. Default: 25", default=25)
    parser.add_argument("-o", "--output",  type=str, help="Directory to write username files to.")
    parser.add_argument("--cookie",        type=str, help="File containing Google CAPTCHA bypass cookies")
    parser.add_argument("--proxy",         type=str, help="Proxy to pass traffic through: <ip:port>")
    parser.add_argument("--lower",         action="store_true", help="Force usernames to all lower case.")
    parser.add_argument("--upper",         action="store_true", help="Force usernames to all upper case.")
    parser.add_argument("--debug",         action="store_true", help="Enable debug output.")
    args = parser.parse_args()
    config = {}
    with open('config.json') as config_file:
        config = json.load(config_file)

    keywords, a = read_in_sheet(config['Keywords'])
    companies, companies_column_names = read_in_sheet(config['Companies'])
    start  = time.time()
    output = args.output if args.output else "./"
    for idx_company, company in enumerate(companies):
        for idx_keyword, keyword in enumerate(keywords):
            if keyword['MARKET'] == company['MARKET']:
                if company['TO SCRAPE'] == 'TRUE' or company['TO SCRAPE'] == 'PRAWDA':
                    if not path.exists("%s/%s.txt" % (output, keyword['KEYWORD']+company['NAME'])):
                        scraper = Scraper(company['NAME'], cookies=args.cookie, depth=args.depth, timeout=args.timeout, proxy=args.proxy, keyword=keyword['KEYWORD'], location=company['LOCATION'], config=config)
                        scraper.loop.run_until_complete(scraper.run())
                        print("\n\n[+] Names Found: %d" % len(scraper.employees))
                        print("[*] Writing names to the following directory: %s" % output)
                        with open("%s/%s.txt" % (output, keyword['KEYWORD']+company['NAME']), 'w') as f:
                            for name in scraper.employees:
                                f.write("%s\n" % name)
                    contacts, contacts_column_names = read_in_sheet(config['Contacts'])
                    existing_contracts = len(contacts)
                    print("Inserting contacts with keyword " + keyword['KEYWORD'] + " from company " + company['NAME'])
                    with open("%s/%s.txt" % (output, keyword['KEYWORD']+company['NAME']), 'r') as f:
                        lines = f.readlines()
                        for idx, line in enumerate(lines):
                            line = line.strip()
                            line = line.split(',')
                            contact = {}
                            contact['ROLE'] = line[2]
                            contact['NAME'] = line[0]
                            contact['LINKEDIN'] = line[1]
                            contact['COMPANY'] = company['NAME']
                            row = [contact.get(column_name, '') for column_name in contacts_column_names]
                            write_row('Contacts', existing_contracts + idx + 1, row)
        company['TO SCRAPE'] = 'FALSE'
        update_row('Companies', idx_company + 1, [company[key] if key in company else '' for key in companies_column_names])






    if args.debug: print("\n[DEBUG] %s executed in %0.4f seconds." % (__file__, elapsed))