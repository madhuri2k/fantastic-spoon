import struct, random

data = bytearray(512)
d_sz = len(data) // 2

for i in range(len(data)):
  data[i] = int(256 * random.random())

wa = struct.unpack('>' + 'H'*d_sz, data)
print("Unpacked into {} elements".format(len(wa)))

dwa_be = struct.pack('>' + 'L'*d_sz, *map(lambda x: x*x, list(wa)))
dwa    = struct.pack(      'L'*d_sz, *map(lambda x: x*x, list(wa)))
dwa_le = struct.pack('<' + 'L'*d_sz, *map(lambda x: x*x, list(wa)))

print("Lengths be = {}, none = {}, le = {}", len(dwa_be), len(dwa), len(dwa_le))

