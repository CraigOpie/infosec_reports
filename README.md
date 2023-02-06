# InfoSec Reports
Selenium based webscraper capable of scraping React.js and Angular.js web applications

The script will fetch information based on user input to command line arguments.  The output is in JSON object notation.

Software was developed and tested on a fedora 37 environment.

## Initial Run:
1. python -m venv env
2. source env/bin/activate
3. pip install -r requirements.txt

Place chromedriver in PATH if its not already there.


## Examples:
```bash
python src/main.py -s hackerone -d 30 -k api -o popular -t public  -H True
```

## Export DB to CSV
Install sqlite3 for command line use or use your own preferred method:
- `sudo dnf install sqlite3`

```bash
sqlite3 -header -csv h1.db "select * from reports;" > db.csv
```

## Issues
Security Issues:
- There is no input validation for the source, duration, key_word, order, type, filename, and headless parameters passed to the Scraper class. Attackers can use this to inject malicious data and potentially cause harm to the system or the data stored in the database.
- The options object passed to the Chrome web driver is created with the --no-sandbox option which can potentially cause security vulnerabilities.

Vulnerabilities:
- The code does not handle exceptions and errors properly, potentially leading to unexpected behavior and data loss.
- The SQLite database connection is not properly secured, and there is no use of parameterized queries which can lead to SQL injection vulnerabilities.
- The code uses a hardcoded database name 'h1.db' which can cause unintended consequences if the same name is used by other scripts or processes.

Please report any functionality issues and bugs if found.  Remember that this is a pre-release software version.  Changes are being made daily to this tool.