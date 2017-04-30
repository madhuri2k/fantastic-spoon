#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        N64 Image Tool
# Purpose:     Png ex/import for common N64 image types
#
# Author:      Zoinkity
#
# Created:     26/04/2014
# Copyright:   (c) Zoinkity 2014
# Licence:     <unlicenced>
#-------------------------------------------------------------------------------

from collections import namedtuple
_exportcontainer = namedtuple("N2D", ['width', 'height', 'image', 'palette'])
export_pattern = _exportcontainer._make((0, 0, None, None,))

def unpackRGB(data, bitdepth=None, order='rgba', src='rgba'):
    """Converts a bytearray of given bitdepth to given order.
    Returns a bytearray with four channels.
    If input source is an array.array bitdepth is optional."""
    from array import array

    if bitdepth is None:
        if isinstance(data, array):
            bitdepth = data.itemsize<<3
        else:
            raise TypeError("unpackRGB() missing 1 required positional argument: 'bitdepth'")
    order = order.lower()
    src = src.lower()
    # Determine order in terms of indices.
    o = []
    for i in order:
        o.append(src.find(i))
    while len(o)<4:
        o.append(-1)

    out = bytearray()
    if bitdepth==32:
        if order==src:
            return data
        else:
            if isinstance(data, array):
                data = data.tobytes()
            for i in range(0, len(data), 4):
                for j in o:
                    if j>=0:
                        out.append(data[i:i+4][j])
                    else:
                        out.append(0)
    elif bitdepth==24:
        # Set alpha as a placeholder.
        if isinstance(data, array):
            data.byteswap()
            data = data.tobytes()
        for i in range(0, len(data), 3):
            for j in o:
                if j>=0:
                    out.append(data[i:i+3][j])
                else:
                    out.append(0)
    elif bitdepth==16:
        # Unpack into 8bit components
        if isinstance(data, (bytes, bytearray)):
            data = array("H", data)
            data.byteswap()
        for c in data:
            clr = dict(r=0, g=0, b=0, a=0)
            for j in reversed(src):
                if j=='a':
                    clr['a'] = 0xFF if c&1 else 0
                    c>>=1
                else:
                    v = (c&0x1F)<<3
                    v|= v>>5
                    clr[j] = v
                    c>>=5
            for j in order:
                out.append(clr.get(j, 0))
    return out

def packRGB(data, newdepth, srcdepth, order='rgba', src='rgba', **kwargs):
    """Converts a bytearray of channel data to given bitdepth and order.
    Returns a bytearray with merged channels.

    <data> should be a bytes or bytearray object
    <newdepth> is the target bitdepth; must be 16, 24, or 32.
    <srcdepth> is <data>'s bitdepth; must be 16, 24, or 32.
    <order> is the arrangement of channels in the output;
        'a' is ignored in 24bit output
    <order> is the arrangement of channels in <data>;
        'a' is ignored in 24bit input

    optional keywords:
        alpha=<int>  (default 0)
            Sets the alpha value for 24bit conversions.
            <alpha> must be 0-255 for 24->32 bit conversion;
            nonzero alpha sets True for 24->16bit conversions.
    """
    raise NotImplementedError
    from array import array

    order = order.lower()
    src = src.lower()
    if newdepth == srcdepth and order==src:
        return data

    if srcdepth not in (16, 24, 32):
        raise ValueError("Source image have 16, 24, or 32 bit depth.")
    if newdepth not in (16, 24, 32):
        raise ValueError("New depth must be either 16, 24, or 32 bits.")

    # Determine order in terms of indices.
    o = []
    for i in order:
        o.append(src.find(i))
    while len(o)<4:
        o.append(-1)

    out = bytearray()
    if srcdepth==32:
        if newdepth in (24, 32):
            if newdepth == 24:
                o = o.replace('a', '')
            if isinstance(data, array):
                data = data.tobytes()
            for i in range(0, len(data), 4):
                for j in o:
                    if j>=0:
                        out.append(data[i:i+4][j])
                    else:
                        out.append(0)
    elif srcdepth==24:
        if newdepth in (24, 32):
            # Set alpha as a placeholder.
            if isinstance(data, array):
                data.byteswap()
                data = data.tobytes()
            v = kwargs.get(alpha, 0)
            for i in range(0, len(data), 3):
                for j in o:
                    if j>=0:
                        out.append(data[i:i+3][j])
                    else:
                        out.append(0)
    elif srcdepth==16:
        # Unpack into 8bit components
        if isinstance(data, (bytes, bytearray)):
            data = array("H", data)
            data.byteswap()
        for c in data:
            clr = dict(r=0, g=0, b=0, a=0)
            for j in reversed(src):
                if j=='a':
                    if newdepth==24:
                        continue
                    clr['a'] = 0xFF if c&1 else 0
                    c>>=1
                else:
                    v = (c&0x1F)<<3
                    v|= v>>5
                    clr[j] = v
                    c>>=5
            if newdepth==24:
                order = order.replace('a', '')
            for j in order:
                out.append(clr.get(j, 0))
    return out

