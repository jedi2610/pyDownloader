import urllib.parse
import webbrowser
import subprocess
import argparse
import requests
import logging
import sys
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from prettytable import *
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.common.exceptions import InvalidArgumentException, WebDriverException
from selenium.webdriver.chrome.options import Options


def print_banner():
    # Print banner
    print("""
                                                                                                         __                       _______
                                                                                                        /  |                     /       \
                                                                 ______   __    __   ______   ______   _$$ |_     ______         $$$$$$$  |  ______   __    __
                                                                /      \ /  |  /  | /      \ /      \ / $$   |   /      \        $$ |__$$ | /      \ /  |  /  |
                                                                /$$$$$$  |$$ |  $$ |/$$$$$$  |$$$$$$  |$$$$$$/   /$$$$$$  |      $$    $$<  $$$$$$  |$$ |  $$ |
                                                                $$ |  $$ |$$ |  $$ |$$ |  $$/ /    $$ |  $$ | __ $$    $$ |      $$$$$$$  | /    $$ |$$ |  $$ |
                                                                $$ |__$$ |$$ \__$$ |$$ |     /$$$$$$$ |  $$ |/  |$$$$$$$$/       $$ |__$$ |/$$$$$$$ |$$ \__$$ |
                                                                $$    $$/ $$    $$ |$$ |     $$    $$ |  $$  $$/ $$       |      $$    $$/ $$    $$ |$$    $$ |
                                                                $$$$$$$/   $$$$$$$ |$$/       $$$$$$$/    $$$$/   $$$$$$$/       $$$$$$$/   $$$$$$$/  $$$$$$$ |
                                                                $$ |      /  \__$$ |                                                                 /  \__$$ |
                                                                $$ |      $$    $$/                                                                  $$    $$/
                                                                $$/        $$$$$$/                                                                    $$$$$$/
    """)


def initialize_driver(browser, isDebug):

    # Initializing WebDriver
    if not isDebug:
        os.environ['WDM_LOG_LEVEL'] = '0'

    pl = sys.platform
    if isDebug:
        print("System Platform:", pl)

    chromeOptions = Options()
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--disable-extensions')
    chromeOptions.add_argument('--disable-gpu')
    # chromeOptions.add_argument('--disable-dev-shm-usage')
    # incase user runs in a headed mode
    chromeOptions.add_argument('disable-infobars')

    if pl == 'win32':
        # Disable logging
        chromeOptions.add_experimental_option(
            'excludeSwitches', ['enable-logging'])

    elif pl == 'linux' or pl == 'linux2' or pl == 'darwin':
        # https://askubuntu.com/questions/1075103/chromium-config-folder-is-missing-in-ubuntu-18-04
        # https://stackoverflow.com/questions/50761757/selenium-headless-chromedriver-fails-with-connectionreseterror-errno-104-conn
        if browser == "chrome":
            chromeOptions.binary_location = '/usr/bin/google-chrome'
        else:
            # if chromium is installed using snap
            chromeOptions.add_argument("user-data-dir=.config/chromium")
            # Not recommended to run in no-sandbox mode
            # chromeOptions.add_argument('--no-sandbox')

            if "snap" in str(subprocess.check_output(["which", "chromium"])):
                chromeOptions.binary_location = '/snap/bin/chromium'
            else:
                # if chromium is installed using from source or deb package
                chromeOptions.binary_location = '/usr/bin/chromium-browser'

    if browser == "chrome":
        try:
            driver = webdriver.Chrome(
                ChromeDriverManager().install(), options=chromeOptions)
        except WebDriverException:
            print("Chrome app is unresponsive.")
            exit(1)

    else:
        try:
            driver = webdriver.Chrome(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=chromeOptions)
        except WebDriverException:
            print("Chromium app is upresponsive.")
            exit(1)

    return driver


def resize_screen():

    # Resizing and clearing the screen
    pl = sys.platform
    if pl == 'win32':
        os.system("cls")
        os.system("mode 500")
    elif pl == 'linux' or pl == 'linux2' or pl == 'darwin':
        os.system("clear")
        # os.system("resize -s 300 300")
    print_banner()


def findPirateSite(driver, isDebug):
    """
    Finds a functional piratebay site

    @return: returns the URL of the functional piratebay site
    """
    # Finds a functional piratebay site
    if isDebug:
        print('Inside findPirateSite() function')
    try:
        driver.get("https://piratebay-proxylist.net")
        if isDebug:
            print('Scraping data of all working websites for your country')
        pageData = driver.page_source
    except Exception as e:
        print(e)
        driver.quit()
        exit(0)

    # Obtain the URL of the working piratebay site
    soup = BeautifulSoup(pageData, features="lxml")
    countries = soup.select(".country")
    domains = soup.select(".url")
    index = indianDomains = list()
    for country in countries:
        if country.getText().strip() == "IN":
            index = countries.index(country)
            countries[index] = ""
            indianDomains.append(domains[index].getText().strip())

    return indianDomains


