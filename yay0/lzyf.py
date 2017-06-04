# Compressor for LZYF

import logging, struct

maxOffsets = [16, 32, 1024]
maxLengths = {16: 513, 32: 4, 1024: 17}
log = logging.getLogger("lzyf")

def create_lzyf(data):
    c = compress(data)
    out = bytearray(b'LZYF1000')
    out.extend(len(c).to_bytes(4, byteorder='big'))
    out.extend(len(data).to_bytes(4, byteorder='big'))
    out.extend(c)
    return out

def checkRunlength(index, src, maxOffset, maxLength):
    """
    Returns starting position in source before index from where a max run is detected.
    """
    size = len(src)
    if index>=size:
        log.warn("Illegal index: {} or size: {} vs {}.".format(index, size, len(src)))
        return -1
    startPos = index - 1 # max(0, index-maxOffset)
    stopPos = max(0, index-maxOffset)
    runs = {}
    while(startPos >= stopPos):
        # log.debug("With: {} {} Runs: {}".format(startPos, index, runs))
        currRun = 0
        pos = startPos
        while src[pos] == src[index+currRun]:
            currRun += 1
            pos += 1
            if currRun == maxLength:
                log.debug("Found run of length {} == {}. Returning...".format(currRun, maxLength))
                return (startPos, maxLength) #found best possible run
            if (pos >= size) or ((index+currRun) >= size):
                break
        if (currRun > 0) and (currRun not in runs.keys()):
            runs[currRun] = startPos
            # log.debug("Result: {} Runs: {}".format(currRun, runs))
        startPos -= 1

    if not runs:
        log.debug("No suitable runs found.")
        return (-1, 0)
    else:
        # Return the index from where the longest run was found
        return (runs[max(runs.keys())], max(runs.keys()))

def compress(src):
    src_size = len(src)
    dst_size = 0
    dst = bytearray()
    src_pos = 0
    rl = 0
    ctrl_byte = 0
    buf = bytearray()

    # log.info("Start Encode")
    # Start a copy-run
    buf.append(src[src_pos])
    src_pos += 1
    rl += 1

    while src_pos < src_size:
        pos1, len1 = checkRunlength(src_pos, src, maxOffsets[0], maxLengths[maxOffsets[0]])
        pos2, len2 = checkRunlength(src_pos, src, maxOffsets[2], maxLengths[maxOffsets[2]])
        if src_pos+1 < src_size:
            pos3, len3 = checkRunlength(src_pos+1, src, maxOffsets[0], maxLengths[maxOffsets[0]])
            pos4, len4 = checkRunlength(src_pos+1, src, maxOffsets[2], maxLengths[maxOffsets[2]])
        else:
            pos3, len3, pos4, len4 = (-1, 0, -1, 0)
        # TODO: Try max(len3,len4) > (1+max(len1, len2))
        if (len1 < 2 and len2 < 2) or (max(len3, len4) > (1+max(len1, len2))):
            # No or sub-optimal repeat pattern, add to or create copy run
            buf.append(src[src_pos])
            rl += 1
            src_pos +=1
            if rl == 0x1F:
                # log.info("Copy: C={}, src[{}:{}] to dst[{}:{}]. Check rl {} vs {}, dst {} vs {}".format(
                #     bin(rl), src_pos-rl, src_pos, dst_size+1, dst_size+1+rl, rl, len(buf), dst_size+1+len(buf), len(dst)+1+len(buf)))
                dst.append(rl)
                dst.extend(buf)
                dst_size += len(buf) + 1
                buf = bytearray()
                rl = 0
        else:
            # output existing copy run, if any
            if rl != 0:
                # log.info("Copy: C={}, src[{}:{}] to dst[{}:{}]. Check rl {} vs {}, dst {} vs {}".format(
                #     bin(rl), src_pos-rl, src_pos, dst_size+1, dst_size+1+rl, rl, len(buf), dst_size+1+len(buf), len(dst)+1+len(buf)))
                dst.append(rl)
                dst.extend(buf)
                dst_size += len(buf) + 1
                buf = bytearray()
                rl = 0
            # TODO: Try len1 > (1+len2)
            if len1 > (1+len2):
                # encode pos1, len1 using C
                v = src_pos-pos1-1
                ctrl_byte = 0x2000 | ((v & 0x0F) << 9) | ((len1-2) & 0x1FF)
                # log.info("0x20: C={}, src[{}:{}] is src[{}:{}]. Check off {} len {}({}) bytes {} dst {} vs {}".format(
                #     bin(ctrl_byte), src_pos, src_pos+len1, pos1, pos1+len1, hex(v), hex(len1), hex(len1-2), ctrl_byte.to_bytes(2, byteorder='big'), dst_size+2, len(dst)+2))
                dst.extend(ctrl_byte.to_bytes(2, byteorder='big'))
                dst_size += 2
                src_pos += len1
            elif (len2 <= maxLengths[maxOffsets[1]]) and ((src_pos-pos2) <= maxOffsets[1]):
                # encode pos2, len2 using A
                v = src_pos - pos2 - 1
                ctrl_byte = 0x80 | ((v<<2) & 0x7c) | ((len2-1) & 0x03)
                # log.info("0x80: C={}, src[{}:{}] is src[{}:{}]. Check off {} len {}({}) byte {} dst {} vs {}".format(
                #     bin(ctrl_byte), src_pos, src_pos+len2, pos2, pos2+len2, hex(v), hex(len2), hex(len2-1), hex(ctrl_byte), dst_size+1, len(dst)+1))
                dst.append(ctrl_byte)
                dst_size += 1
                src_pos += len2
            else:
                # encode pos2, len2 using B
                v = src_pos - pos2 - 1
                ctrl_byte = 0x4000 | ((v<<4) & 0x3FF0) | ((len2-2) & 0x0F)
                # log.info("0x40: C={}, src[{}:{}] is src[{}:{}]. Check off {} len {}({}) bytes {} dst {} vs {}".format(
                #     bin(ctrl_byte), src_pos, src_pos+len2, pos2, pos2+len2, hex(v), hex(len2), hex(len2-2), ctrl_byte.to_bytes(2, byteorder='big'), dst_size+2, len(dst)+2))
                dst.extend(ctrl_byte.to_bytes(2, byteorder='big'))
                dst_size += 2
                src_pos += len2
    if rl != 0:
        # log.info("Copy: C={}, src[{}:{}] to dst[{}:{}]. Check rl {} vs {}, dst {} vs {}".format(
        #     bin(rl), src_pos-rl, src_pos, dst_size+1, dst_size+1+rl, rl, len(buf), dst_size+1+len(buf), len(dst)+1+len(buf)))
        dst.append(rl)
        dst.extend(buf)
        dst_size += len(buf) + 1
        buf = bytearray()
        rl = 0
    dst.append(0)
    dst_size += 1
    # log.info("Zero byte at {}({}). src[0:{}]".format(dst_size, len(dst), src_pos))
    # log.info("Encoded {} into {} bytes.".format(src_size, dst_size))
    return dst

def analyzeRuns(data):
    for i in range(len(data)):
        p, l = checkRunlength(i, data, 1024, 513)
        if l>1:
            log.info("{}: Found run of {} at {}".format(i, l, p))
            # i += l