def redepth(data, org, depth):
    if org == depth:
        return data

    out = bytearray()
    m = (1 << org) - 1
    c = max(org - depth, 0)
    v = 1
    if org > 8 or depth > 8:
        raise NotImplementedError
    else:
        for j in data:
            # Read each sample from bytes data.
            for k in range(8, 0, -org):
                k-=org
                v <<= depth
                j = (j>>k) & m
                v |= j >> c
                if v.bit_length() > 8:
                    out.append(v & 0xFF)
                    v = 1
    return bytes(out)


def splitter(data, mode):
    """If mode ci4:     UL -> 0U 0L
    if mode ia8 or i4:  UL -> UU LL
    if mode ia4:        UUUuLLLl -> UU uu LL ll
    if mode i28:        11223344 -> 11 22 33 44
    if mode i24:        11223344 -> 12 34
    """
    out = bytearray()
    if mode in ('ia8', 'i4'):
        for i in data:
            g = (i>>4) | (i&0xF0)
            out.append(g)
            g = i&0xF
            out.append(g | (g<<4))
    elif mode == 'ci4':
        for i in data:
            out.append(i>>4)
            out.append(i&0xF)
    elif mode == 'ia4':
        # 3bit grey, 1 bit alpha.
        for i in data:
            for g in (i>>4, i&0xF):
                a = 0xFF if g&1 else 0
                g&= (~1)
                g|= g<<4
                out.append(g)
                out.append(a)
    elif mode == 'i24':
         for i in data:
             a = (i>>6) & 3
             b = (i>>4) & 3
             c = (i>>2) & 3
             d = (a<<12) | (b<<8) | (c<<4) | (i&3)
             d|= d<<2
             out.extend(d.to_bytes(2, byteorder='big'))
    elif mode == 'i28':
         for i in data:
             a = (i>>6) & 3
             b = (i>>4) & 3
             c = (i>>2) & 3
             d = (a<<24) | (b<<16) | (c<<8) | (i&3)
             d|= d<<4
             d|= d<<8
             out.extend(d.to_bytes(4, byteorder='big'))
    else:
        return data
    return bytes(out)

def _nibbler(v):
    return ((v>>4) | (v<<4)) & 0xFF
def nibbleswap(data):
    return bytes(i for i in map(_nibbler, data))

def pal32to16(pal, swap=False):
    """Maps c32to16 to entire palette provided."""
    import struct
    p = list()
    for i in range(0, len(pal), 4):
        r = pal[i]>>3
        g = pal[i+1]>>3
        b = pal[i+2]>>3
        a = pal[i+3]>>7
        p.append((r<<11)|(g<<6)|(b<<1)|a)
    return struct.pack(">{:d}{}".format(len(p), 'h' if swap else 'H'), *p)

def deinterlace(data, height):
    from array import array
    a = array("L", data)
    l = len(a)//height
    for j in range(1,height,2):
        for k in range(l*j, l*(j+1), 2):
            b = a[k]
            a[k] = a[k+1]
            a[k+1]= b
    return a.tobytes()

