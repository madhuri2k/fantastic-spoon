#!/usr/bin/env python3

# A Simple Application for handling yay0 files

from tkinter import *
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk
import  os, logging
import frontend, lzyf

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

        toolsMenu = Menu(mainMenu)
        toolsMenu.add_command(label="Compress Yay0 file...", command=self.compress_yay0)
        toolsMenu.add_command(label="Compress LZYF file...", command=self.compress_lzyf)
        mainMenu.add_cascade(label="Tools", menu=toolsMenu)
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
    def compress_yay0(self):
        self.textLabel['text'] = "Not Yet Implemented!"
    def compress_lzyf(self):
        file_types = [("Binary File","*.bin"),("All Files","*")]
        f_in = filedialog.askopenfile(master=self, mode="rb",title="Open File",filetypes=file_types)
        self.textLabel.configure(text="Compressing... please wait!")
        self.update()
        if f_in:
            out = lzyf.create_lzyf(f_in.read())
            file_types = [("LZYF File","*.lzyf"),("Binary File","*.bin"),("All Files","*")]
            n = file_types[0][1].replace('*', os.path.splitext(f_in.name)[0], 1)
            print("Initial file {}".format(n))
            f_out = filedialog.asksaveasfile(mode="wb", initialfile=n, title="Save As...", filetypes=file_types)
            if f_out != None:
                f_out.write(out)
                self.textLabel['text'] = "Compressed {} to {}".format(f_in.name, f_out.name)
            else:
                self.textLabel['text'] = "Aborted!"
        else:
            self.textLabel['text'] = "Aborted!"

def main():
    logging.basicConfig(level=logging.INFO)
    root = Tk()
    root.geometry("400x400")
    app = Application(root)
    root.mainloop()

if __name__ == '__main__':
    main()
