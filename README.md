# BridgeKeeper


Scrape employee names from search engine LinkedIn profiles. Convert employee names to a specified username format.

### Examples

Gather employee names for a company, Example, and convert each name into an 'flast' username formatted email:<br>
`$ python3 bridgekeeper.py --company "Example Ltd." --format {f}{last}@example.com --depth 10 --output example-employees/ --debug`

Convert an already generated list of names to usernames:<br>
`$ python3 bridgekeeper.py --file names.txt --format {f}{last}@example.com --output example-employees/ --debug`


Username format examples (BridgeKeeper supports middle names as well as character limited usernames - e.g. only 4 characters of a last name is used):<br>
```
Name: John Adams Smith
{f}{last}                   > jsmith
{f}{m}.{last}               > ja.smith
{f}{last}[4]@example.com    > jsmit@example.com
```

### Features

* Support for three major search engines: Google, Bing, and Yahoo
* Name parsing to strip LinkedIn titles, certs, prefixes, etc.
* Search engine blacklist evasion
* Proxying
* Username formatting with support for trickier username formats
  * Name trimming
    * e.g. If a username format has only the first 4 characters of the last name
  * Hyphenated last name handling
  * Duplicate username handling
    * Incrementing numbers appended to duplicate usernames
