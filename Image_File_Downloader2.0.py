#!/usr/bin/env python

import logging
import sys
import glob
import time
import pyinputplus
from soup_kitchen import soup_kitchen
import imageio.v3 as iio
import os
import re
import shutil
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s: %(name)s - [%(levelname)s] - %(message)s')

file_handler = logging.FileHandler('Image_Site_Downloader2.0.log', mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
# stream_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
# logger.addHandler(stream_handler)


'''

Modular image_site downloader that works with multiple sites 
CL interface

****search term needs to be in quotes********


'''

logger.debug('Start of Program')


def error_message():

    logger.exception('Error Code: ')
    print('Error encountered: see logs for details.')
    sys.exit()


def digit_extractor(text):

    re_digits = re.compile(r'(\d+),*(\d*),*(\d*)')
    results_digits = re_digits.search(text)
    results_digits = results_digits.group()
    results_digits = results_digits.replace(',', '')
    return int(results_digits)


def searched_vs_results_check(search_count, results_count):

    if results_count < search_count:
        search_count = results_count
        logger.debug('Only %s search results found. Downloading all search results.'
                     % (str(results_count)))

    return search_count


def scroll_for_results():

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((
        By.TAG_NAME, 'img')))
    driver.execute_script('window.scrollBy(0,document.body.scrollHeight)')
    time.sleep(5)
    driver.execute_script('window.scrollBy(0,document.body.scrollHeight)')


def find_image_pages(search_count, results):

    pic_links = []

    for i in range(search_count):
        pic_links.append(results[i].get_attribute('href'))

    return pic_links


def find_file_suffix(file):

    file_type_re = re.compile(r'(\.[a-z]{2,4})$')
    file_type_suffix = file_type_re.search(file)
    file_type_suffix = file_type_suffix.group()
    return file_type_suffix


def click_element(element_XPATH):

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH, element_XPATH)))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
        By.XPATH, element_XPATH)))
    target = driver.find_element(By.XPATH, element_XPATH)

    for i in range(4):
        try:
            target.click()
            break
        except ElementClickInterceptedException:
            logger.debug('Error clicking ' + element_XPATH)
            logger.debug('ElementClickInterceptedException')
            logger.debug('Trying again.')
            time.sleep(5)
            continue

def find_text_of_element(element_XPATH):

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH, element_XPATH)))
    text = driver.find_element(
        By.XPATH, element_XPATH).text
    return text


def find_flickr_download_body(source):

    download_name_re = re.compile(r'\d+_[a-z, 0-9]+')
    download_name = download_name_re.search(source)
    return download_name.group()


def find_file_destination(file_title, suffix):

    file_name = file_title + suffix
    file_destination = search_terms_folder_location + str(image_pages.index(i)) + '-' + file_name
    logger.debug('File destination: ' + file_destination)
    return file_destination


def find_number_of_files(folder):

    list_of_files = glob.glob(folder + '/*')
    number_of_files = len(list_of_files)
    return number_of_files


def find_latest_file_added(folder):

    list_of_files = glob.glob(folder + '/*')
    latest_file = max(list_of_files, key=os.path.getmtime)
    return latest_file


def wait_for_download():

    latest_file = find_latest_file_added('~/Downloads')
    downloading = '.crdownload'

    while downloading in latest_file:
        latest_file = find_latest_file_added('~/Downloads')
        time.sleep(2)
        logger.debug('Downloading file...')


print('Welcome to Image_Downloader.')

# CLI
search_terms = input('Please enter your search query: ')
logger.debug('Search Terms: ' + search_terms)
search_terms_folder = search_terms.replace(' ', '_')
search_terms_folder_location = '~/Pictures/ISD_Storage/' + search_terms_folder + '/'
if os.path.exists(search_terms_folder_location):
    shutil.rmtree(search_terms_folder_location)
# This should check with user - pos. to cont. from prev point
os.makedirs(search_terms_folder_location)
logger.debug('Creating directory for images: ' + search_terms_folder_location)

number_of_pics_to_find = pyinputplus.inputNum(prompt='How many pictures do you want? ', min=1, max=100)
logger.debug('Number of pictures: ' + str(number_of_pics_to_find))

target_site = pyinputplus.inputMenu(['https://imgur.com/', 'https://www.flickr.com/'], prompt='What site would you like to search on?\n', numbered=True)
logger.debug('Target Site: ' + str(target_site))

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

# driver = webdriver.Chrome()
# driver.maximize_window()

print('Accessing website...')

