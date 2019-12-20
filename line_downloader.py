import json
import os
import requests
import argparse
import sys
import time

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PIL import Image

### Progress bar from StackOverflow https://stackoverflow.com/a/34482761
def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()        
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()


parser = argparse.ArgumentParser(description='A simple tool to download stickers from Line')
parser.add_argument("--url", required=True, type=str, help='The sticker pack URL')

args = parser.parse_args()

url = args.url
print("Target URL:", url)

images = []

# Getting the webpage, creating a Response object
response = requests.get(url)
 
# Extracting the source code of the page
data = response.text
 
# Passing the source code to BeautifulSoup to create a BeautifulSoup object for it
soup = BeautifulSoup(data, 'lxml')

title = soup.title.string.replace(' – LINE stickers | LINE STORE', '')
print('Found pack:', title)
 
# Extracting all the <li> tags into a list
tags = soup.find_all('li')

# Extracting URLs from the json inside the data-preview attribute
for tag in tags:
    if tag.has_attr('data-preview'):
        attr_data_preview = tag['data-preview']
        json_attr = json.loads(attr_data_preview)
        image_url = json_attr['staticUrl'].replace(';compress=true', '')

        images.append(image_url)

# Print results
if len(images) == 0:
    print('Unable to download the stickers, please check the URL in the browser or try with a VPN')
    sys.exit()
else:
    print(len(images), 'images found')

# Create the destination folder and print it
dest_dir = os.path.join(os.getcwd(), title)
os.makedirs(dest_dir, exist_ok=True)
print('Saving the images inside directory', dest_dir)

# Download the images
c = 1
for img_url in progressbar(images, prefix='Downloading: ', size=40):
    img = Image.open(requests.get(img_url, stream = True).raw)
    file_name = os.path.join(dest_dir, str(c) + '.png')
    img.save(file_name, format='png')
    c += 1
