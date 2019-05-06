'''All the required helper functions
to scrape and store data in excel'''

import sys
import requests
import urllib
import pandas as pd
from bs4 import BeautifulSoup

# for utf8 encoding
reload(sys)
sys.setdefaultencoding('utf8')


class Scraper:

    def __init__(self, url, filepath):
        self.scrape_url = url
        self.base_url = "http://" + url.split("/")[2]
        self.file_path = filepath

    def _filter_scraped_data(self, data):
        filtered_url = []
        scraped_data = data.findAll('li', 'flex-item')
        for data in scraped_data:
            data_details = {}
            data_url = data.find('a', href=True)['href']
            image_url = data.find('img')['src']
            if 'http' not in data_url:
                data_details['data_url'] = "{}{}".format(self.base_url, data_url)
                data_details['image_url'] = "{}{}".format(self.base_url, image_url)
                filtered_url.append(data_details)
        return filtered_url

    def _scrape_page_data(self, pages_url):
        requested_data = []
        for page in pages_url:
            data = {}
            response = requests.get(page['data_url'])
            bs_scrape_data = BeautifulSoup(response.text, 'html.parser')
            
            try:
                data['Disease name'] = bs_scrape_data.find('h1').text.strip().split('(')[0]
            except Exception as e:
                print "Error getting disease name for url {}. Error: {}".format(page['data_url'], e)
                data['Disease name'] = None
            data['Image link'] = page['image_url']
            
            try:
                data['Origin'] = \
                bs_scrape_data.find_all('div', 'pest-header-content', 'strong')[0].text.split('Origin:')[1].split(
                    'Distribution:')[0]
            except Exception as e:
                print "Error getting origin for url {}. Error: {}".format(page['data_url'], e)
                data['Origin'] = None
            
            try:
                data['Pest'] = None if len(bs_scrape_data.find('h1').text.strip().split('(')) < 2 else \
                bs_scrape_data.find('h1').text.strip().split('(')[1].replace('(', '').replace(')', '')
            except Exception as e:
                print "Error getting pest name for url {}. Error: {}".format(page['data_url'], e)
                data['Pest'] = None
            
            try:
                data['Australia Check'] = 'Yes' if 'australia' in \
                                                   bs_scrape_data.find_all('div', 'pest-header-content', 'strong')[
                                                       0].text.split('Distribution:')[1].split('Features:')[
                                                       0].lower() else 'No'
            except Exception as e:
                print "Error getting Australia check for url {}. Error: {}".format(page['data_url'], e)
                data['Australia Check'] = None
            
            try:
                data['Suspect Specimens'] = ""
                for p in bs_scrape_data.find_all('div', 'hide')[2].find_all('p'):
                    data['Suspect Specimens'] += p.text
            except Exception as e:
                print "Error getting disease name for url {}. Error: {}".format(page['data_url'], e)
                data['Suspect Specimens'] = None
            
            requested_data.append(data)
        return requested_data

    def _convert_url_to_image(self, writer_obj, data):
        worksheet = writer_obj.sheets['Sheet1']
        cell_number = 2
        for d in data:
            worksheet.insert_image('I{}'.format(cell_number), urllib.urlretrieve(d['Image link'])[0])
            cell_number += 1

    def scrape_url_data(self):
        page_response = requests.get(self.scrape_url)
        scrape_page = BeautifulSoup(page_response.text, 'html.parser')
        required_pages_url = self._filter_scraped_data(scrape_page)
        required_data = self._scrape_page_data(required_pages_url)
        return required_data

    def write_data_to_excel(self, scraped_data):
        df = pd.DataFrame(scraped_data)
        writer = pd.ExcelWriter(self.file_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        self._convert_url_to_image(writer, scraped_data)
        writer.save()
