import mmap
import os
import struct

from PIL import Image

class Framebuffer:
    def __init__(self, fb_path, width, height):
        self.fb_path = fb_path
        self.width = width
        self.height = height
        self.bpp = 2  # RGB565 = 2 bytes per pixel
        self.size = width * height * self.bpp

        self.fd = os.open(self.fb_path, os.O_RDWR)
        self.mem = mmap.mmap(self.fd, self.size, mmap.MAP_SHARED,
                              mmap.PROT_WRITE | mmap.PROT_READ)

    def close(self):
        self.mem.close()
        os.close(self.fd)

    def clear(self, color):
        pixel = struct.pack("<H", color)
        self.mem.seek(0)
        self.mem.write(pixel * (self.width * self.height))

    def draw_rect(self, x, y, w, h, color):
        pixel = struct.pack("<H", color)
        for row in range(y, y + h):
            offset = (row * self.width + x) * self.bpp
            self.mem.seek(offset)
            self.mem.write(pixel * w)

    def draw_image(self, src_image_path):
        img = Image.open(src_image_path)
        img = img.convert("RGB")
        img = img.resize((self.width, self.height), Image.BILINEAR)

        self.mem.seek(0)

        for y in range(self.height):
            for x in range(self.width):
                r, g, b = img.getpixel((x, y))
                pixel = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                self.mem.write(struct.pack("<H", pixel))

# RGB565 helpers
def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
