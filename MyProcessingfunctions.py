
import numpy as np
import cv2
import CNN.labeling.labeling as lbl
import math



import warnings
from tensorflow.python.util.tf_stack import FrameSummary
warnings.simplefilter(action='ignore', category=FutureWarning)
import CNN.labeling.labeling as lbl

from tensorflow.keras.models import load_model

model = load_model('CNN/models/_vn_32_64_8_100_94.h5')


def custom_thresh(frame,thresh=65):
    kernel_size = 21
    gamma = 2
    p1 = cv2.medianBlur(frame,kernel_size)
    p2 = np.array(255*(p1 / 255) ** gamma, dtype = 'uint8')
    (T, p3) = cv2.threshold(p2, thresh, 255, cv2.THRESH_BINARY)
    p3 = np.array(p3,dtype=np.uint8)
    
    p4 = np.clip(np.abs(cv2.Laplacian(p3,cv2.CV_64F)),0,1)
    kernel = np.array([     
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]],dtype=np.uint8)
    p4 = 1-cv2.dilate(p4,kernel,iterations = 2)
    p5 = np.array(p4*frame,dtype=np.uint8)
    
    return (p5,1-p4)

def Predict_borders(frame):
    tile_size = 16
    shape = np.shape(frame)

    mask = np.zeros(shape,dtype=np.uint8)
    

    (x_start,y_start) = (0,0)
    while frame[x_start,y_start]<60:
        x_start = x_start + 1
        y_start = y_start + 1

    (x_end,y_end) = (shape[0],shape[1])
    while frame[x_end-1,y_end-1]<60:
        x_end = x_end - 1
        y_end = y_end - 1

    x_start += 16
    y_start += 16
    x_end -= 16
    y_end -= 16

    mask[x_start:x_end,y_start:y_end] = 1

    frame = np.array(frame*mask,dtype=np.uint8)

    frame_temp = frame.copy()

    frame = cv2.medianBlur(frame,21)



    (addr,tiles) = lbl.tile_image(frame,tile_size)

    for i,p in enumerate(tiles):
        tiles[i] = (np.array(p ,dtype=np.uint8).astype('float32')/255)
    tiles = np.array(tiles)
    tiles = np.reshape(tiles,(tiles.shape[0],16,16,1))

    
    # start_time = time.time()

    predictions = model.predict(tiles)
    # predictions = np.argmax(predictions, axis=-1)
    # print("--- %s seconds ---" % np.round(time.time() - start_time,5))
    
    (addr,tiles) = lbl.tile_image(frame_temp,tile_size)
    
    predict_frame = lbl.reconstruct_from_predictions(predictions,tiles,addr,tile_size)
    return predict_frame

def fill_hole(image,initial_point):
    """
          fill a hole in a binary image
          :param image: input binary image
          :param initial_point: a tuple of (y,x) of initial point
          :return: filled image
     """
    result = np.zeros(np.shape(image))
    result[initial_point] = 1
    end = False
    kernel = np.array([[0,1,0],[1,1,1],[0,1,0]],np.uint8)

    while end is not True:
        prev_result = result.copy()
        result = cv2.dilate(result,kernel,iterations = 1)
        result = result - np.logical_and(result,image)

        if np.sum(prev_result - result) == 0 :
            end = True

    return image + result

