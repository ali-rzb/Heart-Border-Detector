import numpy as np
import cv2 as cv
import os

class input:
    img = None
    border_map = None
    
    STATUS = None
    
    points_img = None

    points = []

    selected_point = -1
    
    color = (0,0,0)
    color_active = (36,28,237)

    def __init__(self, _img):
        self.img = _img.copy()
        self.border_map = np.ones(np.shape(_img))
        self.points = []
        self.sorted_points = []
        self.STATUS = 0
        self.selected_point = -1

    def make_resizable_window(self,window_name,img):
        # show output in a resizable and proper defult size
        screen_res = 1920, 1080
        scale_width = screen_res[0] / img.shape[1]
        scale_height = screen_res[1] / img.shape[0]
        scale = min(scale_width, scale_height)*0.5
        window_width = int(img.shape[1] * scale)
        window_height = int(img.shape[0] * scale)
        # window_name = ''
        cv.namedWindow(window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(window_name, window_width, window_height)

    def add_point(self,_point):
        self.points.append(_point)
        self.sorted_points.clear()
        
        temp = []
        for p in self.points:
            if p[0] == -10:
                if len(temp) != 0:
                    temp.sort(key = lambda _p: (_p[0] - 0)**2 + (_p[1] - 0)**2)
                    self.sorted_points = self.sorted_points + temp
                    temp.clear()
                self.sorted_points.append((-10,-10))
            else:
                temp.append(p)
        
        if len(temp) != 0:
            temp.sort(key = lambda _p: (_p[0] - 0)**2 + (_p[1] - 0)**2)
            self.sorted_points = self.sorted_points + temp
            temp.clear()

    def update_points(self,_point):
        for i,p in enumerate(self.sorted_points):
            if p == self.points[self.selected_point]:
                self.sorted_points[i] = _point
        self.points[self.selected_point] = _point

    def undo_points(self):
        if len(self.points)!=0:
            _last_point = self.points[len(self.points)-1]
            self.sorted_points.remove(_last_point)
            self.points.remove(_last_point)

    # mouse callback function
    def draw(self,event,x,y,flags,param):
        if event == cv.EVENT_LBUTTONDOWN:
            if self.STATUS == 0:
                # cv.circle(self.border_map,(x,y),4,self.color,-1)
                self.STATUS = 1
                self.add_point((x,y))
            elif self.STATUS == 1:
                if self.selected_point == -1:
                    for i,p in enumerate(self.points):
                        if ( ((p[0]-x)**2+(p[1]-y)**2)**0.5 < 20 ):
                            self.selected_point = i
                            break                  
                    if self.selected_point == -1:
                        # cv.circle(self.border_map,(x,y),4,self.color,-1)
                        self.add_point((x,y))
                    else:
                        pass
                else:
                    self.selected_point = -1
        elif ( (event == cv.EVENT_MOUSEMOVE) and (self.selected_point != -1) ):
            self.update_points((x,y))

    def getPoints(self):
        self.make_resizable_window('img',self.img)
        cv.setMouseCallback('img',self.draw)
        while(1):
            self.border_map = np.ones(np.shape(self.img))
            last_point = (0,0)
            for i,p in enumerate(self.sorted_points):
                if p[0]!=-10:
                    cv.circle(self.border_map,p,1,self.color,-1)
                    if ((i!=0) and (self.sorted_points[i-1][0]!=-10)):
                        self.border_map = cv.line(self.border_map,last_point,p,self.color,1,cv.LINE_AA)
                    last_point = p
            cv.imshow('img', np.array(self.border_map * self.img,dtype=np.uint8) )
            key = chr(cv.waitKey(20) % 256)
            if key == 'q':
                break
            elif key == 'c':
                self.points.clear()
            elif key == 'z':
                self.undo_points()
            elif key == 'n':
                if (len(self.points)!=0) and (self.points[len(self.points)-1] != -10):
                    self.add_point((-10,-10))
            elif key == 't':
                print(self.points)
                print(self.sorted_points)
        cv.destroyAllWindows()
        return self.border_map       

def tile_class(x,y,_tile_size,selected_points):
    selected_points = selected_points
    if(np.product(selected_points[x:x+_tile_size,y:y+_tile_size]) ==1):
        return 'C0'
    else:
        return 'C1'

def tile_and_save(img,tile_size,selected_points,_path_to_save):
    shape = np.shape(img)
    _tile_size = tile_size
    _pad = int(_tile_size/4)
    _tile_size = _pad*4
    (x_start,y_start) = (0,0)
    while img[x_start,y_start]<60:
        x_start = x_start + 1
        y_start = y_start + 1
    (x_end,y_end) = (shape[0],shape[1])
    while img[x_end-1,y_end-1]<60:
        x_end = x_end - 1
        y_end = y_end - 1
    x = x_start
    y = y_start
    i,j = 0,0
    if os.path.isdir(_path_to_save) is False:
        os.makedirs(_path_to_save)
    if os.path.isdir(_path_to_save+'/C0') is False:
        os.makedirs(_path_to_save+'/C0')
    if os.path.isdir(_path_to_save+'/C1') is False:
        os.makedirs(_path_to_save+'/C1')
    while True:
        if ((x+_tile_size<=x_end) and (y+_tile_size<=y_end)) : 
            name = tile_class(x,y,_tile_size,selected_points) + '/p('+str(i)+','+str(j)+').png'
            name = _path_to_save + '/' + name
            cv.imwrite(name,img[x:x+_tile_size,y:y+_tile_size])
            x = x + 3*_pad
            i = i + 1
        elif ((x+_tile_size>x_end) and (y+_tile_size>y_end)) :
            break
        elif x+_tile_size>x_end:
            i = 0
            j = j+1
            x = x_start
            y = y + 3*_pad
        elif y+_tile_size>y_end:
            x = x + 3*_pad
            i = i + 1

def tile_image(img,tile_size,_path_to_save=None):
    shape = np.shape(img)
    _tile_size = tile_size
    _pad = int(_tile_size/4)
    _tile_size = _pad*4
    (x_start,y_start) = (0,0)
    # while img[x_start,y_start]<60:
    #     x_start = x_start + 1
    #     y_start = y_start + 1
    (x_end,y_end) = (shape[0],shape[1])
    # while img[x_end-1,y_end-1]<60:
    #     x_end = x_end - 1
    #     y_end = y_end - 1
    x = x_start
    y = y_start
    i,j = 0,0
    tiles = []
    address = None
    _index = 0
    while True:
        if ((x+_tile_size<=x_end) and (y+_tile_size<=y_end)) : 
            # temp = pd.DataFrame( [ [str(i)+','+str(j),'C0', img[x:x+_tile_size,y:y+_tile_size] ] ], columns=['filename','class','image'], index=[_index])
            temp = np.array(img[x:x+_tile_size,y:y+_tile_size])
            if len(tiles) == 0:
                address = [(i,j)]
                tiles = [temp]
                # tiles = [np.array(img[x:x+_tile_size,y:y+_tile_size])]
            else:
                address.append((i,j))
                tiles.append(temp)
                # tiles.append(np.array(img[x:x+_tile_size,y:y+_tile_size]))            
            _index = _index + 1
            x = x + 3*_pad
            i = i + 1
        elif ((x+_tile_size>x_end) and (y+_tile_size>y_end)) :
            break
        elif x+_tile_size>x_end:
            i = 0
            j = j+1
            x = x_start
            y = y + 3*_pad
        elif y+_tile_size>y_end:
            # cv.imwrite(_path_to_save+'/p('+str(i)+','+str(j)+').png',img[x:x+_tile_size,y:y_end])
            x = x + 3*_pad
            i = i + 1
    return (address,tiles)

def reconstruct_from_predictions(predictions,tiles,tiles_addr,tile_size):
    _pad = int(tile_size/4)
    img_rec = []
    temp = []
    bin_img_rec = []
    bin_temp = []
    bin_tile = []
    zero = np.zeros((tile_size,tile_size),dtype=np.uint8)
    one = np.ones((tile_size,tile_size),dtype=np.uint8)
    for tile,addr,prediction in zip(tiles,tiles_addr,predictions):
        if prediction[1] >= 0.5:
            _temp = np.array(tile,dtype=np.int) - 50
            tile = np.array(np.clip(_temp,0,255),dtype=np.uint8)
            bin_tile = one.copy()
        else:
            bin_tile = zero.copy()
        # start of new tile line
        if addr[0] == 0:
            if len(img_rec) == 0:
                img_rec = temp
                bin_img_rec = bin_temp
            else:
                img_rec = np.hstack((img_rec,temp))
                bin_img_rec = np.hstack((bin_img_rec,bin_temp))
            temp = tile[0:3*_pad , 0:3*_pad]
            bin_temp = bin_tile[0:3*_pad , 0:3*_pad]
        else:
            temp = np.vstack((temp,tile[0:3*_pad , 0:3*_pad]))
            bin_temp = np.vstack((bin_temp,bin_tile[0:3*_pad , 0:3*_pad]))
    return (img_rec,bin_img_rec)
        
def get_tile(_i_,_j_,entries,_path_to_read, _pad):
    for entry in entries:
        if ('p('+str(_i_)+','+str(_j_)+')') in entry.name:
            name = entry.name
    _read = cv.imread(_path_to_read+'/'+name,0)[0:3*_pad , 0:3*_pad]
    if name[1] == '1':
        _read = _read - 50
    return _read
    
def get_full_tile_and_name(_i_,_j_,entries,_path_to_read, _pad):
    for entry in entries:
        if ('p('+str(_i_)+','+str(_j_)+')') in entry.name:
            name = entry.name
    _read = cv.imread(_path_to_read+'/'+name,0)
    if name[1] == '1':
        _read = _read - 50
    return (name,_read)

def reconstruct_from_tiles(_path_to_read,tile_size,_i,_j):
    _tile_size = tile_size
    _pad = int(_tile_size/4)
    _tile_size = _pad*4
    img_rec = []
    entries = list(os.scandir(_path_to_read+'/'))
    for i in range(_i):
        _read = get_tile(i,0,entries,_path_to_read,_pad)
        temp = _read
        for j in range(1,_j):
            _read = get_tile(i,j,entries,_path_to_read,_pad)
            temp = np.hstack((temp,_read))
        if i != 0:
            img_rec = np.vstack((img_rec,temp))
        else:
            img_rec = temp
    return img_rec
