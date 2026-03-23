import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urldefrag, urlparse, parse_qs
from collections import deque
import time, random
from playwright.sync_api import sync_playwright

url=input("Target: ").strip()

def requires_js(base_url):
    try:
        r= requests.get(base_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if not r.ok:
            print("Request failed.", r.status_code)
            return False

        soup=BeautifulSoup(r.text,"lxml")

        raw_text = soup.get_text(strip=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(base_url, timeout=15000)

            page.wait_for_timeout(3000)

            rendered_html = page.content()
            browser.close()
        
        rendered_page = BeautifulSoup(rendered_html, "lxml")
        rendered_text = rendered_page.get_text(strip=True)

        if len(rendered_text) > len(raw_text)*2:
            return True
        
        return False
        
    except Exception as e:
        return False
    
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

def extract_parameters(base_url):
    parsed=urlparse(base_url)
    params=parse_qs(parsed.query)

    return params

endpoint_patterns = [
    re.compile(r'["\'](\/api\/[^"\']+)["\']'),
    re.compile(r'["\'](\/v[0-9]+\/[^"\']+)["\']'),
    re.compile(r'https?:\/\/[^\s"\']+\/api\/[^\s"\']+')
]

def static_endpoints(js_files):
    endpoints = set()

    for js in js_files:
        try:
            r = requests.get(js, timeout=5)
            content = r.text

            for pattern in endpoint_patterns:
                matches = pattern.findall(content)
                for m in matches:
                    endpoints.add(m)

        except:
            continue

    return endpoints

def dynamic_endpoints(url):
    dynamic_endpoints = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def handle_request(request):
            for x in ["api", "graphql", "ajax"]:
                if x in request.url:
                    dynamic_endpoints.add(request.url)
                    break

        page.on("request", handle_request)

        page.goto(url, timeout=60000)

        for _ in range(5):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1000)

        buttons = page.query_selector_all("button")
        for btn in buttons:
            try:
                btn.click(timeout=2000)
                page.wait_for_timeout(1000)
            except:
                continue

        links = page.query_selector_all("a")
        for link in links[:10]:
            try:
                link.click(timeout=2000)
                page.wait_for_timeout(1000)
                page.go_back()
            except:
                continue

        inputs = page.query_selector_all("input")
        for inp in inputs:
            try:
                inp.fill("test")
                page.wait_for_timeout(1000)
            except:
                continue

        browser.close()

    return dynamic_endpoints

def hidden_endpoints(base_url):
    wordlist = ["api", "admin", "internal", "debug", "v1", "v2", "private"]
    found = set()

    for word in wordlist:
        test_url = urljoin(base_url, f"/{word}")

        try:
            r = requests.get(test_url, timeout=5)

            if r.status_code in [200, 401, 403]:
                found.add(test_url)

        except:
            continue

    return found

def contextual_endpoints(all_links):
    contextual = set()

    for link in all_links:
        parsed = urlparse(link)

        if parsed.query:
            contextual.add(link)

    return contextual

def crawl(start_url):
    print("\n -> CRAWLER")
    visited=set()
    queue=deque()
    queue.append((start_url,0))

    all_links=set()
    all_rsc=set()
    all_images=set()
    all_scripts=set()
    all_inputs=set()
    all_params={}

    max_depth=2

    while queue:
        current_url,depth=queue.popleft()

        headers={"User-Agent": "Mozilla/5.0"}
        if current_url in visited or depth>max_depth:
            continue

        visited.add(current_url)

        try:
            r=requests.get(current_url, headers=headers, timeout=5)

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

            params=extract_parameters(current_url) # parameters

            for key, value in params.items():
                if key not in all_params:
                    all_params[key]=set()
                
                for v in value:
                    all_params[key].add(v)

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

    print("\nParameters")
    for key, values in all_params.items():
        print(f"{key}: {list(values)}")
    print("\n")

    print("Total links: ", len(all_links))
    print("Total images: ", len(all_images))
    print("Total resources: ", len(all_rsc))
    print("Total scripts: ", len(all_scripts))
    print("Total inputs: ", len(all_inputs))
    print("Total parameters: ", len(all_params))

    return all_links, all_scripts


def endpoints(start_url, all_scripts, all_links):
    print("\n -> ENDPOINT EXTRACTION")

    static_eps = static_endpoints(all_scripts) # static js parsing

    dynamic_eps = dynamic_endpoints(start_url) # dynamic (runtime) 

    hidden_eps = hidden_endpoints(start_url) # Hidden(fuzzing)

    contextual_eps = contextual_endpoints(all_links) # Contextual

    print("\nStatic Endpoints")
    for e in static_eps:
        print(e)

    print("\nDynamic Endpoints")
    for e in dynamic_eps:
        print(e)

    print("\nHidden Endpoints")
    for e in hidden_eps:
        print(e)

    print("\nContextual Endpoints")
    for e in contextual_eps:
        print(e)

    print("\nTotal Static endpoints:", len(static_eps))
    print("Total Dynamic endpoints:", len(dynamic_eps))
    print("Total Hidden endpoints:", len(hidden_eps))
    print("Total Contextual endpoints:", len(contextual_eps))

if requires_js(url):
    print("This website REQUIRES JavaScript.")
    scripts, links = crawl(url)
else:
    print("This website does NOT require JavaScript.")
    scripts, links = crawl(url)

endpoints(url, scripts, links)