def processFinalPage(driver, domain, mediaName, parameters, isDebug):

    # Processing data from the pirate site

    if isDebug:
        print('Inside processFinalPage() function')
    # Encoding the query
    query = urllib.parse.quote_plus(mediaName)
    finalUrl = "https://{0}/search.php?q={1}".format(domain, query)
    for key, value in parameters.items():
        finalUrl += f'&{key}={value}'

    if isDebug:
        print(finalUrl)

    try:
        driver.get(finalUrl)
    except InvalidArgumentException as e:
        print(e)
        driver.quit()
        exit(0)

    soup = BeautifulSoup(driver.page_source, features='lxml')
    totEntries = len(soup.select('.list-entry'))

    # Scraping all kinds of data from the website
    typeOfMedia = soup.select('.item-type')
    nameOfMedia = soup.select('.item-name')
    uploadDate = soup.select('.item-uploaded')
    sizeOfMedia = soup.select('.item-size')
    uploadedBy = soup.select('.item-user')
    seeders = soup.select('.item-seed')
    leechers = soup.select('.item-leech')
    magnetLinks = soup.select('.item-icons > a')

    # Initializing PrettyTable with all the table headers and tweak some settings
    tableHeader = ["S.No", "Category", "Name",
                   "Upload Date", "Size", "ULed by", "SE", "LE"]
    table = PrettyTable(tableHeader)
    table.align = "l"
    table.hrules = ALL
    table.padding_width = 4

    try:
        # Adding all the data to the table
        for i in range(0, totEntries + 1):
            table.add_row([i, typeOfMedia[i].getText(), nameOfMedia[i].getText(), uploadDate[i].getText(
            ), sizeOfMedia[i].getText(), uploadedBy[i].getText(), seeders[i].getText(), leechers[i].getText()])
    except IndexError as e:
        if isDebug:
            print(f'Error while scraping data from {domain}')
        return None

    # Deleting row 1 as it's just the table header scraped from the site
    table.del_row(0)
    print("\n\n")
    print(table)

    # Auto exit if no torrent is found
    if nameOfMedia[1].getText().strip() == 'No results returned':
        print("\n")
        driver.quit()
        exit(0)

    try:
        # Getting user input on which torrent to download
        userInput = int(
            input("\nWhich torrent do you wanna download? (0 to exit) > "))
    except ValueError:
        print('Input type should be integer')
        driver.quit()
        exit(0)

    if 0 <= userInput <= 100:
        if userInput == 0:
            print("Cleaning up...")
            driver.quit()
            print("Exiting")
            exit(0)
        path = nameOfMedia[userInput].a.get('href')
        finalUrl = "https://" + domain + path
    else:
        print('Not a valid option')
        driver.quit()
        exit(0)

    if isDebug:
        print(finalUrl)

    driver.get(finalUrl)
    soup = BeautifulSoup(driver.page_source, features='lxml')
    descriptionText = soup.select('#description_text')
    fileNames = soup.select('.file-name')
    fileSizes = soup.select('.file-size')

    try:
        print('\n----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("\nDescription of the torrent: \n\n",
              descriptionText[0].getText())
    except:
        pass

    try:
        print('\n----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("\nList of files included in the torrent: \n")
        maxLen = max([len(fileName.getText()) for fileName in fileNames])
        for i in range(0, len(fileNames)):
            print(fileNames[i].getText().ljust(
                maxLen, " "), "\t", fileSizes[i].getText())
    except:
        pass

    return magnetLinks[userInput-1].get('href')


def main(args):

    # Driver code
    isDebug = args.debug
    if isDebug:
        print("Searching for:", ''.join(args.query))
        print("Browser Type:", args.browser)
    # Initializing Chrome WebDriver
    driver = initialize_driver(args.browser, isDebug)

    # Clearing and resizing screen
    resize_screen()

    # Scraping data to find all working websites
    domains = findPirateSite(driver, isDebug)

    if isDebug:
        print('List of domains:', ', '.join(domains))
        print('Total working domains:', len(domains))

    mediaName = ' '.join(args.query)
    category = args.category
    types = ["all", "audio", "video", "apps", "games", "other"]
    parameters = {}

    # Updating parameters
    for i in types:
        if i in category:
            parameters.update({i: "on"})

    for domain in domains:
        if isDebug:
            print("Currently checking domain: ", domain)
        magnetLink = processFinalPage(
            driver, domain, mediaName, parameters, isDebug)
        if magnetLink is not None:
            break

    if domain == domains[-1]:
        print("Oops!, couldn't find any working sites for your country.")

    if isDebug:
        print(magnetLink)

    # Opening magnet link
    webbrowser.open(magnetLink)
    driver.quit()


if __name__ == "__main__":

    # TODO:
    # Add support for multiplefiledownloads
    # Add support to view the description of file before downloading

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='+', type=str,
                        metavar='query', help="Name of the media to download")
    parser.add_argument('-c', '--category', default="all", choices=[
                        "all", "audio", "video", "apps", "games", "other"], nargs='*', dest='category', type=str, help="Searches for the given 'name' in the specified category (default = all)")
    parser.add_argument('-d', '--debug', dest='debug',
                        action='store_true', help="Prints debug messages")
    parser.add_argument('-b', '--browser', dest='browser', choices=[
                        "chrome", "chromium"], default="chrome", help='Specifiy the browser to use')
    args = parser.parse_args()

    main(args)
