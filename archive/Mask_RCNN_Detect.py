import imagery
from mrcnn import model as modellib, utils
from mrcnn.config import Config
import os
from PIL import Image
import imageio
import numpy as np
import warnings
import geolocation

import matplotlib
matplotlib.use('PS')
import matplotlib.pyplot as plt
import matplotlib.path as pltPath

# scaling the image
from skimage.transform import resize as resize
warnings.filterwarnings('ignore')

# gets a minimum bounding rectangle
from Polygonify import Polygonify
import cv2

class InferenceConfig(Config):
    # Give the configuration a recognizable name
    NAME = "OSM_buildingdetector"

    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1  # 1 Backgroun + 1 Building

    IMAGE_MAX_DIM = 320
    IMAGE_MIN_DIM = 320


MODEL_DIR = ''
ROOT_DIR = ''

TILE_SIZE = 256

class Mask_RCNN_Detect():
    def __init__(self, weights):
        self.inference_config = InferenceConfig()
        self.model = modellib.MaskRCNN(
            mode="inference", config=self.inference_config, model_dir=MODEL_DIR)

        # model_path = os.path.join(ROOT_DIR, "weights/pretrained_weights.h5")
        model_path = os.path.join(ROOT_DIR, weights)
        print("Loading weights from ", model_path)
        self.model.load_weights(model_path, by_name=True)
        self.model.detect([imageio.core.util.Array(
            np.array(Image.open('default_images/tmp.PNG'))[:, :, :3])])
        print("initial detect works")

        # self.image_id = 1
        self.building_id = 1 # for id-ing buildings
        # I think the best way to do this right now is to store the data like so
        # geo_to_point
        # | -- xtile1, ytile1 : [ points ... ]
        # | -- xtile2, ytile2 : [ points ... ]
        # | -- ...
        # | -- merged [ points ... ]
        # so initially, all detections happen within a tile
        # then, user can merge buildings on frontend
        # I implement a merge feature, and the computation will be stored in a separate merged key
        self.geo_to_point = {}
        self.id_to_geo = {}

    # id-ing will help the Mask_R_CNN keep track of each building and adjustments that need to be made
    # rectanglify should always be called so we are using it not as a hyperparameter
    def detect_building(self, image, lat=None, lng=None, zoom=None, to_fill=False):
        rectanglify = True # passed  to backend functions
        assert(image.shape[-1] == 3) # must be size h x w x 3
        print('image shape', image.shape)

        # to return
        masks = None

        # image needs to be split into pieces
        if image.shape[0] > 400 or image.shape[1] > 400:
            print('Using detect multiple...')
            masks = self._detect_with_split(image, rectanglify, to_fill)
        else:
            print('Using detect single...')
            masks = self._detect_single(image, rectanglify, to_fill)
        
        # just a regular image, not part of Flask setup
        if lat is None or lng is None or zoom is None:
            # masks = resize(masks, (image.shape[0], image.shape[1]), preserve_range=True) # masks can be reshaped, corners can't
            masks = masks != 0 # converts to bool mask
            return masks

        Image.fromarray(masks != 0).save('mask_detection.png') # saves result for viewing
        # list of lat/lng points to plot
        to_return = {}

        # pass in top left tile lat long for very large detection batches
        # if just one tile, pass in that one tile's lat long
        def image_xy_to_tile(x, y, lat, lng):
            print(x, y, lat, lng)
            xtile, ytile = geolocation.deg_to_tile(lat, lng, zoom)
            xy_xtile = x // TILE_SIZE + xtile
            xy_ytile = y // TILE_SIZE + ytile
            x_in_tile = x - (x // TILE_SIZE) * TILE_SIZE # in the tile finds the x,y
            y_in_tile = y - (y // TILE_SIZE) * TILE_SIZE
            return xy_xtile, xy_ytile, x_in_tile, y_in_tile

        # finds corners
        building_ids = np.unique(masks)
        building_ids = building_ids[building_ids != 0].astype(int).tolist()
        for ids in building_ids:
            points = np.argwhere(masks == ids).tolist() # gets as coordinates
            for j in range(len(points)):
                x = points[j][1]
                y = points[j][0]

                lat0, lng0 = lat, lng
                if type(lat) == list:
                    lat0 = lat[0]
                    lng0 = lng[0]
                # finds the correct tile 
                xtile, ytile, x_in_tile, y_in_tile= image_xy_to_tile(x, y, lat0, lng0)
                # will be used 
                if (xtile, ytile) not in self.geo_to_point:
                    self.geo_to_point[(xtile, ytile)] = {}
                geopoint = list(geolocation.tilexy_to_deg(xtile, ytile, zoom, x_in_tile, y_in_tile))
                points[j] = geopoint
            # points[2], points[3] = points[3], points[2]
            to_return[self.building_id] = points
            # grabs the current xtile and ytile and puts the points in the dict
            self.geo_to_point[(xtile, ytile)][self.building_id] = points # all the points are stored in class memory
            self.id_to_geo[self.building_id] = (xtile+1, ytile+1) # if the building id is given, we can backtrace the geotile
            self.building_id += 1
        return to_return

    def _detect_single(self, image, rectanglify=True, to_fill=False):
        original_shape = image.shape
        image = (resize(image, (320, 320), anti_aliasing=True) * 256).astype(np.uint8)
        detection = self.model.detect(
            [imageio.core.util.Array(image)])
        masks = detection[0]['masks']
        masks = self._small_merge(masks)
            
        if rectanglify:
            # finds all buildings (one building has the same number in masks)
            building_ids = np.unique(masks)
            building_ids = building_ids[building_ids != 0]
            
            out_mask = np.zeros(original_shape, dtype=np.uint8)
            y_corrector = original_shape[0] / 320
            x_corrector = original_shape[1] / 320

            for i, ids in enumerate(building_ids):
                building_corner_image = self._detect_mask_corners(masks == ids) # gets the corners of a building in a boolean mask
                points = np.argwhere(building_corner_image) # gets as coordinates
                plottable = []
                print(ids, points)
                for x,y in zip(points[:,0], points[:,1]):
                    y *= int(y_corrector)
                    x *= int(x_corrector)
                    plottable.append((y, x))
                    if not to_fill: # if not to_fill, then we need to exract the corners and use image_id
                        out_mask[x,y,:] = np.array([self.building_id] * 3) # gets the corner
                self.building_id += 1 # gives each building a unique id
                plottable[2], plottable[3] = plottable[3], plottable[2] # reorders points
                # tmp = np.copy(plottable[2]) # reorders points
                # plottable[2] = plottable[3]
                # plottable[3] = tmp
                plottable = np.array(plottable, np.int32).reshape(-1,1,2)
                if to_fill:
                    cv2.fillPoly(out_mask, [plottable], (i+1,i+1,i+1)) # draws a rectangle using points; EDGE CASE: i + 1 >= 256 due to so many buildings?
            masks = out_mask[:,:,0]
        else:
            masks = resize(masks, original_shape, anti_aliasing=True, preserve_range=True)

        return masks # not resized back

    def _detect_with_split(self, image, rectanglify=True, to_fill=False):
        minimum = InferenceConfig.IMAGE_MAX_DIM
        height, width = image.shape[0], image.shape[1]

        vert_num_splits = height // minimum
        horiz_num_splits = width // minimum

        final_mask = np.zeros((image.shape[0], image.shape[1])).astype(int)
        # svi = start_vert_index; evi = end_vert_endex
        svi, evi = None, None
        for i in range(vert_num_splits + 1):
            # update svi, evi
            if svi is None: svi = i * minimum
            else: svi = evi
            if i == vert_num_splits - 1 or vert_num_splits == 0:
                evi = height - 1
            else:
                evi = (i + 1) * (height // vert_num_splits)

            # shi = start_horiz_index; ehi = end_horiz_index
            shi, ehi = None, None
            for j in range(horiz_num_splits + 1):
                # update shi, ehi
                if shi is None: shi = j * minimum
                else: shi = ehi
                if j == horiz_num_splits - 1 or horiz_num_splits == 0:
                    ehi = width - 1
                else:
                    ehi = (j + 1) * (width // horiz_num_splits)
                
                im = image[svi:evi, shi:ehi, :]
                original_shape = im.shape
                im = (resize(im, (InferenceConfig.IMAGE_MAX_DIM, InferenceConfig.IMAGE_MAX_DIM), anti_aliasing=True) * 256).astype(np.uint8)
                detection = self.model.detect(
                    [imageio.core.util.Array(im)])
                masks = detection[0]['masks']
                masks = self._small_merge(masks)

                if rectanglify:
                    # finds all buildings (one building has the same number in masks)
                    building_ids = np.unique(masks)
                    building_ids = building_ids[building_ids != 0]
                    
                    out_mask = np.zeros(original_shape, dtype=np.uint8)
                    y_corrector = original_shape[0] / InferenceConfig.IMAGE_MAX_DIM
                    x_corrector = original_shape[1] / InferenceConfig.IMAGE_MAX_DIM

                    for ind, ids in enumerate(building_ids):
                        building_corner_image = self._detect_mask_corners(masks == ids) # gets the corners of a building in a boolean mask
                        points = np.argwhere(building_corner_image) # gets as coordinates
                        plottable = []
                        for y,x in zip(points[:,0], points[:,1]):
                            y = int(y * y_corrector)
                            x = int(x * x_corrector)
                            plottable.append((y, x))
                            if not to_fill: # if not to_fill, then we need to exract the corners and use image_id
                                out_mask[y,x,:] = np.array([self.building_id] * 3) # gets the corner
                        self.building_id += 1 # gives each building a unique id
                        tmp = np.copy(plottable[2]) # reorders points
                        plottable[2] = plottable[3]
                        plottable[3] = tmp
                        plottable = np.array(plottable, np.int32).reshape(-1,1,2)
                        if to_fill:
                            cv2.fillPoly(out_mask, [plottable], (ind+1,ind+1,ind+1)) # draws a rectangle using points; EDGE CASE: i + 1 >= 256 due to so many buildings?
                    masks = out_mask[:,:,0]
                else:
                    masks = resize(masks, original_shape, anti_aliasing=True, preserve_range=True)
                # pastes result into the final mask
                final_mask[svi:evi, shi:ehi] = masks
                np.save('final_mask', final_mask)
        
        return final_mask

    # merges buildings and prevents significant overlap / massive masks
    def _small_merge(self, masks):  # merges only the small ones inside
        net_mask = np.zeros((masks.shape[0], masks.shape[1]))
        for i, layer in enumerate(range(masks.shape[2])):
            m = masks[:, :, layer]  # gives an id
            shared = (m & (net_mask != 0))
            i += 1 # ids range from 1 to # buildings
            shared_count = np.count_nonzero(shared)
            if (shared_count > 100):
                new_id = i
                tmp = np.argwhere(shared)[0]
                collision_id = net_mask[tmp[0], tmp[1]]
                collision_id_mask = net_mask == collision_id

                new_count = np.count_nonzero(m)
                collision_count = np.count_nonzero(collision_id_mask)

                if new_count < collision_count:
                    net_mask[collision_id_mask] = 0
                    net_mask += m * new_id
            else:
                net_mask += m * i

        return net_mask # can make this into a single boolean mask by running net_mask != 0

    # need a way to efficiently do this, perhaps sort by tile
    # given a lat/lng or a building_id, it deletes a building
    def delete_mask(self, lat=None, lng=None, zoom=None, building_id=None):
        assert lat is not None or building_id is not None
        if building_id is not None:
            xtile, ytile = self.id_to_geo[building_id]
            del self.geo_to_point[(xtile, ytile)][building_id]
            del self.id_to_geo[building_id]
            return building_id

        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(lat, lng, zoom)
        if (xtile+1, ytile+1) in self.geo_to_point:
            relevant = self.geo_to_point[(xtile+1,ytile+1)]
            for building_id in relevant:
                points = relevant[building_id]
                polygon = pltPath.Path(points)
                if polygon.contains_point([lat,lng]):
                    del relevant[building_id]
                    del self.id_to_geo[building_id]
                    return building_id
        return -1 # no match


    # gets the corners from a boolean mask, returns a new mask with just the corners
    def _detect_mask_corners(self, im):
        dst = cv2.cornerHarris(np.float32(im),2,3,0.04)
        idxs = np.argwhere(dst != 0)
        guides = np.median(idxs, axis=0)
        
        distr = np.sum((idxs - guides)**2,axis=1)
        # helps rule out far points that don't belong to the main image
        std = np.std(distr)
        median = np.median(distr)
        
        lookup = np.any([distr < (2*std + 1) * median, distr > (1 - 2*std) * median], axis=0)
        
        pg = Polygonify(idxs[lookup])
        corners = pg.find_polygon()

        img = np.zeros(im.shape, dtype=bool)
        for x,y in zip(corners[:,0], corners[:,1]):
            x = int(round(x))
            y = int(round(y))
            if x < 0: x = 0
            elif x >= im.shape[0]: x = im.shape[0] - 1
            if y < 0: y = 0
            elif y >= im.shape[1]: y = im.shape[1] - 1
            img[x,y] = True
        return img

    def plot_corners(self, dict_corners, mask_shape):
        out_mask = np.zeros(mask_shape)
        for i, v in enumerate(dict_corners.values()):
            cv2.fillPoly(out_mask, [np.array(v)], (i+1,i+1,i+1))
        return out_mask
