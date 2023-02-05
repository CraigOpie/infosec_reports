# InfoSec Reports
Selenium based webscraper capable of scraping React.js and Angular.js web applications

The script will fetch information based on user input to command line arguments.  The output is in JSON object notation.

Headless mode does not work in Linux.

## Initial Run:
1. python -m venv env
2. source env/bin/activate
3. pip install -r requirements.txt

Place chromedriver in PATH if its not already there.


## Examples:
```bash
python src/main.py -s hackerone -d 30 -k api -o popular -t public

```

## Issues
The chromedriver fails to run in headless mode in a Debian based environment.

Please report any functionality issues and bugs if found.  Remember that this is a pre-release software version.  Changes are being made daily to this tool.