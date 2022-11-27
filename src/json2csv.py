#!/usr/bin/env python3
# coding: utf-8
"""
__description__ = "Converts a JSON file to a CSV file."
__course__ = "ics691e"
__organization__ = "Information and Computer Sciences Department, University of Hawai'i at Mānoa"
__author__ = "Craig Opie"
__email__ = "opieca@hawaii.edu"
__version__ = "1.0.0"
__created__ = "2022-10-01"
__modified__ = "2022-10-10"
__maintainer__ = "Craig Opie"
"""
from json import loads, dump
from csv import writer
from argparse import ArgumentParser

# Json2Csv class
class Json2Csv:
    """Converts a JSON file to a CSV file."""
    def __init__(self, filename, keyword):
        """Initializes the Json2Csv class."""
        self.filename = str(filename)
        self.keyword = str(keyword)

    def open(self):
        """Opens the JSON file."""
        with open(self.filename, 'r') as infile:
            self.json_data = loads(infile.read())

    def save(self):
        """Saves the CSV file."""
        with open(self.filename.replace('.json', '.csv'), 'w') as outfile:
            self.csv_data = writer(outfile)

            # Find sub headers
            headers_list = []
            keys = self.json_data['data'][0].keys()
            for key in keys:
                if isinstance(self.json_data['data'][0][key], list):
                    sub_columns = self.json_data['data'][0][key][0]
                    if isinstance(sub_columns, dict):
                        for column in sub_columns:
                            headers_list.append(str(column))
                    else:
                        headers_list.append(str(key))
                else:
                    headers_list.append(str(key))
            self.csv_data.writerow(headers_list)

            # Write data
            for record in self.json_data['data']:
                data_list = []
                for key in keys:
                    if isinstance(record[key], list):
                        sub_columns = record[key][0]
                        if isinstance(sub_columns, dict):
                            for column in sub_columns:
                                if sub_columns[column] == '-':
                                    data_list.append('None')
                                else:
                                    data_list.append(str(sub_columns[column]))
                        else:
                            if record[key] == '-':
                                data_list.append('None')
                            else:
                                data_list.append(''.join(record[key]))
                    else:
                        if record[key] == '-':
                            data_list.append('None')
                        else:
                            data_list.append(record[key].replace(',', '').replace('"', ''))
                self.csv_data.writerow(data_list)

    def filter(self):
        """Filters the JSON data."""
        new_json_data = {'data': []}
        for item in self.json_data['data']:
            if self.keyword.lower() in str(item['Links'][0]['Title']).lower():
                new_json_data['data'].append(item)
        self.json_data = new_json_data

if __name__ == "__main__":
    argv = ArgumentParser(usage = "json2csv.py -f [ FILENAME ] -k [ KEYWORD ]")
    argv.add_argument("-f", "--filename", default="data.json", help="Filename to convert <data.json>")
    argv.add_argument("-k", "--keyword", default="", help="Key word to filter for <api>")

    parser = argv.parse_args()
    converter = Json2Csv(parser.filename, parser.keyword)
    converter.open()
    converter.filter()
    converter.save()