#!/usr/end/python
import os
import sys
import requests
import shutil
import gzip
import argparse
from bs4 import BeautifulSoup as bs
from sqlalchemy import update
from urllib.parse import urlparse

def args():
    parser = argparse.ArgumentParser(description="Find all gz links and download them")
    parser.add_argument("-p", help="Enter a path to save the files to.")
    args = parser.parse_args()
    return args

def get_links(site_url):
    r = requests.get(site_url)
    head = r.headers['content-type']
    content = r.text
    soup = bs(content, 'html.parser')
    link_list = []
    for a in soup.find_all('a', href=True, text=True):
        link_text = a['href']
        if ".gz" in link_text:
            link_list.append(link_text)
    return link_list

def download_files(path,link_list):
    parsed_files = {}
    for url in link_list:
        r = requests.get(url, allow_redirects=True)
        parsed = urlparse(url)
        lpath = parsed.path
        local_file = lpath.strip('/')
        nonzip = local_file.rstrip('.gz')
        open('{}/{}'.format(path,local_file), 'wb').write(r.content)
        parsed_files.update({local_file : nonzip})
    return parsed_files

def unzip_files(path,file_dict):
    for key, value in file_dict.items():
        with gzip.open('{}/{}'.format(path,key), 'rb') as in_file:
            with open('{}/{}'.format(path,value), 'wb') as out_file:
                shutil.copyfileobj(in_file, out_file)
                os.remove('{}/{}'.format(path,key))

if __name__ == "__main__":
    args = args()
    if args.p:
        path = args.p
        path = path.rstrip('/')
    else:
        path = os.getcwd()

    link_list = get_links('https://datasets.imdbws.com')
    file_dict = download_files(path,link_list)
    unzip_files(path,file_dict)
