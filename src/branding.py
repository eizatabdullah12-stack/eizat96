"""Vector-style speech-bubble mark, rasterized without external dependencies."""
import base64
import struct
import zlib

CREATOR = 'Eizat'


def logo_png(size=128):
    # Draw at twice the requested resolution and average for smooth edges.
    scale = 2
    width = size * scale
    def inside(x, y):
        # Rounded indigo tile, two conversation bubbles, and a crisp E monogram.
        if not (5 <= x <= 123 and 5 <= y <= 123):
            return (0, 0, 0, 0)
        dx = max(24-x, 0, x-104)
        dy = max(24-y, 0, y-104)
        if dx*dx+dy*dy > 19*19:
            return (0, 0, 0, 0)
        color = (int(23+x/12), int(39+y/10), int(88+x/4), 255)
        if (50 <= x <= 108 and 51 <= y <= 94) or (90 <= x <= 104 and 94 <= y <= 103 and x+y <= 198):
            color = (48, 213, 197, 255)
        if (23 <= x <= 86 and 28 <= y <= 78) or (27 <= x <= 42 and 78 <= y <= 91 and x+y <= 119):
            color = (246, 249, 255, 255)
        if (37 <= x <= 46 and 40 <= y <= 66) or (37 <= x <= 71 and 40 <= y <= 47) or (37 <= x <= 65 and 50 <= y <= 56) or (37 <= x <= 71 and 59 <= y <= 66):
            color = (34, 55, 111, 255)
        if 91 <= x <= 99 and 64 <= y <= 72:
            color = (255, 255, 255, 255)
        return color
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            samples = [inside((x*scale+sx+.5)*128/width, (y*scale+sy+.5)*128/width)
                       for sy in range(scale) for sx in range(scale)]
            raw.extend(sum(c[i] for c in samples)//len(samples) for i in range(4))
    def chunk(kind, payload):
        return struct.pack('>I', len(payload))+kind+payload+struct.pack('>I', zlib.crc32(kind+payload)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))+
            chunk(b'IDAT', zlib.compress(bytes(raw), 9))+chunk(b'IEND', b''))


def tk_logo(master, size=64):
    import tkinter as tk
    return tk.PhotoImage(master=master, data=base64.b64encode(logo_png(size)).decode('ascii'))


def write_icon(path):
    sizes = (16, 24, 32, 48, 64, 128, 256)
    images = [logo_png(size) for size in sizes]
    header = struct.pack('<HHH', 0, 1, len(images))
    offset = 6 + 16*len(images)
    entries = bytearray()
    for size, image in zip(sizes, images):
        entries.extend(struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32, len(image), offset))
        offset += len(image)
    path.write_bytes(header+entries+b''.join(images))
