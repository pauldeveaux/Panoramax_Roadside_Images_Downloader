# Panoramax Downloader

This project is a Python-based application designed to download images from the Panoramax platform. It uses a JSON file containing URLs of the images to be downloaded.

## Project Structure

The main script of the project is `main.py`. This script reads a JSON file named `urls.json` which contains the URLs of the images to be downloaded.

## How to Download Images

To download images, you need to run the `main.py` script. Before running the script, make sure that the `urls.json` file is properly formatted and contains the URLs of the images you want to download.

Here is an example of how the `urls.json` file should be structured:

```json
[
  {
    "trajet": "https://panoramax.openstreetmap.fr/#background=streets&focus=pic&map=20/46.8893148/-2.1187607&pic=a007a778-d24d-4978-9e69-d7bbf3bed4de&pic_type=equirectangular&speed=250&theme=default&xyz=116.17/-9.80/30",
    "yaw": 180,
    "pitch": 75,
    "urls": [
      "https://panoramax-storage-public-fast.s3.gra.perf.cloud.ovh.net/main-pictures/a1/40/65/4a/6afc-4b8f-983d-65c101fc982e.jpg",
      "https://panoramax-storage-public-fast.s3.gra.perf.cloud.ovh.net/main-pictures/fb/c6/11/bb/00d2-408c-9e1a-cfeec9b2d7ea.jpg",
      // More URLs...
    ]
  },
  // More items...
]
```

Each item in the JSON file represents a set of images to be downloaded. The `urls` field is an array of URLs of the images.

To run the script, use the following command:

```bash
python main.py
```

This will start the download process. The script will iterate over each item in the `urls.json` file, and for each item, it will download all the images from the URLs listed in the `urls` field.

The downloaded images will be saved in the same directory as the script.

Please note that you need to have Python installed on your machine to run the script.

## How to configure and test an image

To test an image, you can use the `main.py` script with the `--test` flag. 
You have to provide the URL of the image and the yaw and pitch values to apply to the image with 
the --test_url, --test_yaw, and --test_pitch flags.
This will download the image from the provided URL and apply the yaw and pitch values specified in the `urls.json` file.

Here is how you can use the `test_image.py` script:

This will show you the image with the yaw and pitch values applied so you can easily configure them in the `urls.json` file.

Please note that all images from the same "trajet" have the same yaw and pitch values because they are taken from the same 
vehicle and camera configuration.
