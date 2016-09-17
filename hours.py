"""A very simple CLI app for managing one's hours."""

import json
import argparse
import os.path
import logging
import re
import datetime
import sys
from collections import defaultdict, OrderedDict

logging.basicConfig(level=logging.INFO)

def rec_ord_dict(recdict):
    """Recursive sorting awesomeness!

    Args:
        recdict(dict): A dictionary to recursively sort.
    """
    newdict = OrderedDict()
    for k, v in sorted(recdict.items()):
        if isinstance(v, dict):
            newdict[k] = rec_ord_dict(v)
        else:
            newdict[k] = v
    return newdict

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pos', nargs='?')
    parser.add_argument('-c', '--company', help='the company', default='Example')
    parser.add_argument('-d', '--date', help='the date in a yyyy/mm/dd format', default=datetime.date.today().strftime('%Y/%m/%d'))
    parser.add_argument('-n', '--num_hours', help='the hours', type=int, default=2)
    parser.add_argument('-r', '--report', help='the detailed report', type=str, default='N/A')
    args = parser.parse_args()

    company = args.company
    date_str = args.date
    num_hours = args.num_hours
    report = args.report

    file_name = 'hours.json'

    if not os.path.isfile(file_name):
        json_file = open(file_name, 'w')
        json_file.write('{}')
        json_text = '{}'
        json_file.close()
    else:
        json_file = open(file_name)
        json_text = json_file.read() or '{}'
        json_file.close()

    # Load the json text from file into a dict
    hours_dict = json.loads(json_text)

    # Create a new defaultdict and update it with the pre-existing hours
    new_hours = defaultdict(lambda: defaultdict(dict))
    new_hours.update(hours_dict)

    if args.pos == 'single':
        try:
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d').date()
        except Exception:
            logging.warning('Supplied date does not match... Must match yyyy/mm/dd')
            raise

        new_hours[company][date.strftime('%b %d, %Y')]['h'] = num_hours
        new_hours[company][date.strftime('%b %d, %Y')]['r'] = report
    elif args.pos == 'view':
        logging.info('Viewing the total hours for the json data...')
        print()
        new_hours = rec_ord_dict(new_hours)
        for company, dates in new_hours.items():
            print('%s:' % company)
            for date_str, data in dates.items():
                print('  %s:  %.1f hours' % (date_str, data['h']))
                print('    Report: %s' % data['r'])
        print()
    else:
        try:
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d').date()
        except Exception:
            logging.warning('Supplied date does not match... Must match yyyy/mm/dd')
            raise

        # Monday...
        date = date - datetime.timedelta(days=date.weekday())

        num_hours = float(num_hours) / 5.0

        for x in range(0, 5):
            new_hours[company][date.strftime('%b %d, %Y')]['h'] = num_hours
            new_hours[company][date.strftime('%b %d, %Y')]['r'] = report
            date = date + datetime.timedelta(days=1)

    if args.pos != 'view':
        logging.info('Saving the hours data back to the json file...')
        json_file = open(file_name, 'w')
        json_text = json.dumps(new_hours, sort_keys=True)
        json_file.write(json_text)
        json_file.close()

    logging.info('Exiting...')
