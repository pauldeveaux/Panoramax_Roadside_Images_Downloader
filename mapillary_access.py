import os
from io import BytesIO
from PIL import Image
from tqdm import tqdm
import mercantile, requests, json
from vt2geojson.tools import vt_bytes_to_geojson
from reproject_360_img import panorama_to_plane

output= { "type": "FeatureCollection", "features": [] }

tile_coverage = 'mly1_public'
access_token = 'MLY|26319375920994303|57250902423017bf4350e1075ed2fa20'

tile_layer = 'image'

west, south, east, north = [-4.463196,48.378145,-4.210510,48.507507]

tiles = list(mercantile.tiles(west, south, east, north, 14))

if not os.path.exists('output'):
    os.makedirs('output')
if not os.path.exists('output/360'):
    os.makedirs('output/360')
if not os.path.exists('output/plane'):
    os.makedirs('output/plane')

for tile in tiles:
    tile_url = 'https://tiles.mapillary.com/maps/vtp/{}/2/{}/{}/{}?access_token={}'.format(tile_coverage,tile.z,tile.x,tile.y,access_token)
    response = requests.get(tile_url)
    data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z,layer=tile_layer)

    # push to output geojson object if yes
    for feature in tqdm(data['features']):
        if feature['properties']['is_pano'] is False:
            continue

        lng = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]

        if west < lng < east and south < lat < north:

            # create a folder for each unique sequence ID to group images by sequence
            sequence_id = feature['properties']['sequence_id']

            # request the URL of each image
            image_id = feature['properties']['id']
            if os.path.exists('output/360/{}.jpg'.format(image_id)):
                continue
            header = {'Authorization': 'OAuth {}'.format(access_token)}
            url = 'https://graph.mapillary.com/{}?fields=thumb_2048_url'.format(image_id)
            r = requests.get(url, headers=header)
            data = r.json()
            image_url = data['thumb_2048_url']

            # save each image with ID as filename to directory by sequence ID
            with open('output/360/{}.jpg'.format(image_id), 'wb') as handler:
                image_data = requests.get(image_url, stream=True).content
                handler.write(image_data)

                img = Image.open(BytesIO(image_data))
                reproject_img = panorama_to_plane(110, (1024, 682), 0, 105, image=img)
                reproject_img.save('output/plane/{}.jpg'.format(image_id))
