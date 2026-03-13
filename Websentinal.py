import requests
from bs4 import BeautifulSoup
import lxml
from urllib.parse import urljoin, urldefrag
from collections import deque

url=input("Target: ")

headers={
    "User-Agent": "Mozilla/5.0"
}

def extract_links(soup, base_url):
    links=[]

    for link in soup.find_all(["a", "link"], href=True):
        new_url=urljoin(base_url, link["href"])
        clean_url=urldefrag(new_url).url
        links.append(clean_url)

    return links

def extract_images(soup, base_url):
    images=[]
    
    for image in soup.find_all("img", src=True):
        img_url=urljoin(base_url, image["src"])
        images.append(img_url)

    return images
    

def static_crawl(start_url):
    visited=set()
    queue=deque()
    queue.append((start_url,0))

    max_depth=2

    while queue:
        current_url,depth=queue.popleft()

        if current_url in visited or depth>max_depth:
            continue

        visited.add(current_url)
        print(current_url)

        try:
            r=requests.get(current_url, headers=headers, timeout=10)
            if not r.ok:
                print("Request failed.", r.status_code)
                continue

            soup=BeautifulSoup(r.text,"lxml")

            print("\nLinks")
            links=extract_links(soup, current_url)
            for link in links:
                if link not in visited:
                    queue.append((link, depth+1))
                
            print("\nImages")
            images=extract_images(soup, current_url)
            for image in images:
                print(image)

        except:
            pass

static_crawl(url)