import requests
from bs4 import BeautifulSoup
import lxml
from urllib.parse import urlparse, parse_qs, urljoin
from collections import deque

url=input("Target: ")

headers={
    "User-Agent": "Mozilla/5.0"
}

def crawl(url):
    visited=set()
    queue=deque()
    queue.append((url,0))

    max_depth=2

    while queue:
        url,depth=queue.popleft()

        if url in visited or depth>max_depth or "#" in url:
            continue

        visited.add(url)
        print(url)

        try:
            r=requests.get(url, headers=headers, timeout=5)
            if not r.ok:
                print("Request failed.", r.status_code)
                exit()

            soup=BeautifulSoup(r.text,"lxml")

            for link in soup.find_all(["a", "link"],href=True):
                new_url=urljoin(url,link["href"])
                queue.append((new_url,depth+1))

        except:
            pass

crawl(url)