if target_site == 'https://imgur.com/':

    driver.get(target_site + 'search?q=' + search_terms)
    initial_number_of_downloads = find_number_of_files('~/Downloads')

    number_of_results = find_text_of_element("//span[@class='sorting-text-align']//i")

    logger.debug('Number of results: ' + number_of_results)
    results_digits = digit_extractor(number_of_results)

    if results_digits == 0:
        print('An error occurred. See logger.')
        logger.debug('Zero results found.')
        sys.exit()

    number_of_pics_to_find = searched_vs_results_check(number_of_pics_to_find, results_digits)
    scroll_for_results()
    search_results = driver.find_elements(By.XPATH, "//a[@class='image-list-link']")
    image_pages = find_image_pages(number_of_pics_to_find, search_results)

    for i in image_pages:

        logger.debug('Current Link: ' + i)
        driver.get(i)

        title = driver.title
        logger.debug('Downloading ' + title)
        print('Downloading ' + title)


        drop_down_menu = "//div[@class='Dropdown Gallery-OptionsMenu Dropdown--btn Dropdown--postPage']"
        download_option = "//div[@class='Dropdown Dropdown-open Gallery-OptionsMenu Dropdown--btn Dropdown--postPage']//span[text()='Download']"

        click_element(drop_down_menu)
        click_element(download_option)

        wait_for_download()
        download_location = find_latest_file_added('~/Downloads')
        logger.debug('Moving files to search folder...')
        shutil.move(download_location, search_terms_folder_location)
        initial_number_of_downloads += 1


if target_site == 'https://www.flickr.com/':

    driver.get(target_site + 'search?q=' + search_terms + '&view_all=1')

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((
            By.XPATH, "//span[@class='secondary']")))
    except TimeoutException:
        try:
            no_results = driver.find_element(By.CSS_SELECTOR, 'div.no-results-message')
            logger.debug('No results found on website.')
            error_message()
        except NoSuchElementException:
            try:
                single_result = driver.find_element(By.XPATH, '//img')
                logger.debug('Single result found')
                # FUNCTION NOT ERROR MESSAGE
                error_message()
            except NoSuchElementException:
                logger.debug('Unexplained error searching for pictures.')
                error_message()

    number_of_results = find_text_of_element("//span[@class='secondary']")
    results_digits = digit_extractor(number_of_results)
    logger.debug('Total number of results: ' + str(number_of_results))

    number_of_pics_to_find = searched_vs_results_check(number_of_pics_to_find, results_digits)
    scroll_for_results()
    search_results = driver.find_elements(By.XPATH, "//a[@class='overlay']")
    del search_results[:4]
    image_pages = find_image_pages(number_of_pics_to_find, search_results)

    for i in image_pages:

        logger.debug('Current Link: ' + i)
        driver.get(i)
        initial_number_of_downloads = find_number_of_files('~/Downloads')

        title = find_text_of_element("//h1[@class=' meta-field photo-title ']")
        print('Downloading ' + title)
        title = title.replace(' ', '_')

        move_down = driver.find_element(By.TAG_NAME, 'body')
        move_down.send_keys(Keys.ARROW_DOWN)

        # time.sleep(4)
        click_element("//a[@title='Download this photo']")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, "//ul[@class='sizes']")))
        drop_down_options = driver.find_elements(By.XPATH, "//ul[@class='sizes']/li")

        if len(drop_down_options) == 1:
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((
                By.XPATH, "//img[@class='main-photo']")))
            target_image = driver.find_element(By.XPATH, "//img[@class='main-photo']")
            image_source = target_image.get_attribute('src')
            image_source_plus = image_source.replace('_z', '_b')
            file_type_suffix = find_file_suffix(image_source_plus)
            logger.debug('File type determined: ' + file_type_suffix)

            file_location = find_file_destination(title, file_type_suffix)

            logger.debug('Moving file to search folder.')
            buffered_image = iio.imread(image_source_plus)
            time.sleep(1)
            with open(file_location, 'wb') as destination:
                iio.imwrite(destination, buffered_image, extension=file_type_suffix)

        if len(drop_down_options) > 1:
            image_source = driver.find_element(
                By.XPATH, "//li[@class='Original']//a[@class='download-image-size']")
            image_source = image_source.get_attribute('href')

            file_type_suffix = find_file_suffix(image_source)

            download_name = find_flickr_download_body(image_source)
            download_name = download_name + '_o' + file_type_suffix
            download_location = '~/Downloads/' + download_name

            file_location = find_file_destination(title, file_type_suffix)

            click_element("//li[@class='Original']")
            logger.debug('Moving file to search folder.')
            wait_for_download()
            shutil.move(download_location, file_location)

print('Download complete. Files in: ' + search_terms_folder_location)