def img(func, mode, **kwargs):
    """Converts images and binaries in the format specified by func.
    Mode should be either "out" for export or "imp" for import.
    Acceptable types for func:
        "png"   requires the pypng module

    provide either:
        cmd        string name of format; same as operation
    or:
        frmt       image format index or string code
        depth      image depth

    Arguments for input types:
    img      (req) image filename or a bytes-like object
    pad      (opt) ci images: adds additional entries when palette
        has fewer than the maximum for that type

    Arguments for output types:
    img      (req) image as a bytes object
    pal      (req) palette as a bytes object for required types
    width    (req) width of image
    name     (req) output filename, hopefully with .png extension
    alpha    (opt) ci images: output with or without alpha channel
        default is True
    order    (opt) c/ci images: sets order of channels
        default is 'rgba'
    compress (opt) compression level
        default is 9

    Format and depth use microcode typecodes:
        formats:
            0   'c'     color
            1   'yuv'   yuv
            2   'ci'    indexed
            3   'ia'    intensity-alpha
            4   'i'     intensity
        depths:
            0   4 bit
            1   8 bit
            2   16bit
            3   32bit
    """
    import sys
    if mode not in ('out', 'imp'):
        raise ValueError("Mode must be either 'out' or 'imp'.")
##    f = sys.modules.get('N64img', None)
##    if f is None:
##        f = sys.modules.get('__main__')
##    if f is None:
##        raise ValueError("Unable to retrieve module name.")
##    kwargs.update({'func':getattr(f, func+mode)})
    kwargs.update({'func':globals().get(func+mode)})
    return __funcredir(**kwargs)

def __funcredir(**kwargs):
    func = kwargs.get('func')
    #TODO: this became necessary when the rest of it got fudged.
    if 'cmd' in kwargs:
        i = kwargs.get('cmd')
    elif 'frmt' in kwargs and 'depth' in kwargs:
        # This maps functions to handle standard types.
        # As more support added, stick the functions here.
        frmt = kwargs.get('frmt', -1)
        if isinstance(frmt, str):
            frmt = ('c', 'yuv', 'ci', 'ia', 'i').index(frmt)
        depth= kwargs.get('depth',-1)
        i = (('ni',  'ni',  'c16', 'c32'),
             ('ni',  'ni',  'ni',  'ni'),
             ('ci4', 'ci8', 'ni',  'ni'),
             ('ia4', 'ia8', 'ia16','ni'),
             ('i4',  'i8',  'i16', 'ni'),)[frmt][depth]
    else:
        raise ValueError("You must provide either 'cmd' or 'frmt'+'depth'.")
    # Call function out of class or use NotImplemented.
    try:
        cmd = func().__getattribute__(i)
    except AttributeError:
        cmd = func.ni
    return cmd(**kwargs)

