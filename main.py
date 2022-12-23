import argparse
import requests
import codecs
from bs4 import BeautifulSoup
import os
import re
from sys import platform
from urllib import request
import zipfile
from selenium import webdriver

ZIP_UNIX_SYSTEM = 3


def extract_all_with_permission(zf, target_dir):
  for info in zf.infolist():
    extracted_path = zf.extract(info, target_dir)

    if info.create_system == ZIP_UNIX_SYSTEM:
      unix_attributes = info.external_attr >> 16
      if unix_attributes:
        os.chmod(extracted_path, unix_attributes)


def extract_version_registry(output):
    try:
        google_version = ''
        for letter in output[output.rindex('DisplayVersion    REG_SZ') + 24:]:
            if letter != '\n':
                google_version += letter
            else:
                break
        return(google_version.strip())
    except TypeError:
        return


def extract_version_folder():
    for i in range(2):
        path = 'C:\\Program Files' + \
            (' (x86)' if i else '') + '\\Google\\Chrome\\Application'
        if os.path.isdir(path):
            paths = [f.path for f in os.scandir(path) if f.is_dir()]
            for path in paths:
                filename = os.path.basename(path)
                pattern = '\d+\.\d+\.\d+\.\d+'
                match = re.search(pattern, filename)
                if match and match.group():
                    # Found a Chrome version.
                    return match.group(0)
    return None


def get_chrome_version():
    version = None
    install_path = None
    download_path = None
    link_download = "https://chromedriver.storage.googleapis.com/"

    try:
        if platform == "linux" or platform == "linux2":
            # linux
            install_path = "/usr/bin/google-chrome"
            download_path = "/chromedriver_linux64.zip"
        elif platform == "darwin":
            # OS X
            install_path = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
            download_path = "/chromedriver_mac64.zip"
        elif platform == "win32" or platform == "win64":
            # Windows...
            try:
                # Try registry key.
                stream = os.popen(
                    'reg query "HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome"')
                output = stream.read()
                version = extract_version_registry(output)
            except Exception:
                version = extract_version_folder()
            download_path = "/chromedriver_win64.zip"
    except Exception as ex:
        print(ex)

    version = os.popen(f"{install_path} --version").read().strip(
        'Google Chrome ').strip() if install_path else version

    split_version = version.split(".")

    final_version = ".".join(split_version[0:len(split_version)-1])
    version_download = requests.get(
        "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_" + final_version)

    request.urlretrieve(link_download+version_download.text +
                        download_path, "chromedriver.zip")
    with zipfile.ZipFile("chromedriver_linux64.zip", 'r') as zip_ref:
        extract_all_with_permission(zip_ref, ".")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatic download data on Sanger database by Google Chrome. Made by Vinh Chau ("
                                                 "chauvinhtth13@gmail.com)")
    parser.add_argument("-i", "--input_html", type=str, default="",
                        help="Input file HTML")
    args = parser.parse_args()
    html_file = args.input_html
    f = codecs.open(html_file, 'r', 'utf-8')
    HTMLFile = open(html_file, "r")
    index = HTMLFile.read()
    Soup_code = BeautifulSoup(index, 'lxml')
    try:
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            browser = webdriver.Chrome('./chromedriver')
        elif platform == "win32":
            browser = webdriver.Chrome('./chromedriver.exe')
    except Exception:
        print("Can not detect platform OS. (script support Mac,Linux,Window")
    finally:    
        for i in Soup_code.findAll("a", attrs={"class": "download-link"}):
            print(i["href"])
            browser.get(i["href"])
