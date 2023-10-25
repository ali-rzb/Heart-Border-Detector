import tkinter as tk
from tkinter.constants import LEFT
import webbrowser

from editBar import EditBar
from DataLoader import DataLoader


class Main(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        self.filename = ""
    
        self.video = None
        self.is_video_selected = False
        self.is_video_running = False
        self.message = tk.StringVar()
        self.message.set('pls select a video!')

        self.time_label_msg = tk.StringVar()
        self.message.set('')

        self.title("Heart Tracer")
        
        
        self.data_loader = DataLoader(master=self)
        
        text = tk.Label(master=self,textvariable=self.message, anchor="w", justify=LEFT)
        self.editbar = EditBar(master=self)

        self.time_label = tk.Label(master=self,textvariable=self.time_label_msg, anchor="w", justify=LEFT)

        _hint_text = 'you can drag points or make new points by clicking on the image and delete points by double click on them'

        Hint = tk.Text(width=22,height=7, state='normal', background="#f0f0f0", borderwidth=0)
        Hint.insert(tk.END, _hint_text)
        Hint.configure(state='disabled')

        footer = tk.Label(width=30,text='rzb',fg="#1F487E", cursor="hand2")

        self.data_loader.grid(column=0,row=0,rowspan=7)

        text.grid( column=1, row=0,padx=(10,10))
        self.editbar.grid(column=1 ,row=1)

        # self.pb.grid( column=1, row=2)

        self.time_label.grid( column=1, row=2)
        Hint.grid( column=1, row=3)

        footer.grid( column=1, row=4)
        footer.bind("<Button-1>", lambda e: webbrowser.open_new('http://www.roozbehi.ir'))
    

        