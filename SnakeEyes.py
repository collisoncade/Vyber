from bs4 import BeautifulSoup
from datetime import datetime, date
import requests
import json
import os

class SnakeEyes:
    def __init__(self):
        ...

    def get_week_by_date(self):
        with open('Vyber/static/schedule_reference.json', 'r') as file:
            data = json.load(file)
            date_ranges = data.get('date_ranges', {})
            for week, week_dates in date_ranges.items():
                start_date = date(
                   week_dates['start_year'],
                   week_dates['start_month'],
                   week_dates['start_day']
                )
                end_date = date(
                    week_dates['end_year'],
                    week_dates['end_month'],
                    week_dates['end_day']
                )
                today = date.today()
                if today >= start_date and today < end_date:
                    return week

def main():
    print(os.getcwd())
    jim = SnakeEyes()
    jim.get_week_by_date()

if __name__ == "__main__":
    main()