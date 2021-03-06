# Compressor for LZYF

import yay0, logging, struct

maxOffsets = [16, 32, 1024]
maxLengths = {16: 513, 32: 4, 1024: 17}
log = logging.getLogger("lzyf")

def create_lzyf(data):
    c = compress(data)
    out = bytearray(b'LZYF1000')
    out.extend((16+len(c)).to_bytes(4, byteorder='big'))
    out.extend(len(data).to_bytes(4, byteorder='big'))
    out.extend(c)
    return out

def crl(index, src, maxOffset, maxLength):
    """
    Returns starting position in source before index from where the max runlength is detected.
    """
    src_size = len(src)
    if index > src_size:
        return (-1, 0)
    if (index+maxLength) > src_size:
        maxLength = src_size - index
    startPos = max(0, index-maxOffset)
    endPos = index+maxLength-1
    l = maxLength
    # log.info("Looking from {} - {} ({}, {}) for upto {} bytes match at {}".format(startPos, endPos, index, maxOffset, maxLength, index))
    # log.info("String to be matched: {}".format(src[index:index+maxLength]))
    # log.info("Source to be searchd: {}".format(src[startPos:endPos]))
    while l>1:
        # log.info("At l {}".format(l))
        if src[index:index+l] in src[startPos:index+l-1]:
            p = src.rfind(src[index:index+l], startPos, index+l-1)
            # log.info("Match at {} in range {} {}".format(p, startPos, index+l-1))
            return (p,l)
        l -= 1
    return (-1, 0)

def ocrl(index, src, maxOffset, maxLength):
    """
    Returns starting position in source before index from where the max runlength is detected.
    """
    size = len(src)
    if index >= size:
        log.warn("Illegal index: {} or size: {} vs {}.".format(index, size, len(src)))
        return -1
    startPos =  max(0, index-maxOffset) # index - 1
    # stopPos = max(0, index-maxOffset)
    runs = {}
    while startPos < index :
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
        startPos += 1

    if not runs:
        log.debug("No suitable runs found.")
        return (-1, 0)
    else:
        # Return the index from where the longest run was found
        return (runs[max(runs.keys())], max(runs.keys()))

