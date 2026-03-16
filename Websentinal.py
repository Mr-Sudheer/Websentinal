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
    links=set()

    for link in soup.find_all(["a"], href=True):
        new_url=urljoin(base_url, link["href"])
        clean_url=urldefrag(new_url).url
        links.add(clean_url)

    return links

def extract_resources(soup, base_url):
    resources=set()

    for resource in soup.find_all("link", href=True):
        rsc=urljoin(base_url, resource["href"])
        resources.add(rsc)
    
    return resources

def extract_images(soup, base_url):
    images=set()
    
    for image in soup.find_all("img", src=True):
        img_url=urljoin(base_url, image["src"])
        images.add(img_url)

    return images

def extract_script(soup, base_url):
    scripts=set()

    for jscript in soup.find_all("script", src=True):
        js_url=urljoin(base_url, jscript["src"])
        scripts.add(js_url)
    
    return scripts

def extract_inputs(soup):
    inputs=set()

    for form in soup.find_all("input", type=True):
        fname=form.get("name")
        ftype=form.get("type")
        inputs.add((fname, ftype))
    return inputs

def static_crawl(start_url):
    visited=set()
    queue=deque()
    queue.append((start_url,0))

    all_links=set()
    all_rsc=set()
    all_images=set()
    all_scripts=set()
    all_inputs=set()

    max_depth=5

    while queue:
        current_url,depth=queue.popleft()

        if current_url in visited or depth>max_depth:
            continue

        visited.add(current_url)

        try:
            r=requests.get(current_url, headers=headers, timeout=10)
            if not r.ok:
                print("Request failed.", r.status_code)
                continue

            soup=BeautifulSoup(r.text,"lxml")

            links=extract_links(soup, current_url) #Links

            for link in links:
                all_links.add(link)
                if link not in visited and link not in all_links:
                    queue.append((link, depth+1))

            resources=extract_resources(soup, current_url) #Resources

            for resource in resources:
                all_rsc.add(resource)

            images=extract_images(soup, current_url) #Images
                 
            for image in images:
                all_images.add(image)

            script=extract_script(soup, current_url) #Script

            for jscrpt in script:
                all_scripts.add(jscrpt)

            inputs=extract_inputs(soup) #inputs

            for inp in inputs:
                all_inputs.add(inp)

        except Exception as e:
            print("Error: ", e)

    print("\nLinks")
    for lnk in all_links:
        print(lnk)

    print("\nResources")
    for rsc in all_rsc:
        print(rsc)

    print("\nImages")
    for img in all_images:
        print(img)

    print("\nScripts")
    for scrpt in all_scripts:
        print(scrpt)

    print("\nInputs")
    for inpt in all_inputs:
        print(inpt)
    print("\n")

    print("Total links: ", len(all_links))
    print("Total images: ", len(all_images))
    print("Total resources: ", len(all_rsc))
    print("Total scripts: ", len(all_scripts))
    print("Total inputs: ", len(all_inputs))


static_crawl(url)