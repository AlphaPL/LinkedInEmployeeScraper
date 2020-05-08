#!/usr/bin/env python3

import re
import time
import argparse
from core.hunter import Hunter
from core.scraper import Scraper
from core.transformer import Transformer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape employee names from search engine LinkedIn profiles. Convert employee names to a specified username format.")

    # Allow a user to scrape names or just convert an already generated list of names
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--company", type=str, help="Target company to search for LinkedIn profiles (e.g. 'Example Ltd.').")
    group.add_argument("-F", "--file",    type=str, help="File containing names to be converted to usernames. Name format: 'First Last'")
    parser.add_argument("-k", "--keyword", type=str, help="Keyword to search profiles with." , default="")
    parser.add_argument("-l", "--location", type=str, help="Location of the profile.", default="United Kingdom")

    parser.add_argument("-f", "--format",  type=str, help="Specify username format. Valid format identifiers: {first}, {middle}, {last}, {f}, {m}, {l}, [#] (For trimming names)")
    parser.add_argument("-D", "--domain",  type=str, help="Domain name of target company for Hunter.io email format identification and email scraping.")
    parser.add_argument("-d", "--depth",   type=int, help="Number of pages to search each search engine. Default: 5", default=100)
    parser.add_argument("-t", "--timeout", type=int, help="Specify request timeout. Default: 25", default=25)
    parser.add_argument("-o", "--output",  type=str, help="Directory to write username files to.")
    parser.add_argument("--cookie",        type=str, help="File containing Google CAPTCHA bypass cookies")
    parser.add_argument("--proxy",         type=str, help="Proxy to pass traffic through: <ip:port>")
    parser.add_argument("--lower",         action="store_true", help="Force usernames to all lower case.")
    parser.add_argument("--upper",         action="store_true", help="Force usernames to all upper case.")
    parser.add_argument("--debug",         action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    start  = time.time()
    output = args.output if args.output else "./"

    if args.company:
        scraper = Scraper(args.company, cookies=args.cookie, depth=args.depth, timeout=args.timeout, proxy=args.proxy, keyword=args.keyword, location=args.location)
        scraper.loop.run_until_complete(scraper.run())
        print("\n\n[+] Names Found: %d" % len(scraper.employees))
        print("[*] Writing names to the following directory: %s" % output)
        with open("%s/names.txt" % (output), 'w') as f:
            for name in scraper.employees:
                f.write("%s\n" % name)



    elapsed = time.time() - start
    if args.debug: print("\n[DEBUG] %s executed in %0.4f seconds." % (__file__, elapsed))