import urllib.parse
import webbrowser
import argparse
import requests
import logging
import sys
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from prettytable import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.chrome.options import Options

os.environ['WDM_LOG_LEVEL'] = '20'


def findPirateSite():
    """
    Finds a functional piratebay site

    @return: returns the URL of the functional piratebay site
    """
    try:
        siteList = requests.get("https://piratebay-proxylist.net")
        siteList.raise_for_status()
    except Exception as e:
        print(e ,)
        exit(0)

    # Obtain the URL of the working piratebay site
    soup = BeautifulSoup(siteList.text, features="lxml")
    countries = soup.select(".country")
    domains = soup.select(".domain")
    for country in countries:
        if country.getText().strip() == "IN":
            index = countries.index(country)
            domain = domains[index].getText()
            break

    return domain


def main(args):

    os.environ['WDM_LOG_LEVEL'] = '30'
    chromeOptions = Options()
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--disable-extensions')
    chromeOptions.add_argument('--disable-gpu')
    chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
    # driver = webdriver.Chrome("C:\\Program Files (x86)\\chromedriver.exe", options=chromeOptions)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)
    # Finds a functional piratebay site
    domain = findPirateSite()

    # os.system("mode 500")  # changing size of cmd

    # 
    mediaName = ' '.join(args.query)
    category = args.category

    types = ["all", "audio", "video", "apps", "games", "other"]
    parameters = {}

    # URL encoding and finding the URL of the final page
    for i in types:
        if i in category:
            parameters.update({i: "on"})

    
    query = urllib.parse.quote_plus(mediaName)
    finalUrl = "https://{0}/search.php?q={1}".format(domain, query)
    for key, value in parameters.items():
        finalUrl += f'&{key}={value}'

    try:
        driver.get(finalUrl)
    except InvalidArgumentException as e:
        print(e)
        driver.quit()
        exit(0)

    soup = BeautifulSoup(driver.page_source, features='lxml')
    totEntries = len(soup.select('.list-entry'))

    typeOfMedia = soup.select('.item-type')
    nameOfMedia = soup.select('.item-name')
    uploadDate = soup.select('.item-uploaded')
    sizeOfMedia = soup.select('.item-size')
    uploadedBy = soup.select('.item-user')
    seeders = soup.select('.item-seed')
    leechers = soup.select('.item-leech')
    magnetLinks = soup.select('.item-icons > a')

    tableHeader = ["S.No", "Category", "Name",
                   "Upload Date", "Size", "ULed by", "SE", "LE"]
    table = PrettyTable(tableHeader)
    table.align = "l"
    table.hrules = ALL
    table.padding_width = 4

    for i in range(0, totEntries+1):
        table.add_row([i, typeOfMedia[i].getText(), nameOfMedia[i].getText(), uploadDate[i].getText(),
                    sizeOfMedia[i].getText(), uploadedBy[i].getText(), seeders[i].getText(), leechers[i].getText()])

    table.del_row(0)
    print(table)

    userInput = int(input("\nWhich torrent do you wanna download? (0 to exit)> "))
    if 0 < userInput <= 100:
        path = nameOfMedia[userInput].a.get('href')
        finalUrl = "https://" + domain + path
    else:
        exit(0)

    driver.get(finalUrl)
    soup = BeautifulSoup(driver.page_source, features='lxml')
    descriptionText = soup.select('#description_text')
    fileNames = soup.select('.file-name')
    fileSizes = soup.select('.file-size')

    try:
        print('\n----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("\n", "Description of the torrent: \n\n", descriptionText[0].getText())
    except:
        pass

    try:
        print('\n----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("\nList of files included in the torrent: \n")
        maxLen = max([len(fileName.getText()) for fileName in fileNames])
        for i in range(0, len(fileNames)):
            print(fileNames[i].getText().ljust(maxLen, " "), "\t", fileSizes[i].getText())
    except:
        pass
    
    driver.quit()
    
    # webbrowser.open(magnetLinks[userInput-1].get('href'))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='+', type=str, metavar='query',
                        help="Name of the media to download")
    parser.add_argument('-c', '--category', default="all", choices=[
                        "all", "audio", "video", "apps", "games", "other"], nargs='*', dest='category', type=str, help="Searches for the given 'name' in the specified category (default = all)")
    args = parser.parse_args()

    main(args)
