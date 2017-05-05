# This module is for handling yay0 compressed data, usually images.
# Based on:
#    https://github.com/pho/WindViewer/wiki/Yaz0-and-Yay0
#    http://hitmen.c02.at/files/yagcd/yagcd/chap16.html#sec16.1
#    (Yaz0 doc) http://wiki.tockdom.com/wiki/YAZ0_(File_Format)

import struct, logging

log = logging.getLogger("yay0")

# Yay0 decoder
# A basic yay0 decompressor
def yay0Dec(data):
    """
    data    A stream of bytes
    """
    log.debug("Data: {} bytes. Preamble: {}".format(len(data),data[0:4]))
    # data[4:8] has a 32-bit big-endian integer representing the uncompressed size
    decoded_size = struct.unpack(">I", data[0x04:0x08])[0]
    log.debug ("Determined decoded size: {}".format(decoded_size))

    # initialize bytesarray of size decoded_size to hold uncompressed data
    dest = bytearray(decoded_size)
    log.info("Created dest: {} bytes.".format(len(dest)))

    # o_lt = Offset to Link Table
    o_lt = struct.unpack(">I", data[0x08:0x0c])[0]
    o_mt_max = o_lt
    # o_bccm = Offset to byte chunks and count modifiers
    o_bccm = struct.unpack(">I", data[0x0c:0x10])[0]
    log.debug ("Link table at {} bytes and byte-chunks etc starting at {} bytes.".format(o_lt, o_bccm))

    # o_mt = Offset to mask table
    o_mt = 0x10

    # o_dest = Offset into destination bytesarray
    o_dest = 0

    while(o_dest < decoded_size):
        mask = struct.unpack(">I", data[o_mt:o_mt+0x04])[0]
        mask_count = 32
        log.debug("Mask: {} {} at {}".format(bin(mask), hex(mask), o_mt))
        o_mt += 4
        log.debug("Moved o_mt to {}".format(o_mt))
        while (mask_count > 0) and (o_dest < decoded_size):
            if (0x80000000 & mask) != 0:
                # copy 1 byte from source to dest
                # log.debug(mask_count, ": Unlinked Block. o_dest", o_dest, "(/", len(dest), ") o_bccm", o_bccm, "(/", len(data), ")")
                log.debug("{}: Unlinked Block. o_dest {}/{} o_bccm {}/{}".format(mask_count, o_dest, len(dest), o_bccm, len(data)))
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
                # log.debug(mask_count, ": Linked Block. Copy", count, "bytes from",
                #       o_dest_cp, "to", o_dest, "at size", len(dest))
                log.debug("{}: Linked Block. Copy {} bytes from {} to {} at size {}".format(mask_count, count, o_dest_cp,  o_dest, len(dest)))
                # dest[o_dest:o_dest+count] = dest[o_dest_cp:o_dest_cp+count]
                # o_dest += count
                for r in range(count):
                    dest[o_dest] = dest[o_dest_cp]
                    o_dest += 1
                    o_dest_cp += 1
            mask = mask << 1
            mask_count -= 1
            # log.debug("With o_mt", o_mt, "o_lt", o_lt, "o_bccm", o_bccm,
            #       "o_dest", o_dest, "mask", mask, "mask_count", mask_count)
            log.debug("With o_mt {} o_lt {} o_bccm {} o_dest {} mask {} mask_count {}".format(o_mt, o_lt, o_bccm, o_dest, mask, mask_count))
        log.debug("{} :Getting next mask".format(mask_count))
    log.info("Done decoding to {} bytes.".format(o_dest))
    return dest

def checkRunlength(index, size, src, maxOffset, maxLength):
    """
    Returns starting position in source before index from where a max run is detected.
    """
    if (index>=size) or (size != len(src)):
        log.warn("Illegal index: {} or size: {} vs {}.".format(index, size, len(src)))
        return -1
    startPos = max(0, index-maxOffset)
    runs = {}
    while(startPos < index):
        # log.debug("With: {} {} Runs: {}".format(startPos, index, runs))
        currRun = 0
        pos = startPos
        while src[pos] == src[index+currRun]:
            currRun += 1
            pos += 1
            if currRun == maxLength:
                log.debug("Found run of length {} == {}. Returning...".format(currRun, maxLength))
                return (startPos, maxLength); #found best possible run
            if (pos >= size) or ((index+currRun) >= size):
                break
        if (currRun > 0) and (currRun not in runs.keys()):
            runs[currRun] = startPos
            # log.debug("Result: {} Runs: {}".format(currRun, runs))
        startPos += 1

    if not runs:
        log.debug("No suitable runs found.")
        return (-1, 0)
    else:
        # Return the index from where the longest run was found
        return (runs[max(runs.keys())], max(runs.keys()))

