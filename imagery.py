"""Interface for downloading aerial imagery from Mapbox.
"""

import requests
from PIL import Image
from io import BytesIO
import os.path
import numpy as np
from mapbox import Maps
import matplotlib
matplotlib.use('PS') # for macOS
import matplotlib.pyplot as plt

import geolocation

class ImageryDownloader(object):

    def __init__(self, access_token):
        """Initializes the object with a Mapbox access token"""
        self.maps = Maps(access_token=access_token)

    def get_image_from_latlng_outline(self, corner1, corner2, zoom=18):
        xtile1, ytile1 = geolocation.deg_to_tile(corner1[0], corner1[1], zoom)
        xtile2, ytile2 = geolocation.deg_to_tile(corner2[0], corner2[1], zoom)

        larger_x, smaller_x = xtile2, xtile1
        if xtile1 > xtile2:
            larger_x, smaller_x = xtile1, xtile2
        larger_y, smaller_y = ytile2, ytile1
        if ytile1 > ytile2:
            larger_y, smaller_y = ytile1, ytile2

        x_range = larger_x - smaller_x
        y_range = larger_y - smaller_y

        # image = Image.new("RGB", (256 * (x_range + 1), 256 * (y_range + 1)))
        images = []
        lat_lngs = []
        for i_x, xt in enumerate(range(smaller_x, larger_x + 1)):
            for i_y, yt in enumerate(range(smaller_y, larger_y + 1)):
                try:
                    tile_part = self.download_tile(xt, yt, zoom)
                    # image.paste(tile_part, (256 * i_x, 256 * i_y))
                    images.append(np.array(tile_part))
                    lat_lngs.append(geolocation.tile_to_deg(xt, yt, 18))
                except Exception as e:
                    print(e)
                    pass
        return images, lat_lngs # image
    
    def download_tile(self, x, y, zoom):
        """Downloads a map tile as an image.
           Note that x and y refer to Slippy Map coordinates.
        """
        print(x, y, zoom)
        response = self.maps.tile("mapbox.satellite", x, y, zoom)
        image = Image.open(BytesIO(response.content))

        return image

    # def get_tile_filename(self, x, y, zoom):
    #     """Get the filename for a given tile"""
    #     img_fname = "imgcache/" + str(zoom) + "/" + str(x) + "/" + str(y) + ".png"
    #     return img_fname
    
    def get_tiles_around(self, x, y, zoom):
        im = self.download_tile(x, y, zoom)
        print(im.size, np.array(im).shape)
        return im
        # """Downloads all the tiles around the x, y tile"""
        # image = Image.new("RGB", (256 * 3, 256 * 3))
        # for i in range(-1, 2, 1):
        #     for j in range(-1, 2, 1):
        #         try:
        #             tile_part = Image.fromarray(self.download_tile(x + i, y + j, zoom))
        #             image.paste(tile_part, (256 * (i + 1), 256 * (j + 1)))
        #         except:
        #             pass
        # return image