def rcrl(index, src, maxOffset, maxLength):
    """
    Returns starting position in source before index from where the max runlength is detected.
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

crl_func = rcrl
def checkRunlength(index, src, maxOffset, maxLength):
    return crl_func(index, src, maxOffset, maxLength)

def compress(src):
    src_size = len(src)
    dst_size = 0
    dst = bytearray()
    src_pos = 0
    rl = 0
    ctrl_byte = 0
    buf = bytearray()

    log.info("Start Encode")
    # Start a copy-run
    buf.append(src[src_pos])
    src_pos += 1
    rl += 1
    # print("Under Test!")
    while src_pos < src_size:
        pos0, len0 = checkRunlength(src_pos, src, maxOffsets[0], maxLengths[maxOffsets[0]])
        pos1, len1 = checkRunlength(src_pos, src, maxOffsets[1], maxLengths[maxOffsets[1]])
        pos2, len2 = checkRunlength(src_pos, src, maxOffsets[2], maxLengths[maxOffsets[2]])
        if src_pos+1 < src_size:
            pos3, len3 = checkRunlength(src_pos+1, src, maxOffsets[0], maxLengths[maxOffsets[0]])
            pos4, len4 = checkRunlength(src_pos+1, src, maxOffsets[1], maxLengths[maxOffsets[1]])
            pos5, len5 = checkRunlength(src_pos+1, src, maxOffsets[2], maxLengths[maxOffsets[2]])
            # if src_pos+2 < src_size:
            #     pos6, len6 = checkRunlength(src_pos+2, src, maxOffsets[0], maxLengths[maxOffsets[0]])
            #     pos7, len7 = checkRunlength(src_pos+2, src, maxOffsets[1], maxLengths[maxOffsets[1]])
            #     pos8, len8 = checkRunlength(src_pos+2, src, maxOffsets[2], maxLengths[maxOffsets[2]])
            # else:
            #     pos6, len6, pos7, len7, pos8, len8 = (-1, 0, -1, 0, -1, 0)
        else:
            pos3, len3, pos4, len4, pos5, len5, pos6, len6, pos7, len7, pos8, len8 = (-1, 0, -1, 0, -1, 0, -1, 0, -1, 0, -1, 0)
        # if (max(len0, len1+1, len2) >= 2) and ((max(len0, len1+1, len2)+2) >= max(len3, len4+1, len5, len6-2, len7-1, len8-2)):
        # if ((max(len0, len2) >= 2) and ((max(len0, len2)+2) >= max(len3, len5, len6-2, len8-2))):
        # if ((rl == 0) and (len1 > 0)) or ((max(len0, len2) >= 2) and ((max(len0, len2)+2) >= max(len3, len5, len6-2, len8-2))):
        if ((rl == 0) and (len1 > 0)) or ((max(len0, len2) >= 2) and ((max(len0, len2)+2) >= max(len3, len5))):
            # output existing copy run, if any
            if rl != 0:
                log.info("Copy: C={}, dec[{}:{}] is enc[{}:{}]. Check rl {} vs {}, enc {} vs {}".format(
                    bin(rl), src_pos-rl, src_pos, dst_size+1, dst_size+1+rl, rl, len(buf), dst_size+1+len(buf), len(dst)+1+len(buf)))
                dst.append(rl)
                dst.extend(buf)
                dst_size += len(buf) + 1
                buf = bytearray()
                rl = 0
            if len0 > max(2*len1, len2):
                # encode pos0, len0 using C
                v = src_pos-pos0-1
                ctrl_byte = 0x2000 | ((v & 0x0F) << 9) | ((len0-2) & 0x1FF)
                log.info("0x20: C={}, dec[{}:{}] is dec[{}:{}]. Check off {} len {}({}) bytes {} enc {} vs {}".format(
                    bin(ctrl_byte), src_pos, src_pos+len0, pos0, pos0+len0, hex(v), hex(len0), hex(len0-2), ctrl_byte.to_bytes(2, byteorder='big'), dst_size+2, len(dst)+2))
                dst.extend(ctrl_byte.to_bytes(2, byteorder='big'))
                dst_size += 2
                src_pos += len0
            elif len2 >= (2*len1):
                # encode pos2, len2 using B
                v = src_pos - pos2 - 1
                ctrl_byte = 0x4000 | ((v<<4) & 0x3FF0) | ((len2-2) & 0x0F)
                log.info("0x40: C={}, dec[{}:{}] is dec[{}:{}]. Check off {} len {}({}) bytes {} enc {} vs {}".format(
                    bin(ctrl_byte), src_pos, src_pos+len2, pos2, pos2+len2, hex(v), hex(len2), hex(len2-2), ctrl_byte.to_bytes(2, byteorder='big'), dst_size+2, len(dst)+2))
                dst.extend(ctrl_byte.to_bytes(2, byteorder='big'))
                dst_size += 2
                src_pos += len2
            else:
                # encode pos1, len1 using A
                v = src_pos - pos1 - 1
                ctrl_byte = 0x80 | ((v<<2) & 0x7c) | ((len1-1) & 0x03)
                log.info("0x80: C={}, dec[{}:{}] is dec[{}:{}]. Check off {} len {}({}) byte {} enc {} vs {}".format(
                    bin(ctrl_byte), src_pos, src_pos+len1, pos1, pos1+len1, hex(v), hex(len1), hex(len1-1), hex(ctrl_byte), dst_size+1, len(dst)+1))
                dst.append(ctrl_byte)
                dst_size += 1
                src_pos += len1
        else:
            # No or sub-optimal repeat pattern, add to or create copy run
            buf.append(src[src_pos])
            rl += 1
            src_pos +=1
            if rl == 0x1F:
                log.info("Copy: C={}, dec[{}:{}] is enc[{}:{}]. Check rl {} vs {}, enc {} vs {}".format(
                    bin(rl), src_pos-rl, src_pos, dst_size+1, dst_size+1+rl, rl, len(buf), dst_size+1+len(buf), len(dst)+1+len(buf)))
                dst.append(rl)
                dst.extend(buf)
                dst_size += len(buf) + 1
                buf = bytearray()
                rl = 0
    if rl != 0:
        log.info("Copy: C={}, dec[{}:{}] is enc[{}:{}]. Check rl {} vs {}, enc {} vs {}".format(
            bin(rl), src_pos-rl, src_pos, dst_size+1, dst_size+1+rl, rl, len(buf), dst_size+1+len(buf), len(dst)+1+len(buf)))
        dst.append(rl)
        dst.extend(buf)
        dst_size += len(buf) + 1
        buf = bytearray()
        rl = 0
    dst.append(0)
    dst_size += 1
    log.info("Zero byte at {}({}). src[0:{}]".format(dst_size, len(dst), src_pos))
    log.info("Encoded {} into {} bytes.".format(src_size, dst_size))
    return dst

def analyzeRuns(data):
    for i in range(len(data)):
        p, l = checkRunlength(i, data, 1024, 513)
        if l>1:
            log.info("{}: Found run of {} at {}".format(i, l, p))
            # i += l
