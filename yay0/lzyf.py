# Compressor for LZYF

import yay0, logging, struct

maxOffsets = [16, 32, 1024]
maxLengths = {16: 513, 32: 4, 1024: 17}
log = logging.getLogger("lzyf")

def compress(src):
    src_size = len(src)
    dst_size = 0
    dst = bytearray()
    src_pos = 0
    rl = 0
    ctrl_byte = 0
    buf = bytearray()

    # Start a copy-run
    buf.append(src[src_pos])
    src_pos += 1
    rl += 1

    while src_pos < src_size:
        pos1, len1 = yay0.checkRunlength(src_pos, src_size, src, maxOffsets[0], maxLengths[maxOffsets[0]])
        pos2, len2 = yay0.checkRunlength(src_pos, src_size, src, maxOffsets[2], maxLengths[maxOffsets[2]])
        if len1 < 2 and len2 < 2:
            # No repeat pattern, add to or create copy run
            buf.append(src[src_pos])
            rl += 1
            src_pos +=1
            if rl == 0x1F:
                log.info("Copy run of {} ({}) from {} to {} at {} to {}".format(rl, len(buf), src_pos-rl, src_pos, dst_size, dst_size+rl+1))
                dst.append(rl)
                dst.extend(buf)
                dst_size += len(buf) + 1
                buf = bytearray()
                rl = 0
        else:
            # output existing copy run, if any
            if rl != 0:
                log.info("Copy run of {} ({}) from {} to {} at {} to {}".format(rl, len(buf), src_pos-rl, src_pos, dst_size, dst_size+rl+1))
                dst.append(rl)
                dst.extend(buf)
                dst_size += len(buf) + 1
                buf = bytearray()
                rl = 0
                # log
            if len1 > len2:
                # encode pos1, len1 using C
                v = src_pos-pos1-1
                ctrl_byte = 0x2000 | ((v & 0x0F) << 9) | ((len1-2) & 0x1FF)
                dst.extend(ctrl_byte.to_bytes(2, byteorder='big'))
                dst_size += 2
                src_pos += len1
            elif len2 <= maxLengths[maxOffsets[1]] and pos2 <= maxOffsets[1]:
                # encode pos2, len2 using A
                v = src_pos - pos2 - 1
                ctrl_byte = 0x80 | ((v<<2) & 0x7c) | ((len2-1) & 0x03)
                dst.append(ctrl_byte)
                dst_size += 1
                src_pos += len2
            else:
                # encode pos2, len2 using B
                v = src_pos - pos2 - 1
                ctrl_byte = 0x4000 | ((v<<4) & 0x3FF0) | ((len2-2) & 0x0F)
                dst.extend(ctrl_byte.to_bytes(2, byteorder='big'))
                dst_size += 2
                src_pos += len2
    if rl != 0:
        log.info("Copy run of {} ({}) from {} to {} at {} to {}".format(rl, len(buf), src_pos-rl, src_pos, dst_size, dst_size+rl+1))
        dst.append(rl)
        dst.extend(buf)
        dst_size += len(buf) + 1
        buf = bytearray()
        rl = 0
    log.info("Encoded {} into {} bytes.".format(src_size, dst_size))
    return (dst_size, src_size, dst)

def analyzeRuns(data):
    for i in range(len(data)):
        p, l = yay0.checkRunlength(i, len(data), data, 1024, 513)
        if l>1:
            log.info("{}: Found run of {} at {}".format(i, l, p))
            # i += l
