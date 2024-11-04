from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import os
import time
import re

path_test = "https://www.potomitan.info/kebek/mois_creole_2024.mp4"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

page_to_scrape = requests.get(path_test, headers=headers)

print(page_to_scrape.headers)