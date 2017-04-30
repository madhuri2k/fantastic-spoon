# A frontend for yay0 decoder

import os
import yay0
import N64img
import tempfile

def parseFilename(fileName):
    # Ignore any leading directory paths
    fileName = os.path.basename(fileName)
    ext = os.path.splitext(fileName)[-1][1:]
    title, dimensions = (os.path.splitext(fileName)[-2]).split('.')
    width, height = dimensions.split('x')
    width = int(width)
    height = int(height)
    return (title, dimensions, width, height, ext)

def getPaletteFileName(fn):
    """
    Return the palette file name. Assumes the palette file is located in the
    same directory with extension .pal and same file title but without
    dimensions.
    """
    dirname = os.path.dirname(fn)
    title = parseFilename(fn)[0]
    return os.path.join(dirname,title+".pal")

def getPngFileName(fn):
    (title, dim, w, h, ext) = parseFilename(fn)
    return title+"."+dim+".png"

def process(fn):
    paletteFormats = [ "ci4", "ci8"]

    with open(fn, "rb") as imageFile:
        imagedata = imageFile.read()

	# Check for header and decompress if necessary
    if(b"Yay0" == imagedata[:0x04]):
        print ("Yay!!! Found yay0")
        imagedata = yay0.yay0Dec(imagedata)
        
    (title, dim, w, h, ext) = parseFilename(fn)
    if(ext in paletteFormats):
        pfn = getPaletteFileName(fn)
        print("Opening palette file", pfn)
        with open(pfn, "rb") as palFile:
            paldata = palFile.read()
    else:
        paldata = None

    # Convert to PNG
    fd,tmpFilePath = tempfile.mkstemp()
    os.close(fd)
    N64img.img('png', 'out', cmd=ext, img=imagedata, pal=paldata,
               width=w, height=h, name=tmpFilePath)
    return tmpFilePath

def main():
    infilename = "game_over.256x32.ci8"
    tmpfilename = process(infilename)
    outfilename = getPngFileName(infilename)
    os.rename(tmpfilename, outfilename)

if __name__ == '__main__':
    main()
