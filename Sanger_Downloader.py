import argparse
import codecs
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatic download data on Sanger database by Google Chrome. "
                                                 "Made by Vinh Chau (chauvinhtth13@gmail.com)")
    parser.add_argument("-i", "--input_html", type=str, default="",
                        help="Input file HTML")
    parser.add_argument("-p", "--download_directory", type=str, default="",
                        help="Input file HTML")
    args = parser.parse_args()
    html_file = args.input_html

    f = codecs.open(html_file, 'r', 'utf-8')
    HTMLFile = open(html_file, "r")
    index = HTMLFile.read()

    Soup_code = BeautifulSoup(index, 'lxml')
    chrome_options = Options()
    if args.download_directory != "":
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": args.download_directory,
        })
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')

    browser = webdriver.Chrome(service=Service(ChromeDriverManager(path=r".").install()))

    for i in Soup_code.findAll("a", attrs={"class": "download-link"}):
        print(i["href"])
        browser.get(i["href"])
