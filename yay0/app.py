#!/usr/bin/env python3

# A Simple Application for handling yay0 files

from tkinter import *
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk
import frontend
import os

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.prepare()
        self.infilename = ''
        self.tmpfilename = "game_over.256x32.png"
    def prepare(self):
        self.master.title("Application Utility")
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

        editMenu = Menu(mainMenu)
        editMenu.add_command(label="Show Image", command=self.show_image)
        editMenu.add_command(label="Show Text", command=self.show_text)
        mainMenu.add_cascade(label="Edit", menu=editMenu)
    def image_decode(self):
        self.tmpfilename = frontend.process(self.infilename)
        if(self.tmpfilename == ''):
            self.textLabel['text'] = "Image Decode Failed!"
        else:
            self.textLabel['text'] = "Image Decoded Successfully!"
    def open_file(self):
        self.infilename = filedialog.askopenfilename()
        print("Selected:", self.infilename)
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

root = Tk()
root.geometry("400x300")
app = Application(root)
root.mainloop()
