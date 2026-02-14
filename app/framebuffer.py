import mmap
import os
import struct
import numpy as np

from PIL import Image

class Framebuffer:
    def __init__(self, fb_path, width, height):
        self.fb_path = fb_path
        self.width = width
        self.height = height
        self.bpp = 2  # RGB565 = 2 bytes per pixel
        self.size = width * height * self.bpp

        self._buffer = np.zeros((self.height, self.width), dtype=np.uint16)
        self.fd = os.open(self.fb_path, os.O_RDWR)
        self.mem = mmap.mmap(self.fd, self.size, mmap.MAP_SHARED,
                              mmap.PROT_WRITE | mmap.PROT_READ)

    def close(self):
        self.mem.close()
        os.close(self.fd)

    def clear(self, color):
        arr = np.ndarray(
            shape=(self.height, self.width),
            dtype=np.uint16,
            buffer=self.mem
        )
        arr[:] = color

    def draw_rect(self, x, y, w, h, color):
        arr = np.ndarray(
            shape=(self.height, self.width),
            dtype=np.uint16,
            buffer=self.mem
        )
        arr[y:y+h, x:x+w] = color


    def draw_image(self, src_image_path):
        img = Image.open(src_image_path)
        img = img.convert("RGB")
        img = img.resize((self.width, self.height), Image.BILINEAR)

        arr = np.asarray(img)

        r = arr[:, :, 0].astype(np.uint16)
        g = arr[:, :, 1].astype(np.uint16)
        b = arr[:, :, 2].astype(np.uint16)

        rgb565 = self._buffer
        rgb565[:] = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

        self.mem[:] = rgb565.view(np.uint8)


    def draw_image_at(self, src_image_path, x0, y0, w, h, transparent_bg=(255, 255, 255)):
        """
        Draw an image at a specific location.
        
        Args:
            src_image_path: Path to the image file
            x0, y0: Top-left position
            w, h: Width and height to resize to
            transparent_bg: RGB tuple for transparent background color (default: white)
        """
        img = Image.open(src_image_path)
        img = img.resize((w, h), Image.BILINEAR)
        
        # Handle transparencies by compositing onto background
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create background with specified color
            bg = Image.new('RGB', img.size, transparent_bg)
            if img.mode == 'P':
                img = img.convert('RGBA')
            # Composite image onto background using alpha channel
            bg.paste(img, (0, 0), img if img.mode == 'RGBA' else None)
            img = bg
        else:
            img = img.convert('RGB')

        arr = np.asarray(img)

        r = arr[:, :, 0].astype(np.uint16)
        g = arr[:, :, 1].astype(np.uint16)
        b = arr[:, :, 2].astype(np.uint16)

        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        rgb565 = rgb565.astype('<u2')

        # Write to framebuffer at the specified location
        framebuffer_arr = np.ndarray(
            shape=(self.height, self.width),
            dtype=np.uint16,
            buffer=self.mem
        )
        framebuffer_arr[y0:y0+h, x0:x0+w] = rgb565

# RGB565 helpers
def rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
