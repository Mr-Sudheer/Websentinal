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

def extract_forms(soup, base_url):
    forms = []

    for form in soup.find_all("form"):
        action = form.get("action")
        method = form.get("method", "get").lower()

        full_action = urljoin(base_url, action)

        inputs = []
        for inp in form.find_all(["input", "textarea", "select"]):
            inputs.append({
                "name": inp.get("name"),
                "type": inp.get("type", "text"),
                "value": inp.get("value", "")
            })

        forms.append({
            "action": full_action,
            "method": method,
            "inputs": inputs
        })

    return forms

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
            if request.resource_type in ["xhr", "fetch"]:
                dynamic_endpoints.add(request.url)

        def handle_response(response):
            try:
                if "application/json" in response.headers.get("content-type", ""):
                    dynamic_endpoints.add(response.url)
            except Exception as e:
                pass

        page.on("request", handle_request)
        page.on("response", handle_response)

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=10000)
            page.wait_for_timeout(3000)
            buttons=page.query_selector_all("button")

            for btn in buttons[:3]:
                try:
                    text=btn.inner_text().lower()

                    for x in ["login", "submit", "search"]:
                        if x in text:
                            if btn.is_visible() and btn.is_enabled():
                                btn.click()
                                page.wait_for_timeout(1000)
                            break
                except Exception as e:
                    continue

        except Exception as e:
            print("Dynamic scan error", e)

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
    headers={"User-Agent": "Mozilla/5.0"}
    start_netloc = urlparse(start_url).netloc

    blocked_ext = (".jpg", ".png", ".css", ".pdf", ".zip", ".svg")

    all_links=set()
    all_rsc=set()
    all_scripts=set()
    all_inputs=set()
    all_params={}
    all_forms= []

    max_depth=1

    while queue:
        current_url,depth=queue.popleft()
        current_url=current_url.split("#")[0]
        parsed=urlparse(current_url)

        if (
        current_url in visited
        or depth > max_depth
        or parsed.netloc != start_netloc
        or current_url.endswith(blocked_ext)
        ):
            queue.append((link, depth+1))

        visited.add(current_url)



        try:
            r=requests.get(current_url, headers=headers, timeout=5)

            if not r.ok:
                print("Request failed.", r.status_code)
                continue

            soup=BeautifulSoup(r.text,"lxml")

            links=extract_links(soup, current_url) #Links

            for link in links:
                link=link.split("#")[0]
                parsed_link=urlparse(link)
                all_links.add(link)
                if(parsed_link.netloc == start_netloc
                   and link not in visited
                   and not link.endswith(blocked_ext)):
                    queue.append((link, depth+1))

            resources=extract_resources(soup, current_url) #Resources

            for resource in resources:
                all_rsc.add(resource)

            script=extract_script(soup, current_url) #Script

            for jscrpt in script:
                all_scripts.add(jscrpt)

            inputs=extract_inputs(soup) #inputs

            for inp in inputs:
                all_inputs.add(inp)

            forms=extract_forms(soup, current_url) # forms
            all_forms.extend(forms)

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

    print("\nScripts")
    for scrpt in all_scripts:
        print(scrpt)

    print("\nInputs")
    for inpt in all_inputs:
        print(inpt)

    print("\nForms")
    for form in all_forms:
        print(form)

    print("\nParameters")
    for key, values in all_params.items():
        print(f"{key}: {list(values)}")
    print("\n")

    print("Total links: ", len(all_links))
    print("Total resources: ", len(all_rsc))
    print("Total scripts: ", len(all_scripts))
    print("Total inputs: ", len(all_inputs))
    print("Total forms: ", len(all_forms))
    print("Total parameters: ", len(all_params))

    return all_scripts, all_links


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

start_crawl=time.time()
scripts, links = crawl(url)
end_crawl=time.time()
print("Time taken: ", end_crawl - start_crawl, "seconds")

run_endpoint = False
if requires_js(url):
    print("\nJS-heavy site detected → endpoint extraction will be slow")
    q1 = input("Continue endpoint extraction? (Y/N): ")
    if q1.lower() == "y":
        run_endpoint = True
else:
    run_endpoint = True

if run_endpoint:
    start_endpoint=time.time()
    endpoints(url, scripts, links)
    end_endpoint=time.time()
    print("Time taken: ", end_endpoint - start_endpoint, "seconds")
    