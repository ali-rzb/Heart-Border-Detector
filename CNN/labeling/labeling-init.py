
import os
import cv2 as cv
import numpy as np
import labeling as lbl

for _i in range(1,4):
    prefix = 'frame_1_{:02d}'.format(_i)
    img = cv.imread('frames/{:s}.png'.format(prefix),0)
    tile_size = 16
    tile_num_x = 77
    tile_num_y = 77
    _path = 'data/'+prefix+'_data_'+str(tile_size)
    if os.path.isdir(_path) is False:
        os.makedirs(_path)
    # cv.imshow('original',img)    
    img = cv.medianBlur(img,21)
    
    print(_i)
    # get border from user and save it
    selected_border = lbl.input(img).getPoints()
    cv.imwrite(_path+'/selected_border.png',np.array(selected_border*255,dtype=np.uint8))

    # get border from saved file and tile and class the data
    selected_border = cv.imread(_path+'/selected_border.png',0)/255
    lbl.tile_and_save(img,tile_size,selected_border, _path)