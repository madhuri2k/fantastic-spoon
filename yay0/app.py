#!/usr/bin/env python3

# A Simple Application for handling yay0 files

from tkinter import *
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk
import  os, logging
import frontend

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.appName = "Application Utility"
        self.infilename = ''
        self.tmpfilename = "game_over.256x32.png"
        self.log = logging.getLogger(self.appName)
        self.prepare()
    def prepare(self):
        self.master.title(self.appName)
        self.pack(fill=BOTH, expand=1)
        quitButton = Button(self, text="Decode",
            command=self.image_decode)
        quitButton.place(x=0, y=0)
        self.textLabel = Label(self, text="Ready!")
        self.textLabel.place(x=0, y=50)
        self.imgLabel = Label(self, image=None)
        self.imgLabel.place(x=0, y=100)

        mainMenu = Menu(self.master)
        self.master.config(menu=mainMenu)

        fileMenu = Menu(mainMenu)
        fileMenu.add_command(label="Open...", command=self.open_file)
        fileMenu.add_command(label="Save PNG", command = self.save_file)
        fileMenu.add_command(label="Exit", command=self.app_exit)
        mainMenu.add_cascade(label="File", menu=fileMenu)

        viewMenu = Menu(mainMenu)
        viewMenu.add_command(label="Show Image", command=self.show_image)
        viewMenu.add_command(label="Show Text", command=self.show_text)
        mainMenu.add_cascade(label="View", menu=viewMenu)
    def image_decode(self):
        self.tmpfilename = ''
        ext = frontend.parseFilename(self.infilename)[-1]
        # If file extension ends in y it's pixel data only with a
        # separate palette file containing palette information.
        if 'y' == ext[-1]:
            self.tmpfilename = frontend.processMultiFileImage(self.infilename)
        else:
            self.tmpfilename = frontend.processSingleFileImage(self.infilename)
        if(self.tmpfilename == ''):
            self.textLabel['text'] = "Image Decode Failed!"
        else:
            self.textLabel['text'] = "Image Decoded Successfully!"
    def open_file(self):
        self.infilename = filedialog.askopenfilename()
        self.log.info(("Selected: %s" % self.infilename))
        self.textLabel['text'] = "Opened:"+self.infilename
    def save_file(self):
        self.outfilename = frontend.getPngFileName(self.infilename)
        os.rename(self.tmpfilename, self.outfilename)
        self.textLabel['text'] = "Saved:" + self.outfilename
    def app_exit(self):
        exit()
    def show_image(self):
        load = Image.open(self.tmpfilename) # TODO: Modify this !!!
        render = ImageTk.PhotoImage(load)
        # self.imgLabel = Label(self, image=render)
        self.imgLabel.configure(image=render)
        self.imgLabel.image = render
        # self.imgLabel.configure(image=render)
        # self.imgLabel.place(x=0, y=100)
    def show_text(self):
        self.textLabel['text'] = "Image Displayed!"

logging.basicConfig(level=logging.INFO)
root = Tk()
root.geometry("400x400")
app = Application(root)
root.mainloop()
