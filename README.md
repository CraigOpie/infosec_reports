# Hackerone Scraper
Selenium based webscraper capable of scraping React.js and Angular.js web
applications

The script will fetch information based on user input to command line
arguments.  The output is in JSON object notation.

Headless mode does not work in Linux.

## Requirements File Installation:
run: ```bash pip install -r requirements.txt ``` in your shell.


## Examples:
```bash
python3 src/main.py -s hackerone -d 30 -k api -o popular -t public

```

## Issues
The chromedriver fails to run in headless mode in Debian environment.

Please report any functionality issues and bugs if found.  Remember that this
is a pre-release software version.  Changes are being made daily to this tool.