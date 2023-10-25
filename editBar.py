import tkinter as tk
from tkinter import Frame, Button
from tkinter import filedialog
import cv2
import matplotlib.pyplot as plt


class EditBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)

        _width = 10

        self.start_btn_txt = tk.StringVar()
        self.start_btn_txt.set('Start')

        self.open_button = Button(self, text="Open Video",width=_width)
        self.open_button.bind("<ButtonRelease>", self.open_button_released)
        self.open_button.grid(column=0,row=0,padx=(5,5),pady=(5,5),columnspan=2)

        
        self.clear_button = Button(self, text="Clear Canvas",width=_width,state="disabled")
        self.clear_button.bind("<ButtonRelease>", self.clear_button_released)
        self.clear_button.grid(column=2,row=0,padx=(5,5),pady=(5,5),columnspan=2)
        
        self.start_button = Button(self, textvariable=self.start_btn_txt,width=_width*2+3,state="disabled")
        self.start_button.bind("<ButtonRelease>", self.start_button_released)
        self.start_button.grid(column=0,row=1,columnspan=4,padx=(5,5),pady=(5,5))

        self.cleat_points_button = Button(self, text="Clear Points",width=_width,state="disabled")
        self.cleat_points_button.bind("<ButtonRelease>", self.cleat_points_button_released)
        self.cleat_points_button.grid(column=0,row=2,padx=(5,5),pady=(5,5),columnspan=2)
        
        self.new_curve_button = Button(self, text="new Curve",width=_width,state="disabled")
        self.new_curve_button.bind("<ButtonRelease>", self.new_curve_button_released)
        self.new_curve_button.grid(column=2,row=2,padx=(5,5),pady=(5,5),columnspan=2)
        
        self.cnn_plot_button = Button(self, text="Plot CNN output",width=_width*2+3,state="disabled")
        self.cnn_plot_button.bind("<ButtonRelease>", self.cnn_plot_button_released)
        self.cnn_plot_button.grid(column=0,row=3,columnspan=4,padx=(5,5),pady=(5,5))

        
    

    def open_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.open_button:
            
            filename = filedialog.askopenfilename()
            if filename != '':
                vid = cv2.VideoCapture(filename)
                if vid is not None:
                    self.clear_button["state"] = "normal"
                    self.start_button["state"] = "normal"
                    self.new_curve_button["state"] = "normal"
                    self.cnn_plot_button["state"] = "normal"
                    self.master.filename = filename
                    self.master.is_video_selected = True
                    self.master.is_video_running = False
                    self.master.time_label_msg.set('')
                    self.master.data_loader.show_video()

    
    def clear_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.clear_button:

            self.master.filename = ""
            self.master.is_video_selected = False
            self.master.is_video_running = False
            self.master.data_loader.show_video()
        
            self.clear_button["state"] = "disabled"
            self.start_button["state"] = "disabled"
            self.cnn_plot_button["state"] = "disabled"
            self.master.time_label_msg.set('')
    
    
    def start_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.start_button:
            if self.master.filename != "":
                if self.master.is_video_running:
                    self.master.is_video_running = False
                    self.start_btn_txt.set('Start')
                else:
                    self.master.is_video_running = True
                    self.start_btn_txt.set('Stop')
                    self.master.data_loader.done_editing_points()
                    self.master.data_loader.start_video()
                
    def cleat_points_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.cleat_points_button:
            self.master.data_loader.clear_point()

          
    def new_curve_button_released(self, event):
        if self.winfo_containing(event.x_root, event.y_root) == self.new_curve_button:
            self.master.data_loader.new_curve()
    
    def cnn_plot_button_released(self,event):
        if self.winfo_containing(event.x_root, event.y_root) == self.cnn_plot_button:
            self.master.data_loader.plot_cnn_output()
            
    def Help_button_released(self,event):
        if self.winfo_containing(event.x_root, event.y_root) == self.Help_button:
            plt.imshow(None)
            plt.show()
    
