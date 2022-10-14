# InfoSec Reports
Selenium based webscraper capable of scraping React.js and Angular.js web
applications

The script will fetch information based on user input to command line 
arguments.  The output is in JSON object notation.

Headless mode does not work in Linux.

## Requirements File Installation:
run: ``` pip install -r requirements.txt ``` in your shell.  
Install [selenium](https://pypi.org/project/selenium/) and [chromedriver](https://chromedriver.chromium.org/downloads)


## Examples:
```bash
python3 src/main.py -s hackerone -d 30 -k api -o popular -t public

```

## Issues
The chromedriver fails to run in headless mode in a Debian based environment.

Please report any functionality issues and bugs if found.  Remember that this
is a pre-release software version.  Changes are being made daily to this tool.