def yay0Enc(data):
    """
    data    a stream of bytes containing data to be compressed
    """
    maxOffset = 4096
    maxRunLength = 273
    src_size = len(data)
    o_src = 0
    dc = bytearray()
    lt = bytearray()
    mt = bytearray()
    prec_pos = 0
    # used to hold number of previous bytes coded as unlinked chunks (to enable longer RL with curr byte)
    o_dc = 0
    o_lt = 0
    o_mt = 0
    mask = 0
    mask_count = 32 # Number of bits left to fill in the mask
    while o_src < src_size:
        (ref, rlAtCurr) = checkRunlength(o_src, src_size, data, maxOffset, maxRunLength)
        log.debug("At {} ref {} rlAtCurr {}".format(o_src, ref, rlAtCurr))
        if (rlAtCurr <= 2) or (o_src == 0) or (ref<0):
            dc.append(data[o_src])
            mask = mask | (1 << (mask_count-1))
            o_dc  += 1
            o_src += 1
            # Should increment prec_pos ?
        else:
            if rlAtCurr == maxRunLength:
                #encodeLinkedChunk at o_src
                offset = o_src - ref - 1
                if (offset & 0xf000) != 0:
                    log.warn("Erroneous Offset: {} at {}".format(offset, o_src))
                # trim offset to minimize error propagation
                lt = lt + (offset & 0xfff).to_bytes(2, byteorder='big')
                o_lt += 2
                dc.append(0xff) #Encode max run length
                o_dc += 1
                o_src += rlAtCurr
                prec_pos = 0 #reset!
                # mask bit is 0 by default.
            else:
                if (o_src+1) < src_size:
                    (ref_next, rlAtNext) = checkRunlength(o_src+1, src_size, data, maxOffset, maxRunLength)
                else:
                    (ref_next, rlAtNext) = (-1, 0)
                if rlAtNext >= (rlAtCurr+prec_pos+2):
                    # encode unlinked chunk
                    dc.append(data[o_src])
                    mask = mask | (1 << (mask_count-1))
                    o_dc += 1
                    o_src += 1
                    prec_pos += 1
                else:
                    # encodeLinkedChunk at o_src
                    offset = o_src - ref - 1
                    if (offset & 0xf000) != 0:
                        log.warn("Erroneous Offset: {} at {}".format(offset, o_src))
                    if rlAtCurr < 18:
                        offset = ((rlAtCurr-2) << 12) | (offset & 0xfff)
                        lt = lt + (offset.to_bytes(2, byteorder='big'))
                        o_lt += 2
                    else:
                        lt = lt + (offset & 0xfff).to_bytes(2, byteorder='big')
                        o_lt += 2
                        dc.append(rlAtCurr-18)
                        o_dc += 1
                    o_src += rlAtCurr
                    prec_pos = 0
        # Update mask if necessary
        mask_count -= 1
        if mask_count == 0:
            mt = mt + mask.to_bytes(4, byteorder='big')
            o_mt += 4 # increment by 4 since the mask is 4 bytes long.
            mask = 0
            mask_count = 32
        log.debug("Encoded.")
    if mask_count != 32:
        mt = mt + mask.to_bytes(4, byteorder='big')
        o_mt += 4

    #Compose dst buffer by concatenating the prefix, size, lt offset (which is size of mt+16 bytes header),
    # dc offset (which is lt_offset + lt size), mt, lt and dc.
    dst = b'Yay0' + struct.pack(">I",src_size) + struct.pack(">I", (o_mt+16)) + struct.pack(">I", (o_mt+o_lt+16))
    log.debug("Mask Table {} bytes, Link Table {} bytes, DC {} bytes".format(o_mt, o_lt, o_dc))
    log.debug("Masks {} {} Links {} {} DCs {} {}".format(mt[0:4], mt[4:8], lt[0:2], lt[2:4], dc[0], dc[1]))
    log.info("Created Header: {}".format(dst))
    dst = dst + mt + lt + dc
    return dst

def main():
    logging.basicConfig(level=logging.WARN)
    infilename = "game_over.256x32.ci8y"
    outfilename = "game_over.256x32.raw"
    with open(infilename, "rb") as in_file:
        data = in_file.read()

    log.debug("Header: {}",format(data[:4]))
    #Check for header
    if(b"Yay0" == data[:0x04]):
        log.info ("Yay!!! Found yay0")
        raw = yay0Dec(data)
        with open(outfilename, "wb") as out_file:
            out_file.write(raw)
        log.info ("Decoded.")
        # Round-trip through encoder
        src = yay0Dec(yay0Enc(raw))
        if src == raw:
            log.info ("Re-Encoded successfully!")
        else:
            log.error("Re-encoding error!")

if __name__ == '__main__':
    main()
