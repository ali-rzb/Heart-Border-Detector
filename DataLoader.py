from tkinter import Frame, Canvas, CENTER, ROUND
from PIL import Image, ImageTk
import cv2
import numpy as np
import time
import os

import MyProcessingfunctions as PF
import matplotlib.pyplot as plt

import math

class DataLoader(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master=master, bg="gray", width=512, height=512)

        self.shown_video = None
        self.ratio = 0
        self.interval = 20

        self.canvas = Canvas(self, bg="gray", width=512, height=512)
        self.canvas.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.draw_ids = list()
        self.draw_ids_points = list()
        self.frame_number = 0

            
        self.points = []
        self.points_copy = []
        self.selected_point = -1
        self.mouse_status = -1
        self.delete_mode = False

        self.color = (0,0,0)
        self.color_active = (36,28,237)   

        self.frame = None
        self.prev_frame = None

        self.repeat_count = 0

    def show_video(self):
        self.clear_canvas()
        if self.master.filename != "":
            
            self.video = cv2.VideoCapture(self.master.filename)
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
            self.interval = int((1/float(self.fps))*1000)
            
            ret, self.frame = self.video.read()
            if not ret:
                self.master.message.set('pls select a valid video!')
            else:
                self.frame_number = 0
                start_time = time.time()

                # grayscale the frame
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                self.prev_frame = self.frame.copy()
                shape = np.shape(self.frame)
                
                
                self.calculate_new_sizes(self.frame)
                self.calculate_new_frame(self.frame)
                self.show_image_canvas()

                # show info
                message = "video info : \n\n"+\
                    "filename : {:s}\nsize          : ({:d},{:d})\nfps           : {:d}"\
                        .format(os.path.basename(self.master.filename),shape[0],shape[1],int(self.fps))
                self.master.message.set(message)
                            
                # predict using trained model
                (self.predicted_frame, self.binary_predicted_frame) = PF.Predict_borders(self.frame)
                
                # dialate predicted borders
                kernel = np.array([     
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1]],dtype=np.uint8)
                n = 10
                self.binary_predicted_frame = cv2.dilate(self.binary_predicted_frame*255,kernel,iterations=n)
                self.binary_predicted_frame = cv2.erode(self.binary_predicted_frame,kernel,iterations=n)

                # extract the curves
                (self.result_curves,self.result_curves_as_images) = PF.curve_extractor(self.binary_predicted_frame,2000).get_curves(70)

                # extract the points
                self.points = []
                self.sorted_points = []

                for curve in self.result_curves:
                    self.points.append((-10,-10))
                    for point in curve:
                       self.points.append((point[1],point[0]))
                self.points.append((-10,-10))

                self.points_copy = self.points.copy()

                self.selected_point = -1
                self.draw_lines()


                self.master.time_label_msg.set('preprocessing time : {:d}ms'.format(int( (time.time()-start_time)*1000 )))
                

                # activate editing mode
                self.canvas.bind("<ButtonPress>", self.mouse_down)
                self.canvas.bind("<ButtonRelease>", self.release_mouse)
                self.canvas.bind("<Motion>", self.move_point)
                self.canvas.bind("<Double-Button-1>", self.delete_point)

    def mouse_down(self,event):
        x = event.x
        y = event.y
        self.mouse_status='moving'
        
        for i,p in enumerate(self.points):
            # if ( math.dist(p,(x,y)) < 20 ):
            if np.linalg.norm(np.array(p)-np.array((x,y))) < 20:
                self.selected_point = i
                break

        if self.selected_point == -1:    
            self.points.append((x,y))
            _len = len(self.points)
            
            draw_id = self.canvas.create_line(x, y, x, y, width=8,fill="black", capstyle=ROUND, smooth=True)
            self.draw_ids.append((_len-1,draw_id))
            if ( (_len > 1) and (self.points[_len-2][0]!=-10) ):
                draw_id = self.canvas.create_line(self.points[_len-2][0],self.points[_len-2][1], x, y, width=5,fill="black", capstyle=ROUND, smooth=True)
                self.draw_ids.append((_len-1,draw_id))
            self.selected_point = _len-1
        else:
            self.points[self.selected_point] = (x,y)

            # starting points
            if (self.selected_point > 0) and (self.selected_point != len(self.points)-1):
                if self.points[self.selected_point-1][0] == -10:
                    self.delete_canvas_obj(self.selected_point+1,'line')
                    draw_id = self.canvas.create_line( x, y,self.points[self.selected_point+1][0],self.points[self.selected_point+1][1], width=5,fill="black", capstyle=ROUND, smooth=True)
                    self.draw_ids.append((self.selected_point+1,draw_id))
            
            self.delete_canvas_obj(self.selected_point)

            draw_id = self.canvas.create_line(x, y, x, y, width=8,fill="black", capstyle=ROUND, smooth=True)
            self.draw_ids.append((self.selected_point,draw_id))
            if ( (self.selected_point > 0) and (self.points[self.selected_point-1][0]!=-10) ):
                draw_id = self.canvas.create_line(self.points[self.selected_point-1][0],self.points[self.selected_point-1][1], x, y, width=5,fill="black", capstyle=ROUND, smooth=True)
                self.draw_ids.append((self.selected_point,draw_id))  

    def release_mouse(self,event):
        self.mouse_status = -1
        self.selected_point = -1
        self.master.editbar.cleat_points_button["state"] = "normal"

    def move_point(self,event):
        x = event.x
        y = event.y
        if self.mouse_status == 'moving':
            if self.selected_point != -1:

                self.points[self.selected_point] = (x,y)
                
                    
                # starting points
                if ((self.selected_point == 0) or (self.points[self.selected_point-1][0] == -10)) and (self.selected_point != len(self.points)-1):

                    self.delete_canvas_obj(self.selected_point+1,'line')
                    draw_id = self.canvas.create_line( x, y,self.points[self.selected_point+1][0],self.points[self.selected_point+1][1], width=5,fill="black", capstyle=ROUND, smooth=True)
                    self.draw_ids.append((self.selected_point+1,draw_id))

                self.delete_canvas_obj(self.selected_point)                        


                draw_id = self.canvas.create_line(x, y, x, y, width=8,fill="black", capstyle=ROUND, smooth=True)
                self.draw_ids.append((self.selected_point,draw_id))
                if ( (self.selected_point > 0) and (self.points[self.selected_point-1][0]!=-10) ):
                    draw_id = self.canvas.create_line(self.points[self.selected_point-1][0],self.points[self.selected_point-1][1], x, y, width=5,fill="black", capstyle=ROUND, smooth=True)
                    self.draw_ids.append((self.selected_point,draw_id))

                if (self.selected_point > 0) and (len(self.points)-1 > self.selected_point):
                    if self.points[self.selected_point+1][0] != -10:
                        self.delete_canvas_obj(self.selected_point+1,'line')
                        draw_id = self.canvas.create_line(self.points[self.selected_point+1][0],self.points[self.selected_point+1][1], x, y, width=5,fill="black", capstyle=ROUND, smooth=True)
                        self.draw_ids.append((self.selected_point+1,draw_id))
            else:
                _len = len(self.points)
                self.points[_len-1] = (event.x,event.y)
                
                self.delete_canvas_obj(_len-1)

                draw_id = self.canvas.create_line(x, y, x, y, width=8,fill="black", capstyle=ROUND, smooth=True)
                self.draw_ids.append((_len-1,draw_id))
                if ( (self.selected_point > 0) and (self.points[self.selected_point-1][0]!=-10) ):
                    draw_id = self.canvas.create_line(self.points[self.selected_point-1][0],self.points[self.selected_point-1][1], x, y, width=5,fill="black", capstyle=ROUND, smooth=True)
                    self.draw_ids.append((_len-1,draw_id))
        
    def delete_point(self,event):
        x = event.x
        y = event.y

        for i,p in enumerate(self.points):
            # if ( math.dist(p,(x,y)) < 20 ):
            if np.linalg.norm(np.array(p)-np.array((x,y))) < 20:
                self.selected_point = i
                break                
        
        self.points.pop(self.selected_point)
        self.draw_lines()
   
    def draw_lines(self):
        last_point = (0,0)
        self.show_image_canvas()
        self.draw_ids.clear()
        for i,p in enumerate(self.points):
            if p[0]!=-10:
                
                draw_id = self.canvas.create_line(p[0], p[1], p[0], p[1], width=8,fill="black", capstyle=ROUND, smooth=True)
                self.draw_ids.append((i,draw_id))

                if ((i!=0) and (self.points[i-1][0]!=-10)):
                    draw_id = self.canvas.create_line(last_point[0],last_point[1], p[0], p[1], width=5,fill="black", capstyle=ROUND, smooth=True)
                    self.draw_ids.append((i,draw_id))

                last_point = p
        if len(self.points)!=0:
            self.master.editbar.cleat_points_button["state"] = "normal"
        else:
            self.master.editbar.cleat_points_button["state"] = "disabled"

    def clear_point(self):
        self.points.clear()
        self.draw_lines()
        self.master.editbar.cleat_points_button["state"] = "disabled"

    def new_curve(self):
        if len(self.points) != 0:
            if self.points[len(self.points)-1][0] != -10:
                self.points.append((-10,-10))

    def delete_canvas_obj(self,_i, _point_or_line=None):
        _indexes = []
        _point_index = None
        (_x,_y) = self.points[_i]

        _n = 0

        for i,p in enumerate(self.draw_ids):
            if (self.points[p[0]][0] == _x) and (self.points[p[0]][1] == _y):
                
                if _point_or_line == 'point':
                    if _n == 0:
                        self.canvas.delete(p[1])
                        _indexes.append(i)
                        _point_index = p[0]
                elif _point_or_line == 'line':
                    if _n == 1:
                        self.canvas.delete(p[1])
                        _indexes.append(i)
                        _point_index = p[0]
                else:
                    self.canvas.delete(p[1])
                    _indexes.append(i)
                    _point_index = p[0]
                
                _n += 1

        
        j = 0
        for _i in _indexes:
            self.draw_ids.pop(_i-j)
            j += 1
            
        return _point_index

    def done_editing_points(self):
        self.points_copy = self.points.copy()
        self.repeat_count = 0

    def start_video(self):

        if not self.master.is_video_running:
            return

        start_time = time.time()

        if self.master.is_video_selected and self.master.is_video_running:
            ret, self.frame = self.video.read()
            self.frame_number += 1

            if not ret:
                self.video = cv2.VideoCapture(self.master.filename)
                ret, self.frame = self.video.read()
                self.frame_number = 0
                
                self.points = self.points_copy.copy()

                self.calculate_new_frame(self.frame)
                self.show_image_canvas()
                self.draw_lines()

                self.repeat_count += 1
                if self.repeat_count < 2:
                    self.start_video()
                else:
                    self.repeat_count = 0
                    self.master.is_video_running = False
                    self.master.editbar.start_btn_txt.set('Start')



            else:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                
                for i,p in enumerate(self.points):
                    if p[0] != -10:
                        self.points[i] = PF.track_point(p,self.frame,self.prev_frame)

                self.prev_frame = self.frame

                self.calculate_new_frame(self.frame)
                self.show_image_canvas()
                self.draw_lines()

                tooken_time = int( (time.time()-start_time)*1000 )
                self.master.time_label_msg.set('frame number : {:d}\nprocess time : {:d}ms\nperiod : {:d}ms'.format(self.frame_number,tooken_time,self.interval))
                if self.interval - tooken_time < 0:
                    self.after(1, self.start_video)
                else:
                    self.after(self.interval - tooken_time, self.start_video)
                
        else:
            self.clear_canvas()

    def calculate_new_sizes(self,frame):
        height, width = np.shape(frame)
        ratio = height / width

        self.shown_width = width
        self.shown_height = height

        if height > self.winfo_height() or width > self.winfo_width():
            if ratio < 1:
                self.shown_width = self.winfo_width()
                self.shown_height = int(self.shown_width * ratio)
            else:
                self.shown_height = self.winfo_height()
                self.shown_width = int(self.shown_height * (width / height))  
        self.ratio = height / self.shown_width

    def calculate_new_frame(self,frame):
        self.shown_frame = cv2.resize(frame, (self.shown_width, self.shown_height))
        self.shown_frame = ImageTk.PhotoImage(Image.fromarray(self.shown_frame))

    def show_image_canvas(self):
        self.canvas.config(width=self.shown_width, height=self.shown_height)
        self.canvas.create_image(self.shown_width / 2, self.shown_height / 2, anchor=CENTER, image=self.shown_frame)

    def clear_canvas(self):
        self.master.message.set('pls select a video!')
        self.canvas.delete("all")
    
    def clear_draw(self):
        self.canvas.delete(self.draw_ids)
    
    def do_nothing_func(self,event):
        pass

    def plot_cnn_output(self):
        

        _len = len(self.result_curves_as_images)

        plot_size = []

        if _len<=3:
            plot_size.append(1)
            plot_size.append(_len + 1)
        else:
            plot_size.append(int(_len**0.5)+1)
            plot_size.append(plot_size[0])
        
        plt.subplot(plot_size[0],plot_size[1],1)
        plt.imshow(self.predicted_frame,cmap='gray')
        plt.title('Predicted Image')
        plt.axis(False)
        
        i = 2
        for c in self.result_curves_as_images:
            plt.subplot(plot_size[0],plot_size[1],i)
            plt.imshow(c,cmap='gray')
            plt.title('{:d}th Curve'.format(i-1))
            plt.axis(False)
            # cv2.imwrite('p{:d}.png'.format(i),c)
            i += 1
        
        

        

        plt.show()