def track_point(point,frame,prev_frame,window_size=31):
    side_size = int(window_size/2)
    shape = np.shape(frame)
    if  point[0] < side_size+3 or \
        point[1] < side_size+3 or \
        shape[0]-point[0] < side_size or\
        shape[1]-point[1] < side_size:
        return point
    
    else:
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
        # Set up tracker.
        tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'CSRT', 'MOSSE']
        tracker_type = tracker_types[4]

        if int(major_ver) < 4 and int(minor_ver) < 3:
            tracker = cv2.cv2.Tracker_create(tracker_type)
        else:
            if cv2.__version__ > "4.5.2.53":
                if tracker_type == 'BOOSTING':
                    tracker = cv2.legacy.TrackerBoosting_create()
                if tracker_type == 'MIL':
                    tracker = cv2.legacy.TrackerMIL_create()
                if tracker_type == 'KCF':
                    tracker = cv2.legacy.TrackerKCF_create()
                if tracker_type == 'TLD':
                    tracker = cv2.legacy.TrackerTLD_create()
                if tracker_type == 'MEDIANFLOW':
                    tracker = cv2.legacy.TrackerMedianFlow_create()
                if tracker_type == 'CSRT':
                    tracker = cv2.legacy.TrackerCSRT_create()
                if tracker_type == 'MOSSE':
                    tracker = cv2.legacy.TrackerMOSSE_create()
            else:
                if tracker_type == 'BOOSTING':
                    tracker = cv2.TrackerBoosting_create()
                if tracker_type == 'MIL':
                    tracker = cv2.TrackerMIL_create()
                if tracker_type == 'KCF':
                    tracker = cv2.TrackerKCF_create()
                if tracker_type == 'TLD':
                    tracker = cv2.TrackerTLD_create()
                if tracker_type == 'MEDIANFLOW':
                    tracker = cv2.TrackerMedianFlow_create()
                if tracker_type == 'CSRT':
                    tracker = cv2.TrackerCSRT_create()
                if tracker_type == 'MOSSE':
                    tracker = cv2.TrackerMOSSE_create()

        bbox = (point[0]-side_size , point[1]-side_size , window_size , window_size)

        ok = tracker.init(prev_frame, bbox)

        if not ok:
            return point
        else:
            ok, bbox = tracker.update(frame)
            if ok:
                # Tracking success
                result = (int(bbox[0] + bbox[2]/2.0), int(bbox[1] + bbox[3]/2.0))
                return result
            else:
                return point

class curve_extractor:
    def __init__(self, _img,_min_line_surface):
        if _img is not None:
            self.img = _img.copy()
            self.shape = np.shape(self.img)
            self._min_line_surface = _min_line_surface
    
    def get_curves_as_image(self):
        _curves = []
        _temp_img = self.img.copy()

        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if _temp_img[i,j]==255:                

                    _temp = fill_hole((255-_temp_img)/255,(i,j))

                    _temp = np.array(_temp,dtype=np.uint8)
                    _temp = _temp_img-(1-_temp)*255
                    
                    _temp_img -= np.array(_temp,dtype=np.uint8)

                    if len(_curves)==0:
                        _curves = [_temp]
                    else:
                        _curves.append(_temp)


        return _curves

    def get_curves(self,min_points_distance):

        
        mask = np.zeros(self.shape,dtype=np.uint8)
        pad = 0.1
        mask[int(self.shape[0]*pad):int(self.shape[0]*(1-pad)),int(self.shape[1]*pad):int(self.shape[1]*(1-pad))] = 1

        self.img = np.array(self.img*mask,dtype=np.uint8)
        
        _curves_as_image = self.get_curves_as_image()
        

        # remove small curves
        i = 0
        while True:
            if i == len(_curves_as_image):
                break
            
            
            _sum = np.sum(np.array(_curves_as_image[i],dtype=np.uint8)/255)

            
            if _sum<self._min_line_surface:
                _curves_as_image.pop(i)
            else:
                i += 1


        
        checked_points = []
        curves_as_points = []
        
        _i = 0
        for curve in _curves_as_image:
            # _points = np.zeros(self.shape,dtype=np.uint8)
            _points = []
            for i in range(self.shape[0]):
                for j in range(self.shape[1]):
                    if (curve[i,j]==255) and ((i,j) not in checked_points):
                        
                        checked_points.append((i,j))
                        
                        if len(_points) == 0:
                            _points = [(i,j)]
                        else:
                            flag = True
                            for p in _points:
                                # if math.dist(p,(i,j))<min_points_distance:
                                if np.linalg.norm(np.array(p)-np.array((i,j)))<min_points_distance:
                                    flag = False
                            if flag:
                                _points.append((i,j))
                                # _points[i,j]=255
            curves_as_points.append(_points)
            # cv2.imwrite('p{:d}.png'.format(_i),_points)
            _i += 1

        return (curves_as_points,_curves_as_image)

                    
                    
