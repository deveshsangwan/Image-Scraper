import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver.common.keys import Keys
from urllib.request import *
import time

count = 1
chrome_driver_path = "msedgedriver.exe"
browser_path = "C:\\Program Files (x86)\\Microsoft\\Edge Beta\\Application\\msedge.exe" 
option = EdgeOptions()
option.use_chromium = True  
option.binary_location = browser_path   
driver = Edge(executable_path = chrome_driver_path, options = option)

def is_valid(url):
    '''
    Checks whether `url` is a valid URL.
    '''
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_images(url):
    '''
    Returns all image URLs on a single `url`
    '''
    html = driver.page_source.split('"')
    urls = []
    for i in html:
        if (i.startswith('http') or i.startswith('//')) and 'jpg' in i.split('.')[-1]:    # starting with http or // and ending with jpg (as a part)
            if i.startswith('http'):
                urls.append(i.split('"')[0])
            else:
                urls.append('http:'+i.split('"')[0])
    print(urls)
    print ("Total images after removing duplicates: {}\n".format(len(urls)))
    urls_new = [] 
    [urls_new.append(x) for x in urls  if x not in urls_new]  
    print ("Total images after removing duplicates: {}\n".format(len(urls_new)))
    return urls_new


def download(url, pathname):
    global count
    '''
    Downloads a file given an URL and puts it in the folder `pathname`
    '''
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, str(count)+".jpg")

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))
    count += 1


def main(url, path):
    # get all images
    driver.get(url)
    time.sleep(10)
    for __ in range(10):
        driver.execute_script("window.scrollBy(0, 1000000)")
        time.sleep(5.2)
    imgs = get_all_images(url)
    for img in imgs:
        # for each img, download it
        download(img, path)
    


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="This script downloads all images from a web page")
    parser.add_argument("url", help="The URL of the web page you want to download images")
    parser.add_argument("-p", "--path", help="The Directory you want to store your images, default is the domain of URL passed")
    
    args = parser.parse_args()
    url = args.url
    path = args.path
    if not path:
        # if path isn't specified, use the domain name of that url as the folder name
        path = urlparse(url).netloc
    
    main(url, path)

