''' The main scraper file or the 
entry point of the program'''

from scraper_helper import Scraper
import constants


def main():
    scraper_obj = Scraper(constants.SCRAPE_URL, constants.FILE_NAME)
    scraped_data = scraper_obj.scrape_url_data()
    scraper_obj.write_data_to_excel(scraped_data)


if __name__ == '__main__':
    main()