# The class only exists as a wrapper here.
class pngout:
    """Container class for image output types.
    All have the same interface.  You must provide:
        img     image as a bytes-like object
        width   width of image as an int
        name    output filename
    Indexed types also require a palette:
        pal     palette as a bytes-like object

    Optional keywords:
            'compress'   0-9 (default 9): compression level for output png
            'height'     default size//width: sets given image height
            'interlaced' default False: if True deinterlaces image, padding to block size as required
    Individual methods have additional optional keyword fields.
        Refer to the method docstrings for more details."""

    @staticmethod
    def c16(img, width, name, **kwargs):
        """Optional keywords:
            'order'      default 'rgba': sets the order of channels in output
            'src'        default 'rgba': sets the order of channels in source
            'alpha'      default True:   if False outputs flattened 24bit image
        """
        import png
        alf = kwargs.get('alpha', True)
        der = kwargs.get('order', 'rgba').lower()
        if not alf:
            der = der.replace('a','')
        h = kwargs.get('height', (len(img)>>1)//width)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        o= unpackRGB(img, 16, der, kwargs.get('src', 'rgba').lower()) # bytearray of 32bit colors from 16bit, in rgba order
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, alpha=alf, compression=kwargs.get('compress', 9), interlace=kwargs.get('interlace', False), gamma=kwargs.get('gamma', None))
            i.write_array(f, o)

    @staticmethod
    def c32(img, width, name, **kwargs):
        """Optional keywords:
            'order'     default 'rgba': sets the order of channels in output
            'src'       default 'rgba': sets the order of channels in source
            'alpha'     default True:   if False outputs flattened 24bit image
        """
        import png
        alf = kwargs.get('alpha', True)
        der = kwargs.get('order', 'rgba').lower()
        if not alf:
            der = der.replace('a','')
        h = kwargs.get('height', (len(img)//width)>>2)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        o= unpackRGB(img, 32, der, kwargs.get('src', 'rgba').lower()) # bytearray of 32bit colors from 16bit, in rgba order
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, alpha=alf, compression=kwargs.get('compress', 9))
            i.write_array(f, o)

    @staticmethod
    def ci4(img, pal, width, name, **kwargs):
        """Optional keywords:
            'order'      default 'rgba': sets the order of channels in output
            'src'        default 'rgba': sets the order of channels in source
            'alpha'      default True: if False treats input as a 15bit image
            'nibbleswap' default False: swaps order of nibbles
        """
        import png
        alf = kwargs.get('alpha', True)
        der = kwargs.get('order', 'rgba').lower()
        if not alf:
            der = der.replace('a','')
        p = unpackRGB(pal, 16, der, kwargs.get('src', 'rgba').lower())
        if alf:
            p = zip(*[iter(p)]*4)
        else:
            p = zip(*[iter(p)]*3)
##            p = zip(p[::4], p[1::4], p[2::4])
        if kwargs.get('nibbleswap', False):
            img = nibbleswap(img)
        w = (width+1)>>1
        h = kwargs.get('height', len(img) // w)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, bitdepth=4, palette=p, compression=kwargs.get('compress', 9))
            i.write_packed(f, [img[i:i+w] for i in range(0,len(img),w)])

    @staticmethod
    def ci8(img, pal, width, name, **kwargs):
        """Optional keywords:
            'order'     default 'rgba': sets the order of channels in output
            'src'       default 'rgba': sets the order of channels in source
            'alpha'     default True: if False treats input as a 15bit image
        """
        import png
        alf = kwargs.get('alpha', True)
        der = kwargs.get('order', 'rgba').lower()
        if not alf:
            der = der.replace('a','')
        p= unpackRGB(pal, 16, der, kwargs.get('src', 'rgba').lower()) # bytearray of 32bit colors from 16bit, in rgba order
        if alf:
            p = zip(*[iter(p)]*4)
        else:
            p = zip(*[iter(p)]*3)
##            p = zip(p[::4], p[1::4], p[2::4])
        h = kwargs.get('height', len(img)//width)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        with open(name, 'wb') as f:
            i = png.Writer(width=width, height=h, bitdepth=8, palette=p, compression=kwargs.get('compress', 9))
            i.write_array(f, img)

    @staticmethod
    def ia4(img, width, name, **kwargs):
        """Optional keywords:
            'nibbleswap'    default False: swaps order of nibbles
        """
        import png
        if kwargs.get('nibbleswap', False):
            img = nibbleswap(img)
        w = (width+1)>>1
        h = kwargs.get('height', len(img)//w)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        o = splitter(img, 'ia4') # bytearray of 8bit IA values
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, alpha=True, greyscale=True, compression=kwargs.get('compress', 9))
            i.write_array(f, o)

    @staticmethod
    def ia8(img, width, name, **kwargs):
        """Optional keywords:
            None
        """
        import png
        h = kwargs.get('height', len(img)//width)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        o = splitter(img, 'ia8') # bytearray of 8bit IA values
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, alpha=True, greyscale=True, compression=kwargs.get('compress', 9))
            i.write_array(f, o)

    @staticmethod
    def ia16(img, width, name, **kwargs):
        """Optional keywords:
            None
        """
        import png
        h = kwargs.get('height', (len(img)//width)>>1)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, alpha=True, greyscale=True, compression=kwargs.get('compress', 9))
            i.write_array(f, img)

    @staticmethod
    def i1(img, width, name, **kwargs):
        """Optional keywords:
            'swap'      default False: 32bit byteswaps input
        """
        import png
        # Do you need to byteswap words before using this?
        w = (width+1)>>3
        h = kwargs.get('height', len(img) // w)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        if kwargs.get('swap', False):
            from array import array
            a = array("L", img+bytes(len(img)&3))
            a.byteswap()
            img = a.tobytes()
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, bitdepth=1, greyscale=True, compression=kwargs.get('compress', 9))
            i.write_packed(f, [img[i:i+w] for i in range(0,len(img),w)])

    @staticmethod
    def i2(img, width, name, **kwargs):
        """Optional keywords:
            'swap'      default False: 32bit byteswaps input
        """
        import png
        # Do you need to byteswap words before using this?
        if kwargs.get('swap', False):
            from array import array
            a = array("L", img+bytes(len(img)&3))
            a.byteswap()
            img = a.tobytes()
        w = (width+1)>>2
        h = kwargs.get('height', len(img) // w)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, bitdepth=2, greyscale=True, compression=kwargs.get('compress', 9))
            i.write_packed(f, [img[i:i+w] for i in range(0,len(img),w)])

    @staticmethod
    def i4(img, width, name, **kwargs):
        """Optional keywords:
            'nibbleswap'    default False: swaps order of nibbles
        """
        import png
        if kwargs.get('nibbleswap', False):
            img = nibbleswap(img)
        w = (width+1)>>1
        h = kwargs.get('height', len(img) // w)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, bitdepth=4, greyscale=True, compression=kwargs.get('compress', 9))
            i.write_packed(f, [img[i:i+w] for i in range(0,len(img),w)])

    @staticmethod
    def i8(img, width, name, **kwargs):
        """Optional keywords:
            None
        """
        import png
        h = kwargs.get('height', len(img)//width)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, bitdepth=8, greyscale=True, compression=kwargs.get('compress', 9))
            i.write_array(f, img)

    @staticmethod
    def i16(img, width, name, **kwargs):
        """Optional keywords:
            None
        """
        import png
        h = kwargs.get('height',(len(img)//width)>>1)
        if kwargs.get('interlaced', False):
            img = deinterlace(img, h)
        with open(name, 'wb') as f:
            i= png.Writer(width=width, height=h, bitdepth=16, greyscale=True, compression=kwargs.get('compress', 9))
            i.write_array(f, img)

    @staticmethod
    def GBi2(img, width, name, **kwargs):
        """GameBoy i2 format, used in N64 titles implementing the GB emu.
        Optional keywords:
            None
        """
        ##TODO: implement optional palette field
        import png
        o = []
        for n in range(0,len(img),2):
             i, j =img[n], img[n+1]
             for x in range(8):
                 o.append(((i&0x80)>0) | (((j&0x80)>0)<<1))
                 i<<=1
                 j<<=1;
        h = kwargs.get('height', len(o)//width)
        with open(name, 'wb') as f:
             i= png.Writer(width=width, height=h, greyscale=True, alpha=False, bitdepth=2, compression=kwargs.get('compress', 9))
             i.write_array(f, o)

    @staticmethod
    def ni(**kwargs):
        raise NotImplementedError


class pngimp():
    """Container class for image output types.
    All have the same interface.  You must provide either a filename
      bytes, or bytearray object.
    Each function returns:
        width   width of image as an int
        height  height of image as an int
        img     image as a bytes-like object
    Indexed types also return:
        pal     palette as a bytes-like object

    Refer to each functions' docstrings on what input images are valid.
    """

    @staticmethod
    def c16(img, **kwargs):
        """Returns (width, height, c32).
        <img> may be either a filename (str), bytes, or bytearray object.
        Most .png formats should be compatible.
        """
        r = pngimp.c32(img, **kwargs)
        return r._replace(image=pal32to16(r.image))

    @staticmethod
    def c32(img, **kwargs):
        """Returns (width, height, c32).
        <img> may be either a filename (str), bytes, or bytearray object.
        Most .png formats should be compatible.
        """
        import png
        # They test for bytes via isarray(), which throws an exception in 3.x.
        if isinstance(img, (bytes, bytearray)):
            p = png.Reader(bytes=img)
        else:
            p = png.Reader(img)

        w, h, i, m = p.asRGBA8()
        return export_pattern._replace(width=w, height=h, image=b''.join(i))

    @staticmethod
    def ci4(img, **kwargs):
        """Returns (width, height, ci4, palette).
        <img> may be either a filename (str), bytes, or bytearray object.
        Input .png must be a paletted type and can not have more than 16 colors.

        Optional keywords:
            'pad'      default False: adds additional entries when palette has fewer than 16 colors."""
        import png
        from itertools import chain
        # They test for bytes via isarray(), which throws an exception in 3.x.
        if isinstance(img, (bytes, bytearray)):
            p = png.Reader(bytes=img)
        else:
            p = png.Reader(img)

        p.preamble()
        if not p.colormap:
            raise TypeError("Image must contain a palette.")
        pal = p.palette(alpha='force')
        npal = len(pal)
        if npal > 16:
            raise TypeError("Image must have no more than 16 colors in its palette.")

        w, h, i, m = _png_Reader_read_serial(p)
        d = m.get('bitdepth',4)
        if d not in (1, 2, 4, 8):
            raise TypeError("Only paletted images with bitdepths 1, 2, 4, or 8 are currently supported.")
        i = b''.join(i)
        if d != 4:
            img = bytearray()
            if d == 1:
                for j in i:
                    for k in range(4):
                        x = (j & 0x80) >> 3
                        y = (j & 0x40) >> 6
                        img.append(x | y)
                        j<<=2
            elif d == 2:
                for j in i:
                    v = (j & 0xCC) >> 2
                    j &= 0x33
                    img.append((v & 0x30) | j>>4)
                    img.append(((v << 4) & 0x30) | (j & 7))
            elif d == 8:
                for j in range(0, len(i), 2):
                    img.append((j[0]<<4) | j[1])
            i = bytes(img)

        pal = pal32to16(list(chain(*pal)))
        if kwargs.get('clean', False):
            # TODO: create a translation table for image
            # mapping later instances of identical colors to previous ones.  Byteorder doesn't matter.
            pass
        if kwargs.get('pad', False):
            pal = b''.join((pal, bytes(32-len(pal))))

        return export_pattern._replace(width=w, height=h, image=i, palette=pal)

    @staticmethod
    def ci8(img, **kwargs):
        """Returns (width, height, ci4, palette).
        <img> may be either a filename (str), bytes, or bytearray object.
        Input .png must be a paletted type and can not have more than 256 colors.

        Optional keywords:
            'pad'      default False: adds additional entries when palette has fewer than 256 colors."""
        import png
        from itertools import chain
        # They test for bytes via isarray(), which throws an exception in 3.x.
        if isinstance(img, (bytes, bytearray)):
            p = png.Reader(bytes=img)
        else:
            p = png.Reader(img)

        p.preamble()
        if not p.colormap:
            raise TypeError("Image must contain a palette.")
        pal = p.palette(alpha='force')
        npal = len(pal)
        if npal > 256:
            raise TypeError("Image must have no more than 256 colors in its palette.")

        w, h, i, m = _png_Reader_read_serial(p)
        d = m.get('bitdepth',8)
        if d not in (1, 2, 4, 8):
            raise TypeError("Only paletted images with bitdepths 1, 2, 4, or 8 are currently supported.")
        i = b''.join(i)
        if d != 8:
            out = bytearray()
            m = (1 << d) - 1
            for j in i:
                for k in range(8, 0, -d):
                    k-=d
                    out.append((j>>k) & m)
            i = bytes(out)

        pal = pal32to16(list(chain(*pal)))
        if kwargs.get('clean', False):
            # Experimental: create a translation table for image
            # mapping later instances of identical colors to previous ones.  Byteorder doesn't matter.
            from array import array
            a = array("H", pal)
            p = array("H")
            t = bytearray(range(256))
            for c,j in enumerate(a):
                if j in p:
                    t[c] = p.index(j)
                else:
                    t[c] = len(p)
                    p.append(j)
            pal = p.tobytes()
            i = i.translate(t)
        if kwargs.get('pad', False):
            pal = b''.join((pal, bytes(512-len(pal))))

        return export_pattern._replace(width=w, height=h, image=i, palette=pal)

    @staticmethod
    def i4(img, **kwargs):
        """Returns (width, height, ci4, palette).
        <img> may be either a filename (str), bytes, or bytearray object.
        Input .png must be a greyscale type.
        """
        import png
        # They test for bytes via isarray(), which throws an exception in 3.x.
        if isinstance(img, (bytes, bytearray)):
            p = png.Reader(bytes=img)
        else:
            p = png.Reader(img)

        p.preamble()
        if not p.greyscale:
            raise TypeError("Image must be greyscale.")
        d = p.bitdepth
        if d not in (1, 2, 4, 8):
            raise TypeError("Only greyscale images with bitdepths 1, 2, 4, or 8 are currently supported.")

        w, h, i, m = _png_Reader_read_serial(p)
        i = b''.join(i)
        if d != 4:
            img = bytearray()
            if d == 1:
                for j in i:
                    for k in range(4):
                        x = (j & 0x80) >> 3
                        y = (j & 0x40) >> 6
                        img.append(x | y)
                        j<<=2
            elif d == 2:
                for j in i:
                    v = (j & 0xCC) >> 2
                    j &= 0x33
                    img.append((v & 0x30) | j>>4)
                    img.append(((v << 4) & 0x30) | (j & 7))
            elif d == 8:
                for j in range(0, len(i), 2):
                    img.append((j[0]<<4) | j[1])
            i = bytes(img)

        return export_pattern._replace(width=w, height=h, image=i)

    @staticmethod
    def i8(img, **kwargs):
        """Returns (width, height, ci4, palette).
        <img> may be either a filename (str), bytes, or bytearray object.
        Input .png must be a greyscale type.
        """
        import png
        # They test for bytes via isarray(), which throws an exception in 3.x.
        if isinstance(img, (bytes, bytearray)):
            p = png.Reader(bytes=img)
        else:
            p = png.Reader(img)

        p.preamble()
        if not p.greyscale:
            raise TypeError("Image must be greyscale.")
        d = p.bitdepth
        if d not in (1, 2, 4, 8):
            raise TypeError("Only greyscale images with bitdepths 1, 2, 4, or 8 are currently supported.")

        w, h, i, m = _png_Reader_read_serial(p)
        i = b''.join(i)
        if d != 8:
            out = bytearray()
            m = (1 << d) - 1
            for j in i:
                for k in range(8, 0, -d):
                    k-=d
                    out.append((j>>k) & m)
            i = bytes(out)

        return export_pattern._replace(width=w, height=h, image=i)

    @staticmethod
    def ni(**kwargs):
        raise NotImplementedError

def _png_Reader_read_serial(src, lenient=False, deinterlace=False):
    """Variation of png.Reader.read() that returns the serialized
    image as a bytes object
    Returns (width, height, image, meta).
    Image is a generator outputing individual scanlines;
        you can use b''.join(image) to get a proper bytes object.

    This could be monkeypatched in, but meh."""
    import png
    import warnings
    import zlib

    src.preamble(lenient=lenient)
    raw = []
    d = zlib.decompressobj()
    r = None
    while True:
        try:
            kind, data = src.chunk(lenient=lenient)
        except ValueError as e:
            raise png.ChunkError(e.args[0])
        # Seems different pypng versions expect bytes or str.
        if kind in ('IEND', b'IEND'):
            # http://www.w3.org/TR/PNG/#11IEND
            break
        if kind not in ('IDAT', b'IDAT'):
            continue
        # kind == b'IDAT'
        # http://www.w3.org/TR/PNG/#11IDAT
        if src.colormap and not src.plte:
            warnings.warn("PLTE chunk is required before IDAT chunk")
        if r is None:
            r = bytearray(d.decompress(data))
        else:
            r.extend(d.decompress(data))
        while d.unconsumed_tail:
            r.extend(d.decompress(d.unconsumed_tail))
        if d.eof:
            raw.append(r)
            r = None

    meta = dict()
    for attr in 'greyscale alpha planes bitdepth interlace'.split():
        meta[attr] = getattr(src, attr)
    meta['size'] = (src.width, src.height)
    for attr in 'gamma transparent background'.split():
        a = getattr(src, attr, None)
        if a is not None:
            meta[attr] = a
    if src.plte:
        meta['palette'] = src.palette()
    return src.width, src.height, src.deinterlace(raw) if deinterlace else src.iterstraight(raw), meta

def main():
    pass

if __name__ == '__main__':
    main()
