import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import csv
import json
import vulnscanner
from urllib.parse import urljoin, urlparse

config = json.load(open('config.json'))

base_url = config['target']
timeout = config['timeout']
threads = config['threads']
output = config['output']

results = []

# Request handler with error catching
def request(url):
  try:
    res = requests.get(url, timeout=timeout)
  except requests.exceptions.RequestException as e:
    print(f"Error on {url}: {e}")
    return None
  
  return res


# Extract and recursively requests links  
def extract_links(url):
  res = request(url)
  if res is None:
    return

  links = BeautifulSoup(res.text, 'html.parser').find_all('a')

  with ThreadPoolExecutor(max_workers=threads) as executor:
    executor.map(request_link, links)


# Check individual link  
def request_link(link):
  href = link['href']
  href = urljoin(base_url, href)

  check_response(request(href))


# Check response for clues
def check_response(res):
  if res is None:
    return

  print(f"Checking {res.url}")

  check_headers(res)
  check_content(res.text)

  vulnscanner.scan_response(res)

  time.sleep(1)


# Header and content checks  
def check_headers(res):
  if "password" in res.headers:
    print("Header infoleak")

  if "debug" in res.text:
     print("Debug code")


# Check default paths
def check_defaults():
  paths = ['/admin','/config'] 

  for path in paths:
    check_response(request(urljoin(base_url, path)))


# Parameter tester  
def fuzz_params(path):
  payloads = ['1','../','"%20']

  for payload in payloads:
     check_response(request(path + payload))


# Output results
def output_results():
  if output == 'csv':
    with open('results.csv', 'w') as f:
      writer = csv.writer(f)

      for result in results:
         writer.writerow(result)

  elif output == 'json':
    with open('results.json', 'w') as f:
      json.dump(results, f)


# Main driver
def run():
  extract_links(base_url) 
  check_defaults()

  parsed = urlparse(base_url)
  fuzz_params(parsed.path)

  output_results()


if __name__ == '__main__':
  run()
