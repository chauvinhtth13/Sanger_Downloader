import argparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, JavascriptException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.switch_to.window("TabDownload")
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var elements = document.querySelector('downloads-manager')
        .shadowRoot.querySelector('#downloadsList')
        .items
        if (elements.every(e => e.state === 'COMPLETE'))
        return elements.map(e => e.filePath || e.file_path || e.fileUrl || e.file_url);
        """)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatic download data on Sanger database by Google Chrome. "
                                                 "Made by Vinh Chau (chauvinhtth13@gmail.com)")
    parser.add_argument("-i", "--input_html", type=str, default="",
                        help="Input file HTML")
    parser.add_argument("-p", "--download_directory", type=str, default="",
                        help="Input file HTML")
    args = parser.parse_args()

    HTMLFile = open(args.input_html, "rb")
    index = HTMLFile.read()

    Soup_code = BeautifulSoup(index, 'lxml')
    chrome_options = Options()
    if args.download_directory != "":
        chrome_options.add_experimental_option("prefs", {'download.default_directory': args.download_directory})
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager(path=r".").install()), options=chrome_options)
    browser.execute_script("window.open('about:blank','TabDownload');")
    num_file = 1
    for i in Soup_code.findAll("a", attrs={"class": "download-link"}):
        print("file ", num_file)
        print(i["href"])
        browser.get(i["href"])
        flag = 0
        time_wait = 600
        while flag == 0:
            try:
                paths = WebDriverWait(browser, time_wait, 1).until(every_downloads_chrome)
                print(paths)
                flag = 1
            except (TimeoutException, JavascriptException):
                flag = 0
                time_wait = time_wait + 600
        num_file = num_file + 1
