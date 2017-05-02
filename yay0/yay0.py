# This module is for handling yay0 compressed data, usually images.
# Based on:
#	https://github.com/pho/WindViewer/wiki/Yaz0-and-Yay0
#	http://hitmen.c02.at/files/yagcd/yagcd/chap16.html#sec16.1
#	(Yaz0 doc) http://wiki.tockdom.com/wiki/YAZ0_(File_Format)

import struct


# Yay0 decoder
# A basic yay0 decompressor

def yay0Dec(data):
	"""
	data	A stream of bytes
	"""
	print("Data:", len(data), "bytes. Preamble:", data[0:4])
	# data[4:8] has a 32-bit big-endian integer representing the uncompressed size
	decoded_size = struct.unpack(">I", data[0x04:0x08])[0]
	print ("Determined decoded size: ", decoded_size)

	# initialize bytesarray of size decoded_size to hold uncompressed data
	dest = bytearray(decoded_size)
	print("Created dest:", len(dest), "bytes.")

	# o_lt = Offset to Link Table
	o_lt = struct.unpack(">I", data[0x08:0x0c])[0]
	o_mt_max = o_lt
	# o_bccm = Offset to byte chunks and count modifiers
	o_bccm = struct.unpack(">I", data[0x0c:0x10])[0]
	print ("Link table at", o_lt, "bytes and byte-chunks etc starting at", o_bccm, "bytes.")

	# o_mt = Offset to mask table
	o_mt = 0x10

	# o_dest = Offset into destination bytesarray
	o_dest = 0

	while(o_dest < decoded_size):
		mask = struct.unpack(">I", data[o_mt:o_mt+0x04])[0]
		mask_count = 32
		print("Mask:", bin(mask), hex(mask), "at", o_mt)
		o_mt += 4
		print("Moved o_mt to", o_mt)
		while (mask_count > 0) and (o_dest < decoded_size):
		    if (0x80000000 & mask) != 0:
		        # copy 1 byte from source to dest
		        print(mask_count, ": Unlinked Block. o_dest", o_dest, "(/", len(dest), ") o_bccm", o_bccm, "(/", len(data), ")")
		        dest[o_dest] = data[o_bccm]
		        o_dest += 1
		        o_bccm += 1
		    else:
		        cnd = struct.unpack(">H", data[o_lt:o_lt+2])[0]
		        o_lt += 2
		        distance = cnd & 0xfff
		        count = cnd >> 12 
		        if count == 0:
		            count = data[o_bccm] + 18
		            o_bccm += 1
		        else:
		            count += 2
		        # Subtract 1 to correct for semantic of offset, o_dest is next byte to write, whereas distance is from last byte written
		        o_dest_cp = o_dest - distance - 1 
		        print(mask_count, ": Linked Block. Copy", count, "bytes from", 
		              o_dest_cp, "to", o_dest, "at size", len(dest))
		        # dest[o_dest:o_dest+count] = dest[o_dest_cp:o_dest_cp+count]
		        # o_dest += count
		        for r in range(count):
		        	dest[o_dest] = dest[o_dest_cp]
		        	o_dest += 1
		        	o_dest_cp += 1

		    mask = mask << 1
		    mask_count -= 1
		    print("With o_mt", o_mt, "o_lt", o_lt, "o_bccm", o_bccm, 
		          "o_dest", o_dest, "mask", mask, "mask_count", mask_count)
		print(mask_count, ":Getting next mask")
	print("Done with o_dest at", o_dest)
	return dest

def main():
	infilename = "game_over.256x32.ci8y"
	outfilename = "game_over.256x32.raw"
	with open(infilename, "rb") as in_file:
	    data = in_file.read()

	print(data[:4])
	#Check for header
	if(b"Yay0" == data[:0x04]):
	    print ("Yay!!! Found yay0")
	    raw = yay0Dec(data)
	    with open(outfilename, "wb") as out_file:
	    	out_file.write(raw)
	    print ("Decoded.")

if __name__ == '__main__':
	main()

