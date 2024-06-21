import os
from io import BytesIO

import requests
import csv
import json
import re
from tqdm import tqdm
import logging
from PIL import Image
from reproject_360_img import panorama_to_plane
import argparse

# Constants
PANORAMAX_API = 'https://panoramax.ign.fr/api/'
OUTPUT_FOLDER = './images'
SEARCH_URI = 'search?place_distance=2-10&place_position='
OVERWRITE = True

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


# ----------------------------- Arguments -----------------------------
parser = argparse.ArgumentParser(description='Download images from panoramax.ign.fr')
parser.add_argument('--test', action='store_true', help='Test mode: only test the image precised with \'--test_url\' '
                                                        'arg')
parser.add_argument('--test_url', type=str, help='URL of the image to test')
parser.add_argument('--test_yaw', type=int, help='Yaw of the image to test')
parser.add_argument('--test_pitch', type=int, help='Pitch of the image to test')

args = parser.parse_args()
if args.test and (args.test_url is None or args.test_yaw is None or args.test_pitch is None):
    parser.error('--test requires --test_url, --test_yaw and --test_pitch')

test_mode = args.test
print(args.test_url, args.test_yaw, args.test_pitch)

# ----------------------------- Functions -----------------------------

def download_image(url, yaw=180, pitch=90, download=True):
    output_name = "REPROJECTED_"

    # If url is a direct link to an image
    if re.match(r'^.*\.jpg$', url):
        output_name += url.split('/')[-1]
        file_name = f'{OUTPUT_FOLDER}/{output_name}.jpg'

        if os.path.exists(file_name):
            return Image.open(file_name)

        # Directly download image
        img_response = requests.get(url)
        img = Image.open(BytesIO(img_response.content))

    else:
        # Get coordinates from url
        extract_coords = re.search(r"map=(-?\d+(\.\d+)?)/(-?\d+(\.\d+)?)/(-?\d+(\.\d+)?)", url).groups()
        lat, lon = extract_coords[2], extract_coords[4]
        position = lat, lon
        output_name += f'{position[0]}_{position[1]}'
        file_name = f'{OUTPUT_FOLDER}/{output_name}.jpg'

        if os.path.exists(file_name):
            print(f'Image {file_name} already exists')
            return Image.open(file_name)

        # Request on API
        request = f'{PANORAMAX_API}{SEARCH_URI}{position[0]},{position[1]}'
        logging.debug(f'Requesting {request}')
        response = requests.get(request)
        json_resp = response.json()
        print(request)

        # Parse json to get image and metadata
        data = {
            'img_url': json_resp['features'][0]['assets']['sd']['href'],
            'fov': json_resp['features'][0]['properties']['pers:interior_orientation']['field_of_view'],
            'provider': json_resp['features'][0]['providers'][0]['name']
        }
        logging.debug(json.dumps(data, indent=4))

        # Download image
        img_response = requests.get(data['img_url'])
        img = Image.open(BytesIO(img_response.content))

    # Reproject image from 360 to new fov and save in output folder
    reproject_img = panorama_to_plane(110, (1024, 682), yaw, pitch, image=img)
    if download:
        reproject_img.save(file_name)

    return reproject_img


if test_mode:
    url = args.test_url
    yaw = int(args.test_yaw)
    pitch = int(args.test_pitch)

    img = download_image(url, yaw, pitch, download=False)
    img.show()
else:
    nb_not_found = 0
    with open('urls.json', 'r') as file:

        data = json.load(file)
        nb_urls = sum(len(item['urls']) for item in data)
        print("Number of images : ", nb_urls)

        bar = tqdm(total=nb_urls, desc='Downloading images')

        for row in data:
            yaw = row['yaw']
            pitch = row['pitch']
            for url in row['urls']:
                try:
                    download_image(url, yaw, pitch)
                except Exception as e:
                    nb_not_found += 1
                bar.update(1)

        bar.close()
        if nb_not_found > 0:
            logging.warning(f'{nb_not_found} image(s) not